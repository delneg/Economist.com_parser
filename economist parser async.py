import proxy_checker
import asyncio
import aiohttp
from bs4 import BeautifulSoup
import requests as req
import goslate
import os
import time
import itertools
import random

# =====Config======
# defines if random proxies are used
use_proxy = True
# defines the proxy file (if needed,else if None - fetched) , the file must be in format ip:port separated by newlines (\n)
use_file = 'proxylist.txt'
# Defines the folder to save articles
folder_to_save = os.path.join(os.getcwd(), "economist_com_parser")
# Defines how much output program produces
verbose = True
# Translation code for goslate
transl_code= 'ru'
# TODO: verbosity levels
# ======Config end==




def last_page():
    soup = BeautifulSoup(
        req.get('http://www.economist.com/sections/economics', headers=proxy_checker.user_agent()).text, 'lxml')
    return int(soup.body.findAll('li', {"class": "pager-last even last"})[0].a['href'][-1])


def links_from_html(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = []
    for article in soup.body.findAll('article', {"class": "section-teaser with-image"}):
        links.append("http://www.economist.com" + article['data-href-redirect'])
    return links


@asyncio.coroutine
def get(*args, **kwargs):
    response = yield from aiohttp.request('GET', *args, **kwargs)
    return (yield from response.text())


# TODO: make proxy parsing async
def post(*args, **kwargs):
    response = yield from aiohttp.request('POST', *args, **kwargs)
    return (yield from response.text())


def first_magnet(page):
    soup = BeautifulSoup(page, 'lxml')
    a = soup.find('a', rel='colorbox')
    try:
        link = a['href']
    except:
        link = ''
    return link


def parse_article(name, article):
    if verbose:
        print("Parsing article " + name + "\n")
    start = time.time()
    soup = BeautifulSoup(article, 'lxml')
    text = soup.body.findAll('div', {"class": "main-content"})[0].text
    replaced = text.replace('\n', '').replace('\t', '')
    length = replaced.__len__()
    gs = goslate.Goslate()
    try:
        translated = gs.translate(replaced, transl_code)
    except:
        translated = ''
    data = [replaced, length, replaced[:1000], translated, name]
    end = time.time()
    if verbose:
        print('\nFinished parsing article in ' + str(end - start) + ' seconds\n')
    return save_article_to_file(data, folder_to_save)


def save_article_to_file(data, folder):
    text, length, thousand, translated, name = data
    filename = str(length) + '|' + name + '.txt'
    try:
        if not os.path.exists(folder):
            os.makedirs(folder)
        f = open(os.path.join(folder, filename), 'w')
        f.write("Length:" + str(
            length) + "\nTitle:\n" + name + "\nText:\n" + text + "\nFirst thousand\n" + thousand + "\nTranslation:\n" + translated)
        if verbose:
            print('Wrote ' + name + ' to file\n')
        return True
    except Exception as e:
        print("Didn't write file with name " + name + " due to exception \n" + str(e))
        return False


@asyncio.coroutine
def parse_article_list(url, proxies):
    name = url[url.rfind('/') + 1:]
    sem = asyncio.Semaphore(5)
    if verbose:
        print('Parsing url \n\t' + url)
    if proxies:
        print('With proxies')
        for p in proxies:
            try:
                with (yield from sem):
                    conn = aiohttp.ProxyConnector(proxy="http://" + p)
                    response = yield from asyncio.wait_for(
                        aiohttp.get(url, headers=proxy_checker.user_agent(), connector=conn), timeout=2)
                    status = response.status
                    html = yield from response.text()
                    if status == 200:
                        page = html
                        if verbose:
                            print('Got page ' + url + ' with proxy ' + p)
                        return parse_article(name, page), name
            except Exception as e:
                if verbose:
                    print("Failed to download ", url, 'with proxy ', p, " exception ", str(e))
                pass
    else:
        if verbose:
            print('Without proxies')
        with (yield from sem):
            page = yield from get(url, headers=proxy_checker.user_agent(), compress=True)
            if verbose:
                print('Got page ' + url + ' without proxies')
            return parse_article(name, page), name


@asyncio.coroutine
def do_query(query, proxies=None):
    sem = asyncio.Semaphore(5)
    url = 'http://www.economist.com/sections/economics?page=' + query
    if verbose:
        print('Doing query on \n\t' + url)
    if proxies:
        print('With proxies')
        for p in proxies:
            try:
                with (yield from sem):

                    conn = aiohttp.ProxyConnector(proxy="http://" + p)
                    response = yield from asyncio.wait_for(
                        aiohttp.get(url, headers=proxy_checker.user_agent(), connector=conn), timeout=2)
                    status = response.status
                    html = yield from response.text()
                    if status == 200:
                        page = html
                        if verbose:
                            print('Got page ' + query + ' with proxy ' + p)
                        return links_from_html(page)
            except Exception as e:
                if verbose:
                    print("Failed to download ", url, 'with proxy ', p, " exception ", str(e))
                pass
    else:
        if verbose:
            print('Without proxies')
        with (yield from sem):
            page = yield from get(url, headers=proxy_checker.user_agent(), compress=True)
            if verbose:
                print('Got page ' + query + ' without proxies')
            return links_from_html(page)


if use_proxy:
    if use_file:
        proxies = open(use_file).read().split('\n')
        proxies = list(filter(len, proxies))
        if verbose:
            print('Got ' + str(len(proxies)) + " proxies")
    else:
        proxies = proxy_checker.gatherproxy_req()
    random.shuffle(proxies)

loop = asyncio.get_event_loop()

if use_proxy:
    tasks = [do_query(str(i + 1), proxies) for i in range(last_page())]
else:
    tasks = [do_query(str(i + 1)) for i in range(last_page())]

gather_article_links = list(itertools.chain.from_iterable(
    loop.run_until_complete(asyncio.gather(*tasks))))  # gather tasks,run them until they complete, chain the lists

if use_proxy:
    art_tasks = [parse_article_list(link, proxies) for link in gather_article_links]
else:
    art_tasks = [parse_article_list(link) for link in gather_article_links]

articles = loop.run_until_complete(asyncio.gather(*art_tasks))

for result, name in articles:
    if result:
        print('Saved \n\t' + name + " at " + folder_to_save)
    else:
        print("Failed to save \n\t" + name)

loop.close()

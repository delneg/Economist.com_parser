import requests
import re
import random
def user_agent():
    headers = ['Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.56 (KHTML, like Gecko) Version/9.0 Safari/601.1.56',
               'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_1) AppleWebKit/601.2.7 (KHTML, like Gecko) Version/9.0.1 Safari/601.2.7',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
               'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0',
               'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:41.0) Gecko/20100101 Firefox/41.0',
               'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:41.0) Gecko/20100101 Firefox/41.0',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
               'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36',
               'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.80 Safari/537.36',
               'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.101 Safari/537.36',
               ]
    return {'User-Agent':headers[random.randrange(0,len(headers))]}

def gatherproxy_req():
    print('Gathering proxies...')
    url = 'http://gatherproxy.com/proxylist/anonymity/?t=Elite'
    lines = []
    for pagenum in range(1, 10):
        print('Parsing page '+str(pagenum))
        try:
            data = 'Type=elite&PageIdx={}&Uptime=0'.format(str(pagenum))
            headers = user_agent()
            headers['Content-Type'] = 'application/x-www-form-urlencoded'
            r = requests.post(url, headers=headers, data=data)
            lines += r.text.splitlines()
        except Exception as e:
            print(str(e))
            print('[!] Failed: %s' % url)
            gatherproxy_list = []
            return gatherproxy_list
    gatherproxy_list = parse_gp(lines)
    print('Got '+str(len(gatherproxy_list))+' proxies')
    return gatherproxy_list
def parse_gp(lines):
    ''' Parse the raw scraped data '''
    gatherproxy_list = []
    ip = ''
    get_port = False
    for l in lines:
        # Check if an IP was found on the line prior
        if get_port == True:
            get_port = False
            # GP obsfuscates the port with hex
            hex_port = l.split("'")[1]
            port = str(int(hex_port, 16))
            ip_port = '{}:{}'.format(ip, port)
            ip = ''
            gatherproxy_list.append(ip_port)
        # Search for the IP
        ip_re = re.search(r'[0-9]+(?:\.[0-9]+){3}', l)
        if ip_re:
            ip = ip_re.group()
            get_port = True
            # int('hexstring', 16) converts to decimal. GP uses this for obfuscation
            # proxy = '%s:%s' % (l["PROXY_IP"], str(int(l["PROXY_PORT"], 16)))
            # gatherproxy_list.append(proxy)
            # ctry = l["PROXY_COUNTRY"]

    return gatherproxy_list
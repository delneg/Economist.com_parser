# Economist.com_parser
This is an example of an asynchronous parser,created to show the possibilities of Python 3.5, asyncio and aiohttp.
The goal of parsing economist.com is to help students like myself to choose articles easily, give free access to them in a convenient way.


It uses BeautifulSoup for scraping and fetches proxies from http://gatherproxy.com, if not provided.


It also has popular *User Agents* list, from which headers for get requests are randomly selected.
#Config
Simply edit the config at the start of economist parser async.py file, and use it.
#Requirements:
 `pip3.5 install requests`
 
 `pip3.5 install aiohttp`
 
 `pip3.5 install goslate`
 
 `pip3.5 install beautifulsoup4`

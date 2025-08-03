# crawler.py
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from ..parser import parse_page

HEADERS = {"User-Agent": "Mozilla/5.0"}

def fetch_url(url):
    try:
        res = requests.get(url, timeout=6, headers=HEADERS)
        res.raise_for_status()
        return url, res.text
    except:
        return url, None

def crawl_pages(urls, max_workers=5):
    results = {}
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        for url, html in executor.map(fetch_url, urls):
            if html:
                results[url] = parse_page(url, html)
    return results
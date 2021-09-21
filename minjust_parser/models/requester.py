import requests
from bs4 import BeautifulSoup as bs

from utils.url import Url


class RequestDriver(object):
    def __init__(self):
        self.last_url: Url = None
        self.headers = {'User-Agent': (
            "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0"
        )}
        self.proxies = {}
        self.page_source: bs = None

    def set_proxy(self, proxy:str):
        if not proxy:
            self.proxies = {}
        elif proxy.startswith('https:') or proxy.startswith('http:'):
            self.proxies['https'] = (
                f"http://{proxy.lstrip('https://').lstrip('http://')}"
            )
        else:
            raise ValueError('invalid proxy')

    @property
    def safe_page_source(self):
        if self.page_source is None:
            self.get()
        return self.page_source

    def get(self, url: Url):
        response = requests.get(
            url, proxies=self.proxies, headers=self.headers
        )
        response.raise_for_status()
        self.page_source = bs(response.content, 'html.parser')
        return self.page_source

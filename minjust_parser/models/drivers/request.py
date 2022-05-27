import requests
from bs4 import BeautifulSoup as bs

from utils.url import Url

from . import Driver


class RequestDriver(Driver):
    def __init__(self):
        self.url: Url = None
        self.headers = {'User-Agent': (
            "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0"
        )}
        self.proxy = {}
        self.content: bs = None

    def set_proxy(self, proxy: str):
        if not proxy:
            self.proxy = {}
        elif proxy.startswith('https:') or proxy.startswith('http:'):
            self.proxy['https'] = (
                f"http://{proxy.partition('//')[2]}"
            )
        else:
            raise ValueError('invalid proxy')

    def get(self, url: Url):
        response = requests.get(
            url.url, proxies=self.proxy, headers=self.headers
        )
        response.raise_for_status()
        self.url = url
        self.content = bs(response.content, 'html.parser')
        return self.content

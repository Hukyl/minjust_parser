from abc import ABC, abstractproperty

import requests
from bs4 import BeautifulSoup as bs

from utils.url import Url
from settings import *
from .locator import *


class BaseRequestsPage(ABC):
    URL_TEMPLATE = None
    LOCATORS = None

    @abstractproperty
    def URL(self):
        pass

    def __init__(self):
        self.headers = {'User-Agent': (
            "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0"
        )}
        self.proxies = {}
        self.soup = None

    def __getattr__(self, attr):
        if hasattr(self.LOCATORS, attr.upper()):
            selector, is_multiple = getattr(self.LOCATORS, attr.upper())
            return getattr(
                self.safe_soup, 'select' if is_multiple else 'select_one'
            )(selector)
        else:
            super().__getattr__(attr)

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
    def safe_soup(self):
        if self._soup is None:
            self.get()
        return self._soup

    def get(self):
        response = requests.get(
            self.URL.url, proxies=self.proxies, headers=self.headers
        )
        response.raise_for_status()
        self._soup = bs(response.content, 'html.parser')
        return self._soup


class CatalogRequestsPage(BaseRequestsPage):
    URL_TEMPLATE = Url('https://youcontrol.com.ua/catalog/kved/79/11/{}')
    LOCATORS = CatalogRequestsPageLocators

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_number = 1

    @property
    def URL(self):
        return self.URL_TEMPLATE.format(self.page_number)

    def get_table_pages(self):
        start_url = self.URL.parent.parent.parent.parent.parent
        for link in self.catalog_table_elements[::2]:
            url = start_url + link.get('href')
            _, id_ = url.rsplit()
            agent_type = self.get_link_agent_type(url)
            if agent_type is AgentType.Enterpreneur:
                yield EntepreneurRequestsPage(id_)
            elif agent_type is AgentType.Company:
                yield CompanyRequestsPage(id_)
            else:
                raise ValueError('unknown page for special agent type')

    @staticmethod
    def get_link_agent_type(url: Url):
        _, kind = url.parent.rsplit()
        if kind == 'fop_details':
            return AgentType.Enterpreneur
        elif kind == 'company_details':
            return AgentType.Company
        else:
            return AgentType.Special


class AgentRequestsPage(BaseRequestsPage, ABC):
    LOCATORS = AgentRequestsPageLocators
    URL_TEMPLATE = (
        CatalogRequestsPage.URL_TEMPLATE.parent.parent.parent.parent 
        / '{}' / '{}'
    )

    def __init__(self, id_:int):
        super().__init__()
        self.id = id_

    @property
    def URL(self):
        return self.URL_TEMPLATE.format(self.id)

    def get_short_name(self):
        return self.short_name_span.text.strip()

    def get_full_name(self):
        return self.full_name_span.text.strip()

    @property
    def is_active(self):
        return self.status_span is not None

    @property
    def has_phone_number(self):
        return self.phone_td is not None

    def get_phone_number(self):
        if self.has_phone_number:
            return self.phone_td.text.strip()
        return None    


class EntepreneurRequestsPage(AgentRequestsPage):
    URL_TEMPLATE = (
        AgentRequestsPage.URL_TEMPLATE.parent.parent / 'fop_details' / '{}'
    )
    LOCATORS = EntepreneurRequestsPageLocators


class CompanyRequestsPage(AgentRequestsPage):
    URL_TEMPLATE = (
        AgentRequestsPage.URL_TEMPLATE.parent.parent / 'company_details' / '{}'
    )
    LOCATORS = CompanyRequestsPageLocators

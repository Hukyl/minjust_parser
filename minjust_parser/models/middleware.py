from abc import ABC, abstractmethod

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from utils.url import Url



class Middleware(ABC):
    def __init__(self, fetcher, locators):
        self.fetcher = fetcher
        self.locators = locators

    def __getattr__(self, attr: str):
        return self.get_inner_attribute(attr)

    @abstractmethod
    def get_inner_attribute(self, attr: str):
        pass

    @abstractmethod
    def get(self, *args, **kwargs):
        """
        Get the contents of a web page (or refresh them in some inner variable)
        """
        pass

    def set_proxy(self, proxy: str):
        return self.fetcher.set_proxy(proxy)

    @property
    def proxy(self):
        return self.fetcher.proxy



class RequestMiddleware(Middleware):
    def get_inner_attribute(self, attr: str):
        if hasattr(self.locators, attr.upper()):
            selector, is_multiple = getattr(self.locators, attr.upper())
            return getattr(
                self.fetcher.content, 'select' if is_multiple else 'select_one'
            )(selector)
        else:
            return super(object, self).__getattr__(attr)

    def get(self, url: Url):
        return self.fetcher.get(url)


class WebMiddleware(Middleware):
    def get_inner_attribute(self, attr: str):
        if hasattr(self.locators, attr.upper()):
            locator = getattr(self.locators, attr.upper())
            webelement = self.get_webelement(locator)
            return webelement
        else:
            return super(object, self).__getattr__(attr)

    def click(self, *args, **kwargs):
        return self.fetcher.click(*args, **kwargs)

    def enter_input(self, *args, **kwargs):
        return self.fetcher.enter_input(*args, **kwargs)

    def get_webelement(self, locator: tuple[str, bool]):
        selector, is_multiple = locator
        func = (
            EC.presence_of_all_elements_located if is_multiple else 
            EC.presence_of_element_located
        )
        return WebDriverWait(self.fetcher, 3).until(
            func((By.CSS_SELECTOR, selector))
        )

    def get(self, url: Url):
        return self.fetcher.get(url)

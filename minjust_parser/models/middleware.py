from abc import ABC, abstractmethod

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

from utils.url import Url



class Middleware(ABC):
    def __init__(self, fetcher, url: Url, locators):
        self.fetcher = fetcher
        self.url = url
        self.locators = locators

    @abstractmethod
    def __getattr__(self, attr: str):
        pass



class RequestMiddleware(Middleware):
    def __getattr__(self, attr):
        if hasattr(self.locators, attr.upper()):
            selector, is_multiple = getattr(self.locators, attr.upper())
            return getattr(
                self.safe_soup, 'select' if is_multiple else 'select_one'
            )(selector)
        else:
            super().__getattr__(attr)


class WebMiddleware(Middleware):
    def __getattr__(self, attr):
        locator = getattr(self.locators, attr.upper())
        webelement = self.get_webelement(locator)
        return webelement

    def enter_input(self, webelement, value:str) -> True:
        webelement.click()
        webelement.send_keys(Keys.HOME)
        webelement.send_keys(Keys.SHIFT, Keys.END)
        webelement.send_keys(Keys.BACKSPACE)
        webelement.send_keys(value)
        return True

    def get_webelement(self, locator: tuple[str, bool]):
        selector, is_multiple = locator
        func = (
            EC.presence_of_all_elements_located if is_multiple else 
            EC.presence_of_element_located
        )
        return WebDriverWait(self.fetcher, 3).until(
            func((By.CSS_SELECTOR, selector))
        )

    def __getattr__(self, attr: str):
        ...
import os
import sys
from typing import Optional, Union

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup as bs, PageElement

import settings
from utils.url import Url
from . import Driver


class WebDriver(webdriver.Firefox, Driver):
    NO_PROXY_URL = 'localhost,127.0.0.1,dev_server:8080'

    def __init__(
            self, *args, 
            headless:Optional[bool]=settings.FirefoxData.HEADLESS, **kwargs
            ):
        """
        Create a Firefox webdriver

        :keyword arguments:
            headless:bool=True - to set Firefox to be headless
        :return:
            driver:selenium.webdriver.Firefox
        """
        kwargs.pop('options', None)
        kwargs.pop('executable_path', None)
        kwargs.pop('seleniumwire_options', None)
        options = Options()
        options.add_argument(
            "--disable-blink-features=AutomationControlled"
        )  # these options bypass CloudFare protection
        options.add_argument("--log-level=OFF")  # remove console output
        service_log_path = os.devnull if sys.platform == 'linux' else 'NUL'
        if headless:
            options.add_argument("--disable-extensions")
            options.add_argument("--headless")
            if sys.platform == 'linux':
                options.add_argument("--no-sandbox")
                options.add_argument('--disable-dev-shm-usage')
        seleniumwire_options = {'proxy': {'no_proxy': self.NO_PROXY_URL}}
        fp = webdriver.FirefoxProfile()
        fp.accept_untrusted_certs = True
        fp.DEFAULT_PREFERENCES["frozen"]["browser.link.open_newwindow"] = 3
        capabilities = DesiredCapabilities.FIREFOX.copy()
        capabilities['acceptInsecureCerts'] = True
        super().__init__(
            *args,
            capabilities=capabilities,
            firefox_profile=fp,
            executable_path=settings.FirefoxData.PATH, 
            options=options,
            service_log_path=service_log_path,
            seleniumwire_options=seleniumwire_options,
            **kwargs
        )

    @staticmethod
    def convert_to_css_selector(by, value: str):
        if by == By.ID:
            return '[id="%s"]' % value
        elif by == By.TAG_NAME:
            return value
        elif by == By.CLASS_NAME:
            return ".%s" % value
        elif by == By.NAME:
            return '[name="%s"]' % value
        else:
            return value

    def _get_element(
            self, element: PageElement) -> webdriver.Firefox._web_element_cls:
        return super().find_element('css selector', element.css_selector)

    def click(self, webelement: PageElement) -> True:
        self._get_element(webelement).click()
        return True

    def enter_input(self, webelement: PageElement, value: str) -> True:
        webelement = self._get_element(webelement)
        webelement.click()
        webelement.send_keys(Keys.HOME)
        webelement.send_keys(Keys.SHIFT, Keys.END)
        webelement.send_keys(Keys.BACKSPACE)
        webelement.send_keys(value)
        return True

    def find_element(self, by=By.ID, value=None):
        element = super().find_element(by, value)
        element = bs(
            element.get_attribute('outerHTML'), 'html.parser'
        ).select_one('*')
        element.css_selector = self.convert_to_css_selector(by, value)
        return element

    def find_elements(self, by=By.ID, value=None):
        elements = super().find_elements(by, value)
        css_selector = self.convert_to_css_selector(by, value)
        elements = [
            bs(
                element.get_attribute('outerHTML'), 'html.parser'
            ).select_one('*')
            for element in elements
        ]
        for element in elements:
            element.css_selector = css_selector
        return elements

    @property
    def content(self):
        return bs(self.page_source, 'html.parser')

    @property
    def url(self):
        return Url(self.current_url)

    def get(self, url:Union[Url, str]):
        if isinstance(url, Url):
            url = url.url
        return super().get(url)

    def set_proxy(self, proxy:str):
        if not proxy:
            self.proxy = {'no_proxy': self.NO_PROXY_URL}
        else:
            self.proxy = {
                'no_proxy': self.NO_PROXY_URL,
                'https': proxy
            }
        return True

    def __del__(self):
        try:
            self.quit()
        except Exception:
            pass

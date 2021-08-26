import os
import sys
from typing import Optional, Union

from seleniumwire import webdriver
from selenium.webdriver.firefox.options import Options

import settings
from utils.url import Url


class Driver(webdriver.Firefox):
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
        seleniumwire_options = {
            'proxy': {
                'https': 'https://arturkontopol_gmail_:88256da026@45.148.154.32:30001',
                'no_proxy': 'localhost,127.0.0.1,dev_server:8080'
            }
        }
        super().__init__(
            *args,
            executable_path=settings.FirefoxData.PATH, 
            options=options,
            service_log_path=service_log_path,
            seleniumwire_options=seleniumwire_options,
            **kwargs
        )

    @property
    def url(self):
        return Url(self.current_url)

    def get(self, url:Union[Url, str]):
        if isinstance(url, Url):
            url = url.url
        return super().get(url)

    def set_proxy(self, proxy:str):
        self.proxy['https'] = proxy
        return True

    def open_new_tab(self):
        self.execute_script("window.open('', '_blank');")
        self.switch_tab(1)
        return True

    def switch_tab(self, index:int):
        self.switch_to.window(self.window_handles[index])
        return True

    def __del__(self):
        try:
            self.quit()
        except Exception:
            pass

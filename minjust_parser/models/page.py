from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common import exceptions
from twocaptcha import TwoCaptcha

from utils.url import Url
from settings import *
from .locator import *



class BasePage(object):
    """
    Base class to initialize the base page that will be called from all
    pages
    """
    URL = object
    LOCATORS = object

    def __init__(self, driver):
        self.driver = driver

    def __getattr__(self, attr):
        locator = getattr(self.LOCATORS, attr.upper())
        webelement = self.get_webelement(locator)
        return webelement

    def enter_input(self, webelement, value:str) -> True:
        webelement.click()
        webelement.send_keys(Keys.HOME)
        webelement.send_keys(Keys.SHIFT, Keys.END)
        webelement.send_keys(Keys.BACKSPACE)
        webelement.send_keys(value)
        return True

    def get_webelement(self, locator: tuple[str, str, bool]):
        *locator, is_multiple = locator
        func = (
            EC.presence_of_all_elements_located if is_multiple else 
            EC.presence_of_element_located
        )
        return WebDriverWait(self.driver, 3).until(func(locator))


class RegistryPage(BasePage):
    URL = Url('https://usr.minjust.gov.ua/content/free-search')
    LOCATORS = RegistryPageLocators

    def enter_name(self, value:str):
        return self.enter_input(self.name_input, value)

    def click_search_button(self):
        self.search_button.click()
        return True

    def select_radiobutton(self, agent_type: AgentType):
        if agent_type is AgentType.Enterpreneur:
            self.enterpreneur_radiobutton.click()
        elif agent_type is AgentType.Company:
            self.company_radiobutton.click()
        elif agent_type is AgentType.Special:
            self.special_radiobutton.click()
        else:
            raise ValueError('unknown agent type')
        return True

    def solve_captcha(self):
        client = TwoCaptcha(JsonSettings.rucaptcha_api_key)
        sitekey = Url(self.captcha_iframe.get_attribute('src')).params['k']
        for _ in range(3):
            try:
                return client.recaptcha(
                    sitekey=sitekey,
                    url=str(self.URL)
                )['code']
            except Exception:
                pass
            else:
                break
        else:
            raise ValueError('failed to solve captcha')


class CatalogPage(BasePage):
    URL = Url('https://youcontrol.com.ua/catalog/kved/79/11/{}')
    LOCATORS = CatalogPageLocators

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.page_number = 1

    def set_page(self, page_count:int):
        self.page_number = page_count
        self.driver.get(self.URL.parent / str(page_count))
        return True

    def next_page(self):
        self.page_number += 1
        self.driver.get(self.URL.parent / str(self.page_number))
        return True

    def get_table_links(self):
        elements = self.driver.execute_script(
            'return [...document.querySelectorAll(arguments[0])]', 
            self.LOCATORS.CATALOG_TABLE_ELEMENTS[1]
        )
        return [
            Url(link.find_element(By.TAG_NAME, 'a').get_attribute('href'))
            for link in elements[::2]
        ]

    def get_link_agent_type(self, url: Url):
        _, kind = url.parent.rsplit()
        if kind == 'fop_details':
            return AgentType.Enterpreneur
        elif kind == 'company_details':
            return AgentType.Company
        else:
            return AgentType.Special


class AgentPage(BasePage):
    LOCATORS = AgentPageLocators

    def get_short_name(self):
        return self.short_name_span.text

    def get_full_name(self):
        return self.full_name_span.text

    @property
    def is_active(self):
        try:
            self.status_span
        except exceptions.TimeoutException:
            return False
        else:
            return True

    @property
    def has_phone_number(self):
        try:
            self.phone_td
        except exceptions.TimeoutException:
            return False
        else:
            return True

    def get_phone_number(self):
        if self.has_phone_number:
            return self.phone_td.text
        return None    


class EntepreneurPage(AgentPage):
    URL = CatalogPage.URL.parent.parent.parent.parent / 'fop_details' / '{}'
    LOCATORS = EntepreneurPageLocators


class CompanyPage(AgentPage):
    URL = (
        CatalogPage.URL.parent.parent.parent.parent / 'company_details' / '{}'
    )
    LOCATORS = CompanyPageLocators

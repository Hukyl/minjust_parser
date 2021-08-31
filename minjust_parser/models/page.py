from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
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

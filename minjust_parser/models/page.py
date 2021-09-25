from abc import ABC

from twocaptcha import TwoCaptcha

from utils.url import Url
from settings import *
from .locators import *
from .middleware import Middleware



class BasePage(ABC):
    URL_TEMPLATE = object
    LOCATORS = object

    @property
    def URL(self):
        return self.URL_TEMPLATE

    def __init__(self, middleware: Middleware):
        self.middleware = middleware

    def get(self):
        return self.middleware.get(self.URL)

    def __getattr__(self, attr):
        if hasattr(self.LOCATORS, attr.upper()):
            return getattr(self.middleware, attr)
        else:
            raise AttributeError(
                f"'{self.__class__.__name__}' object has no attribute '{attr}'"
            )


class CatalogPage(BasePage):
    URL_TEMPLATE = Url('https://youcontrol.com.ua/catalog/kved/79/11/{}')
    LOCATORS = CatalogPageLocators

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
                yield EntepreneurPage, id_
            elif agent_type is AgentType.Company:
                yield CompanyPage, id_
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


class AgentPage(BasePage, ABC):
    LOCATORS = AgentPageLocators
    URL_TEMPLATE = (
        CatalogPage.URL_TEMPLATE.parent.parent.parent.parent 
        / '{}' / '{}'
    )

    def __init__(self, middleware: Middleware, id_:int):
        super().__init__(middleware)
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


class EntepreneurPage(AgentPage):
    URL_TEMPLATE = (
        AgentPage.URL_TEMPLATE.parent.parent / 'fop_details' / '{}'
    )
    LOCATORS = EntepreneurPageLocators


class CompanyPage(AgentPage):
    URL_TEMPLATE = (
        AgentPage.URL_TEMPLATE.parent.parent / 'company_details' / '{}'
    )
    LOCATORS = CompanyPageLocators


class RegistryPage(BasePage):
    URL_TEMPLATE = Url('https://usr.minjust.gov.ua/content/free-search')
    LOCATORS = RegistryPageLocators

    def enter_name(self, value:str):
        return self.middleware.enter_input(self.name_input, value)

    def click_search_button(self):
        self.middleware.click(self.search_button)
        return True

    def select_radiobutton(self, agent_type: AgentType):
        if agent_type is AgentType.Enterpreneur:
            self.middleware.click(self.enterpreneur_radiobutton)
        elif agent_type is AgentType.Company:
            self.middleware.click(self.company_radiobutton)
        elif agent_type is AgentType.Special:
            self.middleware.click(self.special_radiobutton)
        else:
            raise ValueError('unknown agent type')
        return True

    def solve_captcha(self):
        client = TwoCaptcha(JsonSettings.rucaptcha_api_key)
        sitekey = Url(self.captcha_iframe.get('src')).params['k']
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

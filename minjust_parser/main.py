from time import sleep
from urllib.parse import quote

import requests

from models.excel_handler import ExcelHandler
from models.drivers.web import WebDriver
from models.drivers.request import RequestDriver
from models.page import (
    EntepreneurPage, CompanyPage, 
    CatalogPage, RegistryPage
)
from models.logger import Logger
from models.api import RegistryDetailApi, RegistrySearchApi
from models.middleware import RequestMiddleware, WebMiddleware
import settings
from utils import is_valid_phone, cycle


driver = WebDriver()
excel_handler = ExcelHandler()
logger = Logger()
proxies = cycle(settings.JsonSettings.PROXIES or [''])

catalog_page = CatalogPage(
    RequestMiddleware(RequestDriver(), CatalogPage.LOCATORS)
)
registry_page = RegistryPage(WebMiddleware(driver, RegistryPage.LOCATORS))


def update_soup_safe(page):
    for _ in range(len(settings.JsonSettings.PROXIES)):
        page.middleware.set_proxy(next(proxies))
        try:
            soup = page.get()
        except requests.exceptions.HTTPError:
            logger.error('403 Forbidden')
        except OSError:
            logger.error(
                f'502 status code: proxy {page.middleware.proxy["https"]}'
            )
        else:
            return soup
    else:
        logger.error('All proxies are banned, quitting...')
        quit(1)


def write_person(page):
    update_soup_safe(page)
    if not page.is_active:
        return
    full_name = page.get_full_name()
    short_name = page.get_short_name()
    if isinstance(page, EntepreneurPage):
        registry_page.get()
        registry_page.select_radiobutton(settings.AgentType.Enterpreneur)
        registry_page.enter_name(full_name)
        registry_page.click_search_button()
        sleep(5)
        try:
            solved_recaptcha_token = registry_page.solve_captcha()
        except ValueError:
            logger.error("Failed to solve captcha, skipping to next person...")
            return
        search_response = RegistrySearchApi.get(
            {'person': quote(full_name), 'c': solved_recaptcha_token}
        )
        try:
            person_rfid = RegistrySearchApi.get_rfid(search_response)
        except KeyError:
            logger.error(
                "couldn't parse person id, the captcha took too long"
            )
            return
        except IndexError:
            logger.error('no such record in the registry')
            return
        detail_response = RegistryDetailApi.get({'rfId': quote(person_rfid)})
        phone_numbers = RegistryDetailApi.get_phone_numbers(detail_response)
        phone_numbers = [x for x in phone_numbers if is_valid_phone(x)]
        if not phone_numbers:
            return
        data = (phone_numbers, full_name)
    elif isinstance(page, CompanyPage):
        if not page.has_phone_number:
            return
        phone_number = page.get_phone_number() 
        if not is_valid_phone(phone_number):
            return
        data = ([phone_number], short_name)
    else:
        logger.warning('Unknown agent type, skipping...')
        return
    excel_handler.insert_data(data)
    excel_handler.save()


for page_number in range(
        settings.JsonSettings.START_PAGE_NUMBER, 
        settings.JsonSettings.END_PAGE_NUMBER
    ):
    catalog_page.page_number = page_number
    breakpoint()
    update_soup_safe(catalog_page)
    for (agent_class, id_) in catalog_page.get_table_pages():
        page = agent_class(
            RequestMiddleware(RequestDriver(), agent_class.LOCATORS), id_
        )
        registry_page.middleware.set_proxy(next(proxies))
        sleep(settings.JsonSettings.PAGE_OPEN_WAIT_TIME)
        write_person(page)
    else:
        logger.info(f'Page {page_number} covered')
else:
    driver.quit()
    input('Press Enter to exit...')

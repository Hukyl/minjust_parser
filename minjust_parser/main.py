from time import sleep
from urllib.parse import quote
from urllib3.exceptions import MaxRetryError as HTTP502Error

import requests

from models.excel_handler import ExcelHandler
from models.driver import Driver
from models.page import RegistryPage
from models.requests_page import (
    EntepreneurRequestsPage, CompanyRequestsPage, 
    CatalogRequestsPage
)
from models.logger import Logger
from models.api import RegistryDetailApi, RegistrySearchApi
import settings
from utils import is_valid_phone, cycle


driver = Driver()
excel_handler = ExcelHandler()
logger = Logger()
proxies = cycle(settings.JsonSettings.PROXIES or [''])

catalog_page = CatalogRequestsPage()
registry_page = RegistryPage(driver)


def update_soup_safe(page):
    for _ in range(len(settings.JsonSettings.PROXIES)):
        page.set_proxy(next(proxies))
        try:
            soup = page.get()
        except requests.exceptions.HTTPError:
            logger.error('403 Forbidden')
        except HTTP502Error:
            logger.error('502 status code: ')
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
    if isinstance(page, EntepreneurRequestsPage):
        driver.get(registry_page.URL)
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
    elif isinstance(page, CompanyRequestsPage):
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
    update_soup_safe(catalog_page)
    for page in catalog_page.get_table_pages():
        driver.set_proxy(next(proxies))
        sleep(settings.JsonSettings.PAGE_OPEN_WAIT_TIME)
        write_person(page)
    else:
        logger.info(f'Page {page_number} covered')
else:
    driver.quit()
    input('Press Enter to exit...')

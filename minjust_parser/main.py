from time import sleep
from urllib.parse import quote

from models.excel_handler import ExcelHandler
from models.driver import Driver
from models.page import (
    EntepreneurPage, AgentPage, CompanyPage, RegistryPage, CatalogPage
)
from models.api import RegistryDetailApi, RegistrySearchApi
import settings
from utils import is_valid_phone, cycle


driver = Driver()
excel_handler = ExcelHandler()
proxies = cycle(settings.ParserSettings.PROXIES)

catalog_page = CatalogPage(driver)
registry_page = RegistryPage(driver)


def write_person():
    agent_type = catalog_page.get_link_agent_type(link)
    driver.get(link)
    page = AgentPage(driver)
    if not page.is_active:
        return
    full_name = page.get_full_name()
    short_name = page.get_short_name()
    if agent_type is settings.AgentType.Enterpreneur:
        page = EntepreneurPage(driver)
        driver.switch_tab(1)
        registry_page.select_radiobutton(agent_type)
        registry_page.enter_name(full_name)
        registry_page.click_search_button()
        sleep(5)
        try:
            solved_recaptcha_token = registry_page.solve_captcha()
        except ValueError:
            return
        search_response = RegistrySearchApi.get(
            {'person': quote(full_name), 'c': solved_recaptcha_token}
        )
        try:
            person_rfid = RegistrySearchApi.get_rfid(search_response)
        except KeyError:
            settings.LoggerSettings.LOGGER.error(
                "couldn't parse person id, the captcha took too long"
            )
            return
        detail_response = RegistryDetailApi.get({'rfId': quote(person_rfid)})
        phone_numbers = RegistryDetailApi.get_phone_numbers(detail_response)
        phone_numbers = [x for x in phone_numbers if is_valid_phone(x)]
        if not phone_numbers:
            return
    elif agent_type is settings.AgentType.Company:
        page = CompanyPage(driver)
        if not page.has_phone_number:
            return
        phone_number = page.get_phone_number() 
        if not is_valid_phone(phone_number):
            return
        phone_numbers = [phone_number]
    else:
        settings.LoggerSettings.LOGGER.warning(
            'Unknown agent type, skipping...'
        )
        return
    excel_handler.insert_data((phone_numbers, short_name))
    excel_handler.save()


driver.open_new_tab()
driver.switch_tab(0)

for page_number in range(
        settings.ParserSettings.START_PAGE_NUMBER, 
        settings.ParserSettings.END_PAGE_NUMBER
    ):
    catalog_page.set_page(page_number)
    for link in catalog_page.get_table_links():
        driver.set_proxy(next(proxies))
        driver.switch_tab(1)
        driver.get(registry_page.URL)
        driver.switch_tab(0)
        catalog_page.set_page(page_number)
        write_person()     
    else:
        print(f'Page {page_number} covered')

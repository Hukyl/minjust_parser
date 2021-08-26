from selenium.webdriver.common.by import By

# (Type, Identifier, Is multiple)


class RegistryPageLocators(object):
    CAPTCHA_IFRAME = (
        By.XPATH, '//*[@id="ngrecaptcha-0"]/div/div/iframe', False
    )
    ENTERPRENEUR_RADIOBUTTON = (
        By.XPATH, '//div[@role="radiogroup"]/div[1]/label/input', False
    )
    COMPANY_RADIOBUTTON = (
        By.XPATH, '//div[@role="radiogroup"]/div[2]/label/input', False
    )
    SPECIAL_RADIOBUTTON = (
        By.XPATH, '//div[@role="radiogroup"]/div[3]/label/input', False
    )
    NAME_INPUT = (By.CSS_SELECTOR, 'input[type=text]', False)
    SEARCH_BUTTON = (By.CSS_SELECTOR, 'button[type=submit]', False)



class CatalogPageLocators(object):
    CATALOG_TABLE_ELEMENTS = (
        By.CSS_SELECTOR, 
        'table#catalog-functiongroup-page > tbody > tr > td', 
        True
    )


class AgentPageLocators(object):
    FULL_NAME_SPAN = (
        By.XPATH, 
        '//*[@id="catalog-company-file"]/div[2]/div[1]/div[2]/span', 
        False
    )
    SHORT_NAME_SPAN = (
        By.XPATH, 
        '//*[@id="catalog-company-file"]/div[2]/div[2]/div[2]/span', 
        False
    )
    STATUS_SPAN = (By.CSS_SELECTOR, 'span.status-green-seo', False)
    PHONE_TD = (By.CSS_SELECTOR, 'td.phone', False)


class EntepreneurPageLocators(AgentPageLocators):
    pass


class CompanyPageLocators(AgentPageLocators):
    PHONE_TD = (By.CSS_SELECTOR, 'a.phone-catalog-style', False)

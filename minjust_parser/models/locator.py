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

# (CSS Selector, Is multiple)


class CatalogRequestsPageLocators(object):
    CATALOG_TABLE_ELEMENTS = (
        'table#catalog-functiongroup-page > tbody > tr > td > a', 
        True
    )


class AgentRequestsPageLocators(object):
    FULL_NAME_SPAN = (
        '#catalog-company-file > div:nth-of-type(2) > div:nth-of-type(1) '
        '> div:nth-of-type(2) > span', False
    )
    SHORT_NAME_SPAN = (
        '#catalog-company-file > div:nth-of-type(2) > div:nth-of-type(2)'
        ' > div:nth-of-type(2) > span', False
    )
    STATUS_SPAN = ('span.status-green-seo', False)
    PHONE_TD = ('td.phone', False)


class EntepreneurRequestsPageLocators(AgentRequestsPageLocators):
    pass


class CompanyRequestsPageLocators(AgentRequestsPageLocators):
    PHONE_TD = ('a.phone-catalog-style', False)

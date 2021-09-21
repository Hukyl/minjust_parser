# (CSS Selector, Is multiple)


class RegistryPageLocators(object):
    CAPTCHA_IFRAME = ('#ngrecaptcha-0 > div > div > iframe', False)
    ENTERPRENEUR_RADIOBUTTON = ( 
        'div[role=radiogroup] > div:nth-of-type(1) > label > input', False
    )
    COMPANY_RADIOBUTTON = (
        'div[role=radiogroup] > div:nth-of-type(2) > label > input', False
    )
    SPECIAL_RADIOBUTTON = (
        'div[role=radiogroup] > div:nth-of-type(3) > label > input', False
    )
    NAME_INPUT = ('input[type=text]', False)
    SEARCH_BUTTON = ('button[type=submit]', False)


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

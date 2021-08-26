from enum import Enum

from twocaptcha import TwoCaptcha

from utils.url import Url
from utils.logger import Logger, ERROR, INFO, DEBUG, WARNING


class AgentType(Enum):
    Enterpreneur = 1
    Company = 2
    Special = 3


class LoggerSettings(object):
    LOG_LEVEL = WARNING
    LOGGER = Logger(LOG_LEVEL)


class ExcelSettings(object):
    FILENAME = 'output.xlsx'


class ParserSettings(object):
    RUCAPTCHA_API_KEY = 'ad21a04ad13efe8cbbdf212789ce59b0'
    RUCAPTCHA_CLIENT = TwoCaptcha(RUCAPTCHA_API_KEY)
    API_SEARCH_URL = Url(
        'https://usr.minjust.gov.ua/USRWebAPI/api/public/'
        'search?person={person}&c={c}'
    )
    API_DETAIL_URL = Url(
        'https://usr.minjust.gov.ua/USRWebAPI/api/public/detail?rfId={rfId}'
    )
    START_PAGE_NUMBER = 277  # inclusively
    END_PAGE_NUMBER = 278  # exclusively
    CATALOG_URL = Url('https://youcontrol.com.ua/catalog/kved/79/11/{}')
    REGISTRY_URL = Url('https://usr.minjust.gov.ua/content/free-search')
    PROXIES = [
        'https://arturkontopol_gmail_:88256da026@45.148.155.123:30001',
        'https://arturkontopol_gmail_:88256da026@45.148.154.32:30001',
        'https://arturkontopol_gmail_:88256da026@45.148.154.105:30001'
    ]


class FirefoxData(object):
    HEADLESS = False
    PATH = R'E:\Python\freelance\minjust_parser\geckodriver.exe'

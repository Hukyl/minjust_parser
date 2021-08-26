from enum import Enum
import json

from utils import DictAttributeMetaClass


class JsonSettings(metaclass=DictAttributeMetaClass):
    JSON = json.load(open('config.json'))


class AgentType(Enum):
    Enterpreneur = 1
    Company = 2
    Special = 3


class LoggerSettings(object):
    LOG_LEVEL = 'warning'


class ExcelSettings(object):
    FILENAME = 'output.xlsx'


class FirefoxData(object):
    HEADLESS = False
    PATH = JsonSettings.GECKODRIVER_PATH

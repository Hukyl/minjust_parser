import requests

from utils.url import Url


class BaseApi(object):
    URL = object
    AGENT = "Mozilla/5.0 (Windows NT 6.3; rv:36.0) Gecko/20100101 Firefox/36.0"

    @classmethod
    def get(cls, params: dict):
        return requests.get(
            cls.URL.format(**params).url,
            headers={'User-Agent': cls.AGENT}
        ).json()

    @classmethod
    def post(cls, data:dict):
        return requests.post(
            cls.URL.url, data=data,
            headers={'User-Agent': cls.AGENT}
        ).json()



class RegistrySearchApi(BaseApi):
    URL = Url(
        'https://usr.minjust.gov.ua/USRWebAPI/api/public/'
        'search?person={person}&c={c}'
    )

    @staticmethod
    def get_rfid(response: dict):
        return response['searchData'][0]['rfId']



class RegistryDetailApi(BaseApi):
    URL = Url(
        'https://usr.minjust.gov.ua/USRWebAPI/api/public/detail?rfId={rfId}'
    )

    @staticmethod
    def get_phone_numbers(response: dict):
        return [
            formatted.partition(':')[-1].strip()
            for formatted in response[-1]['value'].split(',')
        ]

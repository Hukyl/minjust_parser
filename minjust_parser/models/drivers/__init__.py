from abc import ABC, abstractmethod

from bs4 import PageElement

from utils.url import Url


class Driver(ABC):
    @staticmethod
    def generate_xpath(element: PageElement):
        components = []
        child = element if element.name else element.parent
        for parent in child.parents:
            siblings = parent.find_all(child.name, recursive=False)
            components.append(
                child.name if 1 == len(siblings) else '%s[%d]' % (
                    child.name,
                    next(i for i, s in enumerate(siblings, 1) if s is child)
                    )
                )
            child = parent
        components.reverse()
        return '/%s' % '/'.join(components)

    @abstractmethod
    def get(self, url: Url):
        pass

    @abstractmethod
    def set_proxy(self, proxy: str):
        pass

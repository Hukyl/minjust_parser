from collections.abc import Iterable


def is_valid_phone(phone:str):
    phone = phone.strip()
    for symbol in ['+', ' ', '-', '(', ')']:
        phone = phone.replace(symbol, '')
    return len(phone) >= 10 and '@' not in phone


def cycle(iterable: Iterable):
    while True:
        for x in iterable:
            yield x


class DictAttributeMetaClass(type):
    def __getattr__(cls, attr):
        if 'JSON' not in cls.__dict__:
            raise AttributeError
        return cls.JSON[attr.lower()]


class SingletonMetaClass(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMetaClass, cls).__call__(
                *args, **kwargs
            )
        return cls._instances[cls]

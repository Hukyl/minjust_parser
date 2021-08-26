from collections.abc import Iterable


def is_valid_phone(phone:str):
    phone = phone.strip()
    for symbol in ['+', ' ', '-', '(', ')']:
        phone = phone.replace(symbol, '')
    return len(phone) >= 10


def cycle(iterable: Iterable):
    while True:
        for x in iterable:
            yield x

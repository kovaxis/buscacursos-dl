import requests
from time import sleep
import logging


log = logging.getLogger("scraper")


def get_text(query: str) -> str:
    tries = 10
    while tries > 0:
        try:
            log.info(f'sending request to "{query}"...')
            text = requests.get(query).text
            return text
        except Exception:
            tries -= 1
            sleep(1)
    raise Exception(f'too many tries to URL "{query}"')

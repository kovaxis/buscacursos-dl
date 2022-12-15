import traceback
import requests
from time import sleep
import logging


log = logging.getLogger("scraper")


def get_text(cfg, query: str) -> str:
    cookies = cfg.get("cookies")

    tries = 10
    while tries > 0:
        try:
            log.info(f'sending request to "{query}"...')
            text = requests.get(query, headers={
                "Cookie": cookies,
            }).text
            return text
        except Exception:
            log.error(f"request to {query} failed:")
            log.error(traceback.format_exc())
            tries -= 1
            sleep(1)
    raise Exception(f'too many tries to URL "{query}"')

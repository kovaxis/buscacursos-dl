import os
import traceback
from typing import Callable, Dict
import requests
from time import sleep
import logging
import hashlib
import json
import binascii


log = logging.getLogger("scraper")


cache = {}
cachefile = None

def load_cache():
    if os.path.exists(".requestcache"):
        with open(".requestcache", 'r') as file:
            for line in file.readlines():
                c = json.loads(line)
                cache[c['key']] = c['resp']
    cachefile = open(".requestcache", 'a')


def add_to_cache(key: str, resp: str):
    cache[key] = resp
    if cachefile:
        json.dump({'key': key, 'resp': resp}, cachefile)
        cachefile.write('\n')
        cachefile.flush()


def get_text_raw(cfg, url: str, key: str, fetchtext: Callable[[], str]):
    if not cfg.get("disable-cache"):
        if key in cache:
            log.info("request to %s hit cache", url)
            return cache[key]

    tries = 10
    while tries > 0:
        try:
            resp = fetchtext()
            if not cfg.get("disable-cache"):
                add_to_cache(key, resp)
            return resp
        except Exception:
            log.error(f"request to {url} failed:")
            log.error(traceback.format_exc())
            tries -= 1
            sleep(1)
    raise Exception(f'too many tries to URL "{url}"')


def make_key(obj) -> str:
    return binascii.hexlify(hashlib.blake2b(json.dumps(obj).encode(encoding='UTF-8')).digest()).decode("ascii")


def get_text(cfg, query: str) -> str:
    cookies = cfg.get("cookies")
    key = make_key({
        'm': 'get',
        'url': query,
        'cks': cookies,
    })

    def fetch():
        return requests.get(query, headers={"Cookie": cookies}).text

    return get_text_raw(cfg, query, key, fetch)


def post_text(cfg, url: str, form_params: Dict[str, str]):
    cookies = cfg.get("cookies")
    key = make_key({
        'm': 'post',
        'url': url,
        'cks': cookies,
        'prm': form_params,
    })

    def post():
        return requests.post(url, data=form_params, headers={"Cookie": cookies}).text

    return get_text_raw(cfg, f"{url} & {form_params}", key, post)

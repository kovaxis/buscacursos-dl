#!/usr/bin/env python3
# Quick and dirty buscacursos/catalogo scraper based on the scraper for ramos-uc

import os
import traceback
from bc_scraper.actions.collect import CollectCourses
from bc_scraper.actions.collect_catalogo import CollectCatalogo
from bc_scraper.scraper.request import load_cache
import json
import logging
import sys



logging.basicConfig(level=logging.INFO)
log = logging.getLogger()

cookies = ""
if os.path.exists(".cred"):
    try:
        with open(".cred", 'r') as file:
            cookies = file.read()
        log.info(f"using cookies = '{cookies}'")
    except Exception:
        log.error("reading .cred for cookies failed:")
        log.error(traceback.format_exc())


args = sys.argv.copy()
args.pop(0)
opts = set()
for i in reversed(range(len(args))):
    if args[i].startswith("--"):
        opts.add(args[i][2:])
        args.pop(i)

if len(args) == 0:
    print(
        "usage: python3 main.py [options] [periods...]")
    print("  options:")
    print("    --skip-program   Do not fetch course program text.")
    print("    --skip-quota     Do not fetch course quota information.")
    print("    --disable-cache  Do not load or store cache from `.requestcache`.")
    print("    --test           Search for up to 10 courses and then stop.")
    print("  example: python3 main.py 2022-2 2022-1 > stdout.txt 2> stderr.txt")
    print("  if period is 'catalogo' then catalogo UC is scraped")
    sys.exit()
periods = args

settings = {
    "batch_size": 100,
    "cookies": cookies,
    "testmode": "test" in opts,
    "fetch-program": "skip-program" not in opts,
    "fetch-quota": "skip-quota" not in opts,
    "disable-cache": "disable-cache" in opts
}

if not settings.get("disable-cache"):
    load_cache()

if len(args) == 1 and args[0] == "catalogo":
    # Scrape catalogo UC
    log.info("scraping catalogo UC")
    courses = CollectCatalogo()
    courses.collect(settings)
    data = dict(sorted(courses.courses.items()))
    json.dump(data, sys.stdout)
else:
    # Scrape buscacursos
    log.info(f"scraping {len(periods)} buscacurso periods")
    data = {}
    for period in periods:
        log.info(f"scraping buscacurso period {period}")
        print(f"period[{period}]")
        courses = CollectCourses()
        courses.collect(period, settings)
        for course in courses.courses.values():
            course['sections'] = dict(
                sorted(course["sections"].items(), key=lambda x: int(x[0])))
        data[period] = dict(sorted(courses.courses.items()))
    data = dict(sorted(data.items(), reverse=True))
    json.dump(data, sys.stdout)

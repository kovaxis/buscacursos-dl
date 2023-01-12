from ..scraper.search_catalogo import catalogo_search
from ..scraper.programs import get_program
from ..scraper.requirements import get_requirements
from .schedule import process_schedule
from .errors import handle
import logging
from typing import Set, Dict, List, Union

log = logging.getLogger("scraper")


CATALOGO_LIMIT = 1000


class CollectCatalogo:
    processed: Set[str]
    courses: Dict[str, dict]

    def __init__(self):
        self.processed = set()
        self.courses = {}

    def process_courses(self, cfg: dict, courses: List[dict]):
        for c in courses:
            if c['initials'] in self.processed:
                continue
            self.processed.add(c['initials'])

            try:
                # Fetch auxiliary data
                program = ""
                if cfg.get("fetch-program"):
                    program = get_program(cfg, c["initials"])
                req, con, restr, equiv = get_requirements(cfg, c["initials"])

                print(
                    f"got course {c} with req {req}, con {con}, restr {restr} and equiv {equiv}")

                # Save course
                self.courses[c['initials']] = {
                    'name': c['name'],
                    'credits': c['credits'],
                    'req': req,
                    'conn': con,
                    'restr': restr,
                    'equiv': equiv,
                    'program': program,
                    'school': c['school'],
                    'relevance': c['relevance'],
                }
            except Exception as err:
                handle(c, err)

            # Commit to DB
            log.info(
                "Processed: %s %s",
                c["initials"],
                c["name"],
            )

    def collect(self, cfg: dict):
        testmode: bool = cfg.get('testmode', False)

        LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        NUMBERS = "0123456789"
        for l1 in LETTERS:
            comb = l1
            log.info("Searching %s", comb)
            courses = catalogo_search(cfg, comb)
            if testmode and len(courses) > 10:
                courses = courses[:10]
                pass
            self.process_courses(cfg, courses)
            if testmode:
                break
            if len(courses) < CATALOGO_LIMIT:
                continue

            for l2 in LETTERS:
                comb = l1 + l2
                log.info("Searching %s", comb)
                courses = catalogo_search(cfg, comb)
                self.process_courses(cfg, courses)
                if len(courses) < CATALOGO_LIMIT:
                    continue

                for l3 in LETTERS:
                    comb = l1 + l2 + l3
                    log.info("Searching %s", comb)
                    courses = catalogo_search(cfg, comb)
                    self.process_courses(cfg, courses)
                    if len(courses) < CATALOGO_LIMIT:
                        continue

                    for n1 in NUMBERS:
                        comb = l1 + l2 + l3 + n1
                        log.info("Searching %s", comb)
                        courses = catalogo_search(cfg, comb)
                        self.process_courses(cfg, courses)
                        if len(courses) < CATALOGO_LIMIT:
                            continue

                        for n2 in NUMBERS:
                            comb = l1 + l2 + l3 + n1 + n2
                            log.info("Searching %s", comb)
                            courses = catalogo_search(cfg, comb)
                            self.process_courses(cfg, courses)

        log.info("Found %s courses", len(self.courses))

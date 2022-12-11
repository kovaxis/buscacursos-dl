from ..scraper.search import bc_search
from ..scraper.programs import get_program
from ..scraper.requirements import get_requirements
from .schedule import process_schedule
from .errors import handle
import logging
from typing import Dict, List

log = logging.getLogger("scraper")


class CollectCourses:
    processed_initials: Dict[str, bool]
    processed_nrcs: Dict[str, bool]
    new_sections: int
    new_courses: int

    # Map code to course
    courses: Dict[str, dict]

    def __init__(self):
        # Global procesed courses and sections
        self.procesed_initials = {}
        self.procesed_nrcs = {}
        self.new_sections = 0
        self.new_courses = 0
        self.courses = {}
        self.sections = {}

    def process_courses(self, courses: List[Dict[str, str | bool | int]], period: str):
        """For a list of courses, process and gathers all related data and commits to DB."""
        for c in courses:
            # Skip recently procesed sections
            if c["nrc"] in self.procesed_nrcs:
                continue

            # Mark as procesed inmediatly to avoid repeating errors
            self.procesed_nrcs[c["nrc"]] = True

            try:
                # Save Course if needed
                if c["initials"] not in self.procesed_initials:
                    # Get Course related data
                    program = get_program(c["initials"])
                    req, con, restr = get_requirements(c["initials"])

                    # Save Course
                    # NOTE: Original code checks if the initial already exists in the db
                    # This means some duplicate courses might occur?
                    self.courses[c["initials"]] = {
                        "name": c["name"],
                        "credits": c["credits"],
                        "requirements": req,
                        "connector": con,
                        "restrictions": restr,
                        "program": program,
                        "school": c["school"],
                        "area": c["area"],
                        "category": c["category"],
                        "sections": {},
                    }
                    self.new_courses += 1

                    self.procesed_initials[c["initials"]] = True

                # Save Section
                self.courses[c["initials"]]["sections"][str(c["section"])] = {
                    "nrc": c["nrc"],
                    "teachers": c["teachers"],
                    "schedule": process_schedule(c["schedule"]),
                    "format": c["format"],
                    "campus": c["campus"],
                    "is_english": c["is_english"],
                    "is_removable": c["is_removable"],
                    "is_special": c["is_special"],
                    "total_quota": c["total_quota"],
                    # NOTE: Depends on the exact timing of the scrape
                    "available_quota": c["available_quota"],
                }
                self.new_sections += 1

                # Save schedules
                # TODO: process schedules
                # db_cursor.execute(sql.DELETE_FULL_SC, (section_id,))
                # db_cursor.execute(sql.DELETE_INFO_SC, (section_id,))
                # db_cursor.execute(insert_full_sc_query, (section_id,))
                # db_cursor.execute(insert_info_sc_query, (section_id,))

                # Commit to DB
                log.info(
                    "Processed: %s %s",
                    c["initials"] + "-" + str(c["section"]),
                    c["name"],
                )

            except Exception as err:
                handle(c, err)

    def collect(self, period: str, settings: dict):
        """Iterates a search throw all BC and process all courses and sections found."""

        testmode: bool = settings.get('testmode', False)

        LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        NUMBERS = "0123456789"
        for l1 in LETTERS:
            comb = l1
            log.info("Searching %s", comb)
            courses = bc_search(comb, period)
            if testmode and len(courses) > 10:
                courses = courses[:10]
                pass
            self.process_courses(courses, period)
            if testmode:
                break
            if len(courses) < 50:
                continue

            for l2 in LETTERS:
                comb = l1 + l2
                log.info("Searching %s", comb)
                courses = bc_search(comb, period)
                self.process_courses(courses, period)
                if len(courses) < 50:
                    continue

                for l3 in LETTERS:
                    comb = l1 + l2 + l3
                    log.info("Searching %s", comb)
                    courses = bc_search(comb, period)
                    self.process_courses(courses, period)
                    if len(courses) < 50:
                        continue

                    for n1 in NUMBERS:
                        comb = l1 + l2 + l3 + n1
                        log.info("Searching %s", comb)
                        courses = bc_search(comb, period)
                        self.process_courses(courses, period)
                        if len(courses) < 50:
                            continue

                        for n2 in NUMBERS:
                            comb = l1 + l2 + l3 + n1 + n2
                            log.info("Searching %s", comb)
                            courses = bc_search(comb, period)
                            self.process_courses(courses, period)

        log.info("New courses: %s", self.new_courses)
        log.info("New sections: %s", self.new_sections)
        log.info("Total courses: %s", len(self.procesed_initials))
        log.info("Total sections: %s", len(self.procesed_nrcs))
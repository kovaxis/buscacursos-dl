#!/usr/bin/env python3

import sys
import json
from typing import Dict, List


def process_schedule(text_sc: str) -> Dict[str, List[str]]:
    """For a given schedule text in BC format, returns the SQL queries for inserting
    the full schedule and schedule info. Those queries have to format ID.
    """
    # Full Schedule
    data = text_sc.split("\nROW: ")[1:]
    # data rows -> day-day:module,module <> type <> room <><>
    schedule: Dict[str, List[str]] = {}
    for row in data:
        row = row.split("<>")
        while len(row) > 0 and row[-1] == "":
            row.pop()
        horario = row[0].split(":")
        days = horario[0].split("-")
        modules = horario[1].split(",")
        for day in days:
            for mod in modules:
                if len(day) and len(mod):
                    schedule[day.lower() + mod] = row[1:]
    return schedule


with open("data.json", "r") as file:
    data = json.load(file)

for section in data["sections"].values():
    # Put section inside corresponding course
    course = data["subjects"][section["course_initials"]]
    if "sections" not in course:
        course["sections"] = {}
    sections = course["sections"]
    sections[str(section["section"])] = {
        "nrc": section["nrc"],
        "teachers": section["teachers"],
        "schedule": process_schedule(section["schedule"]),
        "format": section["format"],
        "campus": section["campus"],
        "is_english": section["is_english"],
        "is_removable": section["is_removable"],
        "is_special": section["is_special"],
        "total_quota": section["total_quota"],
        # NOTE: Depends on the exact timing of the scrape
        "available_quota": section["available_quota"],
    }

    # Change data format
    section["schedule"] = process_schedule(section["schedule"])
    del section["course_initials"]
    del section["period"]
    del section["section"]

courses = {}
for initials, course in data["subjects"].items():
    courses[initials] = {
        "name": course["name"],
        "credits": course["credits"],
        "requirements": course["req"],
        "connector": course["con"],
        "restrictions": course["restr"],
        "program": course["program"],
        "school": course["school"],
        "area": course["area"],
        "category": course["category"],
        "sections": course["sections"],
    }

json.dump({"2022-2": courses}, sys.stdout)

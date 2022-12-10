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

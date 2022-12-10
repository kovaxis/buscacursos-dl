from datetime import datetime
import json
import logging
import traceback

log = logging.getLogger("scraper")


def handle(context, err):
    log.error("%s", traceback.format_exc())
    log.error("Context: %s", json.dumps(context, indent=2))

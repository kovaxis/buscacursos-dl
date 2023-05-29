from html.parser import HTMLParser
from .request import get_text
import logging
from time import sleep


log = logging.getLogger("scraper")


class BannerParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.toggle = False
        self.col = 0
        self.quota = {}
        self.keys = []

    def process(self, text):
        self.toggle = False
        self.col = 0
        self.quota = {}
        self.keys = []
        self.feed(text)
        return self.quota

    def handle_starttag(self, tag, attrs):
        if not self.toggle and tag == "tr" and ("class", "resultadosRowImpar") in attrs:
            self.toggle = True
        if tag == "td" and self.toggle:
            self.col += 1

    def handle_endtag(self, tag):
        if tag == "tr":
            self.col = 0
            self.keys = []

    def handle_data(self, data):
        data = data.strip()
        if data == "&nbsp;":
            self.toggle = False
        if self.toggle and data:
            if self.col < 7:
                self.keys.append(data)
            elif self.col == 7:
                key = "/".join(self.keys)
                self.quota[key] = int(data)


def banner_quota(cfg, nrc: str, period: str):
    parser = BannerParser()
    url = f"https://buscacursos.uc.cl/informacionVacReserva.ajax.php?nrc={nrc}&termcode={period}"
    resp = get_text(cfg, url)

    # Check valid response
    if len(resp) < 1000:
        log.warn("Too many request prevention")
        sleep(5)
        resp = get_text(cfg, url)

    return parser.process(resp)

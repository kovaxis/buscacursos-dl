from html.parser import HTMLParser
from time import sleep
from .request import post_text
import logging
from typing import List, Dict, Tuple, Union, Optional

log = logging.getLogger("scraper")


class _CatalogoParser(HTMLParser):
    first: bool
    nested: int
    text: str
    cols: list[str]
    courses: List[Dict[str, Union[str, bool, int]]]

    def __init__(self):
        super().__init__()
        self.first = True
        self.nested = 0
        self.text = ""
        self.cols = []
        self.courses = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]):
        if tag in ("tr", "td"):
            if self.nested == 0:
                self.text = ""
                self.cols = []
            self.nested += 1

    def handle_endtag(self, tag: str):
        if tag in ("tr", "td"):
            if self.nested == 2:
                self.cols.append(self.text)
                self.text = ""
            elif self.nested == 1:
                if self.first:
                    self.first = False
                else:
                    self.process_course()
            self.nested -= 1

    def handle_data(self, data: str):
        if self.nested == 2:
            data = data.strip()
            self.text += data

    def process_course(self):
        course = {
            "school": self.cols[0],
            "initials": self.cols[1],
            "name": self.cols[2],
            "level": self.cols[3],
            "credits": int(self.cols[4]),
            "relevance": self.cols[5],
        }

        self.courses.append(course)


# Search
def catalogo_search(cfg, query: str):
    parser = _CatalogoParser()
    url = f"https://catalogo.uc.cl/index.php?Itemid=378"
    params = {
        "cod_unidad_academ": "",
        "sigla": query,
        "nom_curso": "",
        "nivel": "",
        "vigencia": "0",
        "Buscar": "Buscar",
        "option": "com_catalogo",
        "view": "cursoslist",
        "Itemid": "378",
    }
    resp = post_text(cfg, url, params)

    # Check valid response
    if len(resp) < 1000:
        log.warn("Too many request prevention")
        sleep(5)
        resp = post_text(cfg, url, params)

    parser.feed(resp)
    return parser.courses

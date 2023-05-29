#!/usr/bin/env python3

import json

with open("universal-noprogram.json", "r") as file:
    courses = json.load(file)

with open("siding-mock.json", "r") as file:
    siding = json.load(file)


def getlist(code):
    l = siding["getListaPredefinida"][f"{{\"CodLista\": \"{code}\"}}"]
    l = map(lambda c: c['Sigla'], l)
    l = filter(lambda c: c in courses and courses[c]['instances'], l)
    l = set(l)
    return l


lists = ["L1", "L10", "L11", "C8931"]
lists = dict(map(lambda code: (code, getlist(code)), lists))

# L1: OFG
# L10: Optativo Biologico
# L11: Exploratorio de Major
# C8931: Optativo de Fundamentos de Ingenieria

for l1_code, l1 in lists.items():
    for l2_code, l2 in lists.items():
        if l1_code >= l2_code:
            continue
        inter = l1.intersection(l2)
        l1_lo = set(
            filter(lambda c: courses[c]['credits'] < 10, set(l1).difference(l2)))
        l2_lo = set(
            filter(lambda c: courses[c]['credits'] < 10, set(l2).difference(l1)))
        if inter and l1_lo and l2_lo:
            print(f"conditions given in {l1_code} and {l2_code}")
            print(f"  {l1_code} and {l2_code} have {len(inter)} courses in common")
            if len(inter) < 50:
                print(f"    {inter}")
            print(f"  {len(l1_lo)} lo-credit courses exclusively in {l1_code}")
            if len(l1_lo) < 50:
                print(f"    {l1_lo}")
            print(f"  {len(l2_lo)} lo-credit courses exclusively in {l2_code}")
            if len(l2_lo) < 50:
                print(f"    {l2_lo}")

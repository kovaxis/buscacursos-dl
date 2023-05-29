#!/usr/bin/env python3

import sys
import json
import traceback
from reqparse import ReqParser, Conn, Or, And

with open("courses.json", "r") as file:
    data = json.load(file)


courses = data["2022-2"]
unique = set()
unique_lhs = {}

req_counts = {}

for sigla, c in courses.items():

    # if c['area'] != "":
    #    print(f"{sigla} area = \"{c['area']}\"")
    # if c['category'] != "":
    #    print(f"{sigla} category = \"{c['category']}\"")

    # restr = c['restr']
    # if restr not in unique:
    #    #print(f"{sigla} {restr}")
    #    unique.add(restr)
    #    if restr != "No tiene":
    #        try:
    #            restr_obj = BcParser(restr).parse()
    #            #print(f"  {restr_obj}")
    #            restr_obj.find_unique_lhs(unique_lhs)
    #        except:
    #            print(f"parsing restr \"{restr}\" for course {sigla} failed:")
    #            traceback.print_exc()

    try:
        deps = ReqParser.parse_deps(c['req'], c['conn'], c['restr'])
        c['deps'] = deps
        leaves = {}
        deps.find_unique_leaves(leaves)
        cnt = 0
        for code, inst in leaves.items():
            cnt += len(inst)
        req_counts.setdefault(cnt, {})[sigla] = deps
    except:
        print(
            f"parsing deps '{c['req']}', '{c['conn']}', '{c['restr']}' for course {sigla} failed:")
        traceback.print_exc()
req_counts = dict(sorted(req_counts.items()))

for lhs, rhss in unique_lhs.items():
    print(f"\"{lhs}\":")
    for rhs in rhss:
        print(f"  {rhs}")

diffs = {}

for cnt, cs in req_counts.items():
    print(f"{len(cs)} courses with {cnt} requirements")
    if cnt >= 0:
        for code, deps in cs.items():
            orig = deps.count_nodes()
            simplified = deps.simplify()
            new = simplified.count_nodes()
            diffs.setdefault(new-orig, set()).add(code)
            if code == "IIC2523":
                print(f"  {code}")
                print(f"    original:   {deps}")
                print(f"    simplified: {simplified}")

for diff, cs in sorted(diffs.items()):
    print(f"simplify delta = {diff}: {len(cs)} courses")
    if len(cs) < 100:
        print(cs)


def is_only_or(expr):
    if not isinstance(expr, Conn):
        return True
    if not isinstance(expr, Or):
        return False
    for x in expr.params:
        if not is_only_or(x):
            return False
    return True


for code, c in courses.items():
    if c['equiv'] == "No tiene":
        c['eqlist'] = []
    else:
        equiv = ReqParser.parse_requirement(c['equiv'])
        if not is_only_or(equiv):
            print(f"equiv for {code} = {equiv}")
        if isinstance(equiv, Conn):
            c['eqlist'] = equiv.params
        else:
            c['eqlist'] = [equiv]

for code, c in courses.items():
    for eq in c['eqlist']:
        if eq not in courses:
            # print(f"referenced course not found: {eq}")
            continue
        eqc = courses[eq]
        if code not in eqc['eqlist']:
            print(
                f"course {code} has equivalency {eq}, but {eq} does not have equivalency {code}")

empty_programs = set()
schools = {}
empty_school = set()
empty_area = set()
empty_category = set()
for code, c in courses.items():
    if c['program'] == "":
        empty_programs.add(code)
    schools.setdefault(c['school'], set()).add(code)
    if c['school'] == "":
        empty_school.add(code)
    if c['area'] == "":
        empty_area.add(code)
    if c['category'] == "":
        empty_category.add(code)
print(f"empty programs: {empty_programs}")
print(f"schools: {list(schools.keys())}")
print(f"empty school: {len(empty_school)}")
print(f"empty area: {len(empty_area)}")
print(f"empty category: {len(empty_category)}")

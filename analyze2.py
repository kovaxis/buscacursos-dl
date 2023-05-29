#!/usr/bin/env python3

import sys
import json
import traceback
from reqparse import Expr, Req, ReqParser, Conn, Or, And

with open("universal-noprogram.json", "r") as file:
    courses = json.load(file)


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
        deps = deps.simplify()

        def check_deps(expr: Expr):
            if isinstance(expr, Req):
                if expr.code not in courses:
                    print(
                        f"course {sigla} has dependency on {expr.code}, which does not exist")
            elif isinstance(expr, Conn):
                for sub in expr.params:
                    check_deps(sub)
        check_deps(deps)

        c['deps'] = deps
    except:
        print(
            f"parsing deps '{c['req']}', '{c['conn']}', '{c['restr']}' for course {sigla} failed:")
        traceback.print_exc()


for sigla, c in courses.items():
    try:
        eqlist = []
        if c['equiv'] != "No tiene":
            equivs = ReqParser.parse_requirement(c['equiv'])
            if isinstance(equivs, Req):
                assert not equivs.co
                eqlist.append(equivs.code)
            elif isinstance(equivs, Or):
                for req in equivs.params:
                    assert isinstance(req, Req) and not req.co
                    eqlist.append(req.code)
            else:
                raise Exception(
                    "top-level equivalence is not a course or OR expression")
        c['eqlist'] = eqlist
        c['inveqlist'] = []
        c['eqclass'] = {sigla}
    except:
        print(f"parsing equivs '{c['equiv']}' for course {sigla} failed:")
        traceback.print_exc()

for sigla, c in courses.items():
    for eq in c['eqlist']:
        if eq in courses:
            courses[eq]['inveqlist'].append(sigla)
            a = c['eqclass']
            b = courses[eq]['eqclass']
            if a is not b:
                if len(b) < len(a):
                    a, b = b, a
                for code in a:
                    b.add(code)
                    courses[code]['eqclass'] = b
        else:
            print(
                f"course {sigla} has equivalency with course {eq}, which does not exist")


def is_satisfied(passed: set[str], expr: Expr, allow_eq: bool, allow_inv_eq: bool, allow_trans_eq: bool) -> bool:
    if isinstance(expr, Req):
        if expr.code in passed:
            return True
        if allow_eq and expr.code in courses:
            for eq in courses[expr.code]['eqlist']:
                if eq in passed:
                    return True
        if allow_inv_eq and expr.code in courses:
            for eq in courses[expr.code]['inveqlist']:
                if eq in passed:
                    return True
        if allow_trans_eq and expr.code in courses:
            for eq in courses[expr.code]['eqclass']:
                if eq in passed:
                    return True
        return False
    elif isinstance(expr, And):
        for sub in expr.params:
            if not is_satisfied(passed, sub, allow_eq, allow_inv_eq, allow_trans_eq):
                return False
        return True
    elif isinstance(expr, Or):
        for sub in expr.params:
            if is_satisfied(passed, sub, allow_eq, allow_inv_eq, allow_trans_eq):
                return True
        return False
    else:
        return True


print(f"equivs for ING1001: {courses['ING1001']['eqlist']}")
print(f"equivs for IPP1000: {courses['IPP1000']['eqlist']}")

# Given a set of passed courses, search for a course that is takeable only if forward equivalencies are allowed
passed = ["FIL188", "ING1004", "MAT1203", "MAT1610", "QIM100E", "FIS0154", "ICE1514", "ICS1513", "IIC1103", "LET0003", "MAT1620", "VRA3010", "FIS0152", "IIC2233", "IIC2552", "IIQ1003", "IMT1001", "MAT1630", "MAT1640", "TTF061", "AST0112", "BIO143M", "EYP1113", "FIS0153", "IEE1533",
          "IIC1253", "IIC2553", "VRA100C", "DPT6270", "ICS1113", "IEE2103", "IIC2413", "IIC2552", "ING2030", "MUC701", "IEE2123", "IEE2713", "IIC2133", "IIC2143", "IIC2343", "IIC2553", "VRA1323", "VRA4000", "IIC2333", "IIC2513", "IIC2552", "ING1001", "IEE2613", "IEE2753", "DPT9035"]
passed = set(passed)
interesting = {
    "trans": [],
    "both": [],
    "fw": [],
    "bk": [],
}
for code, c in courses.items():
    fw = is_satisfied(passed, c['deps'], True, False, False)
    bk = is_satisfied(passed, c['deps'], False, True, False)
    both = is_satisfied(passed, c['deps'], True, True, False)
    trans = is_satisfied(passed, c['deps'], False, False, True)
    insts = list(courses[code]['instances'].keys())
    if both and not fw and not bk:
        # This course could only be taken if both directions are possible
        interesting["both"].append(code)
    if fw and not bk:
        interesting["fw"].append(code)
    if bk and not fw:
        interesting["bk"].append(code)
    if trans and not both:
        interesting["trans"].append(code)
for kind, codes in interesting.items():
    match kind:
        case "trans":
            print("courses that can only be taken if equivalencies are force-transitive")
        case "both":
            print("courses that can only be taken if equivalencies are both ways")
        case "fw":
            print(
                "courses that can only be taken if forward equivalencies are valid")
        case "bk":
            print(
                "courses that can only be taken if backward equivalencies are valid")
    codes.sort(key=lambda c: len(courses[c]['instances']), reverse=True)
    for code in codes:
        print(f"  {code} {list(courses[code]['instances'].keys())}")

#!/usr/bin/env python3

import json
import sys
import lzma
from collections import defaultdict


def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


args = sys.argv.copy()
args.pop(0)

opts = set()
for i in reversed(range(len(args))):
    if args[i].startswith("--"):
        opts.add(args[i][2:])
        args.pop(i)

if not args:
    log("usage: python3 make-universal.py [options] <JSON data files...>")
    log("  --strip-program    Remove course program descriptions.")
    log("  --compress         Compress the resulting JSON using LZMA.")
    log("  There must be exactly 1 catalogo file and 1+ buscacurso files.")
    log("  The file type is automatically recognized.")
    log("  The order in which files are specfied only matters if there is duplicated buscacursos data.")
    log("  In this case, a proper warning will be issued.")
    sys.exit()

universal = {}

catalogo = None
buscacursos = {}

for path in args:
    with open(path, 'r') as file:
        data = json.load(file)
        assert isinstance(data, dict)
        is_catalogo = False
        for key in data.keys():
            is_catalogo = '-' not in key
            break
        if is_catalogo:
            if catalogo is not None:
                raise Exception("mas de un catalogo")
            catalogo = data
        else:
            for period, pdata in data.items():
                if period in buscacursos:
                    log(
                        f"duplicated data for period {period}, using first copy")
                    continue
                buscacursos[period] = pdata

if not catalogo:
    raise Exception("no catalogo data")

if not buscacursos:
    raise Exception("no buscacursos data")

if 'strip-program' in opts:
    for course in catalogo.values():
        course['program'] = ""
    for courses in buscacursos.values():
        for course in courses.values():
            course['program'] = ""

for course in catalogo.values():
    course['instances'] = {}

warnings_emitted = defaultdict(lambda: 0)
max_identic_warnings = 8
max_showstr_len = 40
def shorten_str(s):
    if not isinstance(s, str):
        return s
    s = json.dumps(s, ensure_ascii=False)
    if len(s) > max_showstr_len:
        s = s[:max_showstr_len-4] + '"...'
    return s
def disagree(field, src, dst, *, srcname, dstname, override=False, silent_replace_empty=False, allow_clear=False):
    dstval = dst.get(field)
    srcval = src[field]
    empty_src = srcval is None or srcval == ""
    empty_dst = dstval is None or dstval == ""

    silent_override = False
    if not allow_clear and empty_src:
        override = False
    if silent_replace_empty and empty_dst and not empty_src:
        silent_override = True
        override = True
    if override:
        dst[field] = src[field]

    if srcval == dstval:
        return
    if override and silent_override:
        return
    if warnings_emitted[field, srcname] >= max_identic_warnings:
        return
 
    using = srcname if override else "main"
    srcval = shorten_str(srcval)
    dstval = shorten_str(dstval)
    log(f"{srcname} does not agree with main database on field {field} on course {dstname}, using {using} (main: {dstval}, {srcname}: {srcval})")
    warnings_emitted[field, srcname] += 1
    if warnings_emitted[field, srcname] >= max_identic_warnings:
        log(f"warned {max_identic_warnings} times about '{field}' from source {srcname}, supressing warnings from this source-field")

for period, data in sorted(buscacursos.items()):
    for code, src in data.items():
        if code not in catalogo:
            log(
                f"WARNING: skipping course {code} in buscacursos period {period} but not in catalogo")
            continue
        dst = catalogo[code]
        assert isinstance(dst, dict)
        # These properties always come from catalogo, even in buscacursos scrapes
        # Therefore, any disagreements mean something changed in catalogo
        for attr in ['req', 'conn', 'restr', 'equiv', 'program']:
            disagree(
                attr,
                src,
                dst,
                srcname=period,
                dstname=code,
                override=False,
            )
        # Each period has its own instance, so there is no conflict
        # name, credits and school are both in catalogo and buscacursos (keep both)
        # area and category only come from buscacursos
        # sections is per-section info and therefore belongs in the instances dict
        dst['instances'][period] = {
            'name': src['name'],
            'credits': src['credits'],
            'school': src['school'],
            'area': src['area'],
            'category': src['category'],
            'sections': src['sections'],
        }

out = json.dumps(catalogo).encode("utf-8")
if 'compress' in opts:
    out = lzma.compress(out)
sys.stdout.buffer.write(out)

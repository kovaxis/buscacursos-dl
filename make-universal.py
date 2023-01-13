#!/usr/bin/env python3

import json
import sys
import lzma


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
    log("usage: make-universal.py [options] <data files...>")
    log("  --strip-program    Remove course program descriptions.")
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

for period, data in sorted(buscacursos.items()):
    for code, src in data.items():
        if code not in catalogo:
            log(
                f"WARNING: skipping course {code} in buscacursos period {period} but not in catalogo")
            continue
        dst = catalogo[code]
        assert isinstance(dst, dict)
        for attr in ['credits', 'req', 'conn', 'restr', 'equiv', 'program']:
            if src[attr] != dst[attr]:
                log(
                    f"buscacursos (period {period}) and catalogo dont agree on attribute {attr} of course {code} (buscacursos says '{src[attr]}', catalogo says '{dst[attr]}')")
        dst['area'] = src['area']
        dst['category'] = src['category']
        dst['instances'][period] = {
            'name': src['name'],
            'school': src['school'],
            'sections': src['sections'],
        }

sys.stdout.buffer.write(lzma.compress(json.dumps(catalogo).encode("utf-8")))

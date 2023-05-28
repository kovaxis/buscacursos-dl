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
    log("usage: python3 make-universal.py [options] <data files...>")
    log("  --strip-program    Remove course program descriptions.")
    log("  --compress         Compress the resulting JSON using LZMA.")
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
        for attr in ['credits', 'req', 'conn', 'restr', 'equiv']:
            if src[attr] != dst[attr]:
                log(
                    f"buscacursos (period {period}) and catalogo dont agree on attribute {attr} of course {code} (buscacursos says '{src[attr]}', catalogo says '{dst[attr]}')")
        if src['program'] != '':
            if dst['program'] == '':
                log(f"ignoring program info in buscacursos, because catalogo has no program info")
            else:
                if src['program'] != dst['program']:
                    log(f"buscacursos (period {period}) and catalogo dont agree on program of course {code} (buscacursos: {len(src['program'])} characters starting with \"{src['program'][:30]}\", catalogo: {len(src['program'])} characters starting with \"{dst['program'][:30]}\")")
        dst['area'] = src['area']
        dst['category'] = src['category']
        dst['instances'][period] = {
            'name': src['name'],
            'school': src['school'],
            'sections': src['sections'],
        }

out = json.dumps(catalogo).encode("utf-8")
if 'compress' in opts:
    out = lzma.compress(out)
sys.stdout.buffer.write(out)

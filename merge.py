#!/usr/bin/env python3

import sys
import json

args = sys.argv[1:]

def merge(dst, src):
    if isinstance(dst, dict) and isinstance(src, dict):
        # Merge recursively
        for key, val in src.items():
            if key in dst:
                dst[key] = merge(dst[key], val)
            else:
                dst[key] = val
        return dst
    else:
        # Replace
        return src

out = None
for path in args:
    with open(path, 'r') as file:
        src = json.load(file)
        out = merge(out, src)
if isinstance(out, dict):
    out = dict(sorted(out.items(), reverse=True))
json.dump(out, sys.stdout)

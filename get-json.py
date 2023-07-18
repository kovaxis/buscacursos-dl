#!/usr/bin/env python3

import sys

if len(sys.argv) < 3:
    print(f"usage: {sys.argv[0]} <stdout.txt of main.py> <data.json>")
    print("    This script can be used to extract the raw JSON from")
    print("    the stdout of the main scraper, `main.py`.")
    sys.exit()

with open(sys.argv[1], 'r') as input:
    lines = input.readlines()
while lines and not lines[-1]:
    lines.pop()
with open(sys.argv[2], 'w') as output:
    output.write(lines[-1].strip())

#!/usr/bin/env python3
"""
    binarize.py: binarize labels in labeled file
    usage: binarize.py label < file
    20181109 erikt(at)xs4all.ml
"""

import sys

NEGLABEL = "__label__NEG"
POSLABEL = "__label__POS"
targetLabel = sys.argv.pop(1)

for line in sys.stdin:
    line = line.strip()
    fields = line.split()
    label = fields.pop(0)
    line = " ".join(fields)
    if label == targetLabel: print(POSLABEL,end="")
    else: print(NEGLABEL,end="")
    if line != "": print(" "+line)
    else: print()

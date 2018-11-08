#!/usr/bin/env python3
"""
    data-select.py: select labeled rows from data
    usage: data-select.py < file
    note: first outputs first 10% of rows, then the other 90%
    20181108 erikt(at)xs4all.nl
"""

import sys

MINROWS = 6
minRows = {"__label__ESS":3,"__label__POR":4}
labelCounts = {}
thisBuffer = []

for line in sys.stdin:
    line = line.strip()
    fields = line.split()
    label = fields[0]
    if not label in labelCounts or \
       (label in minRows and labelCounts[label] < minRows[label]) or \
       (not label in minRows and labelCounts[label] < MINROWS):
        print(line)
        if not label in labelCounts: labelCounts[label] = 0
        labelCounts[label] += 1
    else: thisBuffer.append(line)

for line in thisBuffer: print(line)

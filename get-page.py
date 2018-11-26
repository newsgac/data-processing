#!/usr/bin/env python3
"""
    get-page.py: get page of newspaper url
    usage: get-page.py < file.html
    20181126 erikt(at)xs4all.nl
"""

import re
import sys
import xml.etree.ElementTree as ET

COMMAND = sys.argv.pop(0)
CURRENTPAGEID = r"object-view-menu__navigate-results__input-search"
LASTPAGEID = r"object-view-menu__navigate-results__content"
CURRENTPAGENBR = r"value=\"(\d+)\""
LASTPAGENBR = r">(\d+)<"

def main(argv):
    for line in sys.stdin:
        if re.search(CURRENTPAGEID,line):
            results = re.search(CURRENTPAGENBR,line)
            if results: print(results.group(1))
        if re.search(LASTPAGEID,line):
            results = re.search(LASTPAGENBR,line)
            if results: print(results.group(1))

if __name__ == "__main__":
    sys.exit(main(sys.argv))

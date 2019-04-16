#!python3
# convertDates.py: convert dates in fastText data file for sorting
# usage: convertDates.py [back] < file.txt
# notes:
# * expected input: second field on line: DATE=MM/DD/YYY
# * generated output: second field on line: DATE=YYYY/MM/DD
# * optional argument back triggers backward conversion
# 20190416 erikt(at)xs4all.nl

import re
import sys

COMMAND = sys.argv.pop(0)
REGEXPFROM = r"^(DATE=)(\d\d/\d\d)/(\d\d\d\d)$"
REGEXPFROMBACK = r"^(DATE=)(\d\d\d\d)/(\d\d/\d\d)$"
REGEXPTO = r"\1\3/\2"

def convert(line):
    fields = line.split()
    try: fields[1] = re.sub(REGEXPFROM,REGEXPTO,fields[1])
    except Exception as e: sys.exit(COMMAND+": incomplete line: "+line)
    return(" ".join(fields))

def convertBack(line):
    fields = line.split()
    try: fields[1] = re.sub(REGEXPFROMBACK,REGEXPTO,fields[1])
    except Exception as e: sys.exit(COMMAND+": incomplete line: "+line)
    return(" ".join(fields))

def main(argv):
    if len(sys.argv) == 0: 
        for line in sys.stdin: print(convert(line))
    else: 
        for line in sys.stdin: print(convertBack(line))
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))


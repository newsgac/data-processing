#!/usr/bin/env python3
"""
    cwi2nlesc.py: convert kb articles from cwi to nlesc format
    usage: cwi2nlesc.py < file
    notes
    * expected input line format: id, date, article type, text
    * output line format: id (converted), date (converted), article type, text
    20190606 erikt(at)xs4all.nl
"""

import csv
import re
import sys

FIELDNAMES = ["Identifier","Datum","Article Type","Text"]
IDPREFIX = "http://resolver.kb.nl/resolve?urn="
IDSUFFIX = ":ocr"
DATESEPIN = "-"
DATESEPOUT = "/"

def convertId(articleId):
    return(IDPREFIX+articleId+IDSUFFIX)

def removeInitialZero(numString):
    return(re.sub(r"^0+",r"",numString))

def convertDate(dateString):
    year,month,day = dateString.split(DATESEPIN)
    return(DATESEPOUT.join([removeInitialZero(month),removeInitialZero(day),year]))

def main(argv):
    csvreader = csv.reader(sys.stdin)
    csvwriter = csv.DictWriter(sys.stdout,fieldnames=FIELDNAMES)
    csvwriter.writeheader()
    for row in csvreader:
        csvwriter.writerow({FIELDNAMES[0]:convertId(row[0]),
                            FIELDNAMES[1]:convertDate(row[1]),
                            FIELDNAMES[2]:row[2],
                            FIELDNAMES[3]:row[3]+" "+row[4]})

if __name__ == "__main__":
    sys.exit(main(sys.argv))

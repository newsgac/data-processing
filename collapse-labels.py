#!python3
"""
    collapse-labels.py: combine eight less interesting labels to one class
    usage: collapse-labels.py < fasttext-file.txt
    note: expected input line format: label text
    20190419 erikt(at)xs4all.nl
"""

import getopt
import re
import sys

COMMAND = sys.argv.pop(0)
LEVEL = "-l"
LEVEL1 = 9
LEVEL2 = 3
LABELSMED = [ "__label__MOP","__label__MED"]
LABELSOPI = [ "__label__HOO","__label__OPI"]
LABELSPOR = [ "__label__PRO","__label__POR"]
LABELSSER = [ "__label__ESS","__label__FIC","__label__ING","__label__LOS",\
              "__label__MED","__label__OVE","__label__POR","__label__SER" ]
LABELSNIE = [ "__label__ACH","__label__INT","__label__VER","__label__NIE" ]
LABELSCOL = [ "__label__OPI","__label__REC","__label__REP","__label__COL" ]

def convertLabel(label,options):
    if label in LABELSMED: label = LABELSMED[-1]
    if label in LABELSOPI: label = LABELSOPI[-1]
    if label in LABELSPOR: label = LABELSPOR[-1]
    if LEVEL in options and int(options[LEVEL]) <= LEVEL1:
        if label in LABELSSER: label = LABELSSER[-1]
    if LEVEL in options and int(options[LEVEL]) <= LEVEL2:
        if label in LABELSNIE: label = LABELSNIE[-1]
        if label in LABELSCOL: label = LABELSCOL[-1]
    return(label)

def convertLine(line,options):
   fields = line.split()
   try: 
       fields[0] = convertLabel(fields[0],options)
       return(" ".join(fields))
   except Exception as e:
       sys.exit(COMMAND+": problem processing line: "+line+": "+str(e))
 
def processOptions(argv):
    optlist,args = getopt.getopt(argv,"l:")
    opthash = {}
    for opt,val in optlist: opthash[opt] = val
    return(opthash,args)

def main(argv):
    options,args = processOptions(argv)
    for line in sys.stdin:
        print(convertLine(line,options))

if __name__ == "__main__":
    sys.exit(main(sys.argv))

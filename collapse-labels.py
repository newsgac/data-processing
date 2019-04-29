#!python3
"""
    collapse-labels.py: combine eight less interesting labels to one class
    usage: collapse-labels.py [-l LEVEL ] [ -s ] < fasttext-file.txt
    notes: 
    * expected input line format: label text
    * option -l specifies number of target labels: 9 or 3 (16 is default)
    * option -s shows all sets of collapsed labels
    20190419 erikt(at)xs4all.nl
"""

import getopt
import re
import sys

COMMAND = sys.argv.pop(0)
LEVEL = "-l"
LEVEL1 = 9
LEVEL2 = 3
LABELSET = {}
LABELSET["MED"] = ["__label__MOP","__label__MED"]
LABELSET["OPI"] = ["__label__HOO","__label__OPI"]
LABELSET["POR"] = ["__label__PRO","__label__POR"]
LABELSET["SER"] = ["__label__ESS","__label__FIC","__label__ING","__label__LOS",\
                   "__label__MED","__label__OVE","__label__POR","__label__SER" ]
LABELSET["NIE"] = ["__label__INT","__label__REP","__label__VER","__label__NIE" ]
LABELSET["COL"] = ["__label__ACH","__label__OPI","__label__REC","__label__COL" ]

def convertLabel(label,options):
    if label in LABELSET["MED"]: label = LABELSET["MED"][-1]
    if label in LABELSET["OPI"]: label = LABELSET["OPI"][-1]
    if label in LABELSET["POR"]: label = LABELSET["POR"][-1]
    if LEVEL in options and int(options[LEVEL]) <= LEVEL1:
        if label in LABELSET["SER"]: label = LABELSET["SER"][-1]
    if LEVEL in options and int(options[LEVEL]) <= LEVEL2:
        if label in LABELSET["NIE"]: label = LABELSET["NIE"][-1]
        if label in LABELSET["COL"]: label = LABELSET["COL"][-1]
    return(label)

def convertLine(line,options):
   fields = line.split()
   try: 
       fields[0] = convertLabel(fields[0],options)
       return(" ".join(fields))
   except Exception as e:
       sys.exit(COMMAND+": problem processing line: "+line+": "+str(e))
 
def processOptions(argv):
    optlist,args = getopt.getopt(argv,"l:s")
    opthash = {}
    for opt,val in optlist: opthash[opt] = val
    return(opthash,args)

def getShortLabel(label):
    return(re.sub("__label__","",label))

def showLabelSets():
    for label in LABELSET:
        print(getShortLabel(LABELSET[label][-1]),"= ",end="")
        for i in range(0,len(LABELSET[label])):
            if i > 0: print(" + ",end="")
            print(getShortLabel(LABELSET[label][i]),end="")
        print()

def main(argv):
    options,args = processOptions(argv)
    if "-s" in options:
        showLabelSets()
        return
    for line in sys.stdin:
        print(convertLine(line,options))

if __name__ == "__main__":
    sys.exit(main(sys.argv))

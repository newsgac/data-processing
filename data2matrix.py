#!/usr/bin/env python
"""
    data2matrix.py: convert output of uniq to confusion matrix
    usage: uniq -c < file | python data2matrix.py
    note: expected line input: number goldlabel predictedlabel
    20190429 erikt(at)xs4all.nl
"""

import re
import sys

COMMAND = sys.argv.pop(0)
MINFIELDS = 2

def getShortLabel(label):
    return(re.sub("__label__","",label))

def readLines():
    data = {}
    labels = []
    for line in sys.stdin:
        fields = line.split()
        if len(fields) > 0 and fields[0] == "": fields.pop(0)
        if len(fields) < MINFIELDS:
            sys.exit(COMMAND+": incomplete line: ",line)
        if not fields[1] in data: data[fields[1]] = {}
        data[fields[1]][fields[2]] = int(fields[0])
        if not fields[1] in labels: labels.append(fields[1])
    return(data,labels)

def main(argv):
    data,labels = readLines()
    print("# column names: [",end="") 
    for i in range(0,len(labels)):
        labelGold = labels[i]
        print("\""+getShortLabel(labelGold)+"\"",end="")
        if i < len(labels)-1: print(",",end="")
        else: print("]",end="")
    print("")
    for i in range(0,len(labels)):
        labelGold = labels[i]
        if i == 0: print("[",end="")
        else: print(" ",end="")
        print("[",end="")
        for j in range(0,len(labels)):
            labelPredicted = labels[j]
            if labelGold in data and labelPredicted in data[labelGold]:
                print(" {0:4d}".format(data[labelGold][labelPredicted]),end="")
            else:
                print(" {0:4d}".format(0),end="")
            if j < len(labels)-1: print(",",end="")
        print("]",end="")
        if i < len(labels)-1: print(",")
        else: print("]")

if __name__ == "__main__":
    sys.exit(main(sys.argv))

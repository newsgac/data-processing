#!/usr/bin/env python3
"""
    over-sample.py: use data duplication to convert unbalanced to balanced data
    usage: over-sample.py < file
    note: expected line format: label SPACE data
    20181122 erikt(at)xs4all.nl
"""

import sys

COMMAND = sys.argv.pop(0)

def getLabel(line):
    fields = line.split()
    try: 
        label = fields.pop(0)
        lineData = " ".join(fields)
    except Exception as e: sys.exit(COMMAND+": error: "+str(e))
    return(label,lineData)

def printAll(data,label):
    for d in data: print(label,d)

def printPart(data,label,count):
    if count > len(data): 
        sys.exit(COMMAND+": data set is too small: "+label+" ("+count+")")
    for i in range(0,count): print(label,data[i])

def readFileFromStdin():
    data = {}
    for line in sys.stdin:
        line = line.strip()
        label,lineData = getLabel(line)
        if not label in data: data[label] = []
        data[label].append(lineData)
    return(data)

def getLargestSize(data):
    return(max([len(data[key]) for key in data.keys()]))

def printData(data,largestSize):
    for label in data.keys():
        size = 0
        while size+len(data[label]) < largestSize: 
            printAll(data[label],label)
            size += len(data[label])
        if size < largestSize:
            printPart(data[label],label,largestSize-size)

def main(argv):
    data = readFileFromStdin()
    largestSize = getLargestSize(data)
    printData(data,largestSize)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

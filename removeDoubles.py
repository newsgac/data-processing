#!/usr/bin/python3 -W all
"""
    removeDoubles.py: select data from file2 that is not in file1
    usage: rmeoveDoubles.py file1 file2
    note: used for selecting new linked data not in erik-fasttext.txt
    20180831 erikt(at)xs4all.nl
"""

import re
import sys

COMMAND = sys.argv.pop(0)

def processDate(date):
    month,day,year = date.split("/")
    month = re.sub("^DATE=","",day)
    month = re.sub(r"^0","",day)
    day = re.sub(r"^0","",month)
    if re.search(r"....",year): return("DATE="+month+"/"+day+"/"+year)
    else: return("DATE="+month+"/"+day+"/19"+year)

def readFile(fileName):
    lines = []
    labels = []
    try:
        inFile = open(fileName,"r")
        for line in inFile: 
            tokens = line.strip().split()
            labels.append(tokens.pop(0))
            date = processDate(tokens.pop(0))
            tokens.insert(0,date)
            line = " ".join(tokens)
            if line in lines: print("warning: duplicate line in file "+fileName)
            lines.append(line)
        inFile.close()
    except Exception as e: 
        sys.exit(COMMAND+": error processing file "+fileName+": "+str(e))
    return(lines,labels)

def main(argv):
    fileName1,fileName2 = argv
    lines1,labels1 = readFile(fileName1)   
    lines2,labels2 = readFile(fileName2)
    inLines1 = {}
    for i in range(0,len(lines1)): inLines1[lines1[i]] = True
    for i in range(0,len(lines2)):
        if not lines2[i] in inLines1: print(labels2[i],lines2[i])

if __name__ == "__main__":
    sys.exit(main(sys.argv))

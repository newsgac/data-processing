#!/usr/bin/env python3
"""
    fasttext2files.py: extract texts from fasttext file, store in seperate files
    usage: fasttext2files.py
    20181206 erikt(at)xs4all.nl
"""

import sys

COMMAND = sys.argv.pop(0)
MINFILENAMELEN = 8

def getText(line):
    fields = line.split()
    label = fields.pop(0)
    date = fields.pop(0)
    text = " ".join(fields)
    return(text)

def makeFileName(thisId):
    fileName = str(thisId)+".txt"
    while len(fileName) < MINFILENAMELEN: fileName = "0"+fileName
    return(fileName)

def saveText(text,thisId):
    fileName = makeFileName(thisId)
    try: outFile = open(fileName,"w")
    except Exception as e: 
        sys.exit(COMMAND+": cannot write file "+fileName+": "+str(e))
    print(text,file=outFile)
    outFile.close()

def main(argv):
    thisId = 1
    for line in sys.stdin:
        line = line.strip()
        text = getText(line)
        saveText(text,thisId)
        thisId += 1

if __name__ == "__main__":
    sys.exit(main(sys.argv))

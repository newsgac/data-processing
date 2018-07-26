#!/usr/bin/python3 -W all
"""
    compareLinks.py: compare text-metadata links by two annotators
    usage: compareLinks.py file1 file2
    20180726 erikt(at)xs4all.nl
"""

import csv
import re
import sys

COMMAND = sys.argv.pop(0)
IDFIELD = "Artikel ID"
KBIDFIELD = "KB-identifier"
SEPARATORTAB = "\t"

def readAnnotations(fileName,preAnnotated):
    annotated = list(preAnnotated)
    try:
        inFile = open(fileName,"r",encoding="utf-8")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORTAB)
        for row in csvReader:
            if KBIDFIELD in row and IDFIELD in row and row[KBIDFIELD] != "":
                annotated.append({"metadataId":row[IDFIELD],"textIds":row[KBIDFIELD]})
        inFile.close()
    except: sys.exit(COMMAND+": error processing file "+fileName)
    return(annotated)

def compare(annotations1,annotations2):
    dictionary1 = {}
    for data in annotations1: 
        dictionary1[data["metadataId"]] = data["textIds"]
    dictionary2 = {}
    for data in annotations2: 
        dictionary2[data["metadataId"]] = data["textIds"]
    totalPairs1 = 0
    totalPairs2 = 0
    totalEqualPairs = 0
    for key in dictionary1:
        for textId1 in dictionary1[key].split():
            textId1 = re.sub(r":ocr$","",textId1)
            totalPairs1 += 1
            if key in dictionary2:
                for textId2 in dictionary2[key].split():
                    textId2 = re.sub(r":ocr$","",textId2)
                    if textId2 == textId1: 
                        totalEqualPairs += 1
                        break
    for key in dictionary2:
        for textId2 in dictionary2[key].split():
            totalPairs2 += 1
    return(totalPairs1,totalPairs2,totalEqualPairs)

def main(argv):
    try: fileName1,fileName2 = argv
    except: sys.exit("usage:",COMMAND,"file1 file2")
    annotations1 = readAnnotations(fileName1,[])
    annotations2 = readAnnotations(fileName2,[])
    totalPairs1,totalPairs2,totalEqualPairs = compare(annotations1,annotations2)
    print(totalPairs1,totalPairs2,totalEqualPairs)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

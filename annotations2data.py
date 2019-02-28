#!/usr/bin/env python3
"""
    annotations2data.py: convert manual annotations to data
    usage: annotations2data.py < annotations.tsv
    notes:
    * expected input: tab-separated annotations file, 1: id; 2: urls
    * also uses file frank-dutch.csvfor meta data
    * output: comma-separated data for data2fasttext.py: Genre Identifier Page
    20190228 erikt(at)xs4all.nl
"""

import csv
import sys

COMMA = ","
COMMAND = sys.argv.pop(0)
TAB = "\t"
DATADIR = "/home/erikt/projects/newsgac/data"
METADATAFILE = DATADIR+"/frank-dutch.csv"
METADATAID = "Artikel ID"
NEWSPAPER = "Titel krant" 
DATE = "Datum"
PAGE = "Paginanummer"
GENRE = "Genre"
URLS = "KB-identifier"

def readCsv(inFileName,delimiter=COMMA):
    try:
        if inFileName != "-": inFile = open(inFileName,"r")
        else: inFile = sys.stdin
        csvreader = csv.DictReader(inFile,delimiter=delimiter)
        table = []
        for row in csvreader: table.append(row)
        inFile.close()
        return(table)
    except Exception as e:
        sys.exit(COMMAND+": error processing file "+inFileName+": "+str(e))

def list2dict(listIn,keyColumnName):
    dictOut = {}
    for row in listIn:
        try: dictOut[row[keyColumnName]] = row
        except Exception as e: sys.exit(COMMAND+": problem with element: "+row+"+: "+str(e))
    return(dictOut)

def combineLists(metadataList,annotationsList):
    annotationsDict = list2dict(annotationsList,METADATAID)
    metadataDict = list2dict(metadataList,METADATAID)
    outList = []
    for key in annotationsDict:
        try:
            if not key in metadataDict:
                print(COMMAND+": key "+key+" not found",file=sys.stderr)
                break
            outList.append({METADATAID:key,\
               NEWSPAPER:metadataDict[key][NEWSPAPER],\
               DATE:metadataDict[key][DATE],PAGE:metadataDict[key][PAGE],\
               GENRE:metadataDict[key][GENRE],URLS:annotationsDict[key][URLS]})
        except: print(key)
    return(outList)

def writeCsv(listIn):
    if len(listIn) > 0:
        csvwriter = csv.DictWriter(sys.stdout,listIn[0].keys())
        csvwriter.writeheader()
        for row in listIn: csvwriter.writerow(row)

def main(argv):
    metadataList = readCsv(METADATAFILE)
    annotationsList = readCsv("-",TAB)
    listOut = combineLists(metadataList,annotationsList)
    writeCsv(listOut)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

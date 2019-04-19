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
NEWSTYPE = "Aard nieuws"
SELFCLASS = "Zelfclassificatie"
QUOTES = "Directe quotes"
TOPIC = "Onderwerp"
AUTHOR = "Soort Auteur"
SPACE = " "

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

def combineLists(metadataList,annotationsDict):
    metadataDict = list2dict(metadataList,METADATAID)
    outList = []
    for key in annotationsDict:
        try:
            if not key in metadataDict:
                print(COMMAND+": key "+key+" not found",file=sys.stderr)
                break
            outList.append({METADATAID:key,\
               NEWSPAPER:metadataDict[key][NEWSPAPER],\
               DATE:metadataDict[key][DATE],\
               PAGE:metadataDict[key][PAGE],\
               NEWSTYPE:metadataDict[key][NEWSTYPE],\
               SELFCLASS:metadataDict[key][SELFCLASS],\
               QUOTES:metadataDict[key][QUOTES],\
               TOPIC:metadataDict[key][TOPIC],\
               AUTHOR:metadataDict[key][AUTHOR],\
               GENRE:metadataDict[key][GENRE],\
               URLS:annotationsDict[key]})
        except: print(key)
    return(outList)

def writeCsv(listIn):
    if len(listIn) > 0:
        csvwriter = csv.DictWriter(sys.stdout,listIn[0].keys())
        csvwriter.writeheader()
        for row in listIn: csvwriter.writerow(row)

def removeUrl(urls,urlTarget):
    urlListIn = set(urls.split(SPACE))
    urlListOut = []
    for url in urlListIn:
        if url != urlTarget: urlListOut.append(url)
    return(SPACE.join(urlListOut))

def removeDuplicates(annotationsList):
    metadataIdsDict = {}
    urlsDict = {}
    for element in annotationsList:
        metadataId = element[METADATAID]
        urls = element[URLS]
        for url in set(urls.split(SPACE)):
            if url in urlsDict:
                metadataIdsDict[urlsDict[url]] = removeUrl(metadataIdsDict[urlsDict[url]],url)
                if metadataIdsDict[urlsDict[url]] == "":
                    del(metadataIdsDict[urlsDict[url]])
                del(urlsDict[url])
        if metadataId in metadataIdsDict:
            for url in set(metadataIdsDict[metadataId].split(SPACE)): del (urlsDict[url])
            del(metadataIdsDict[metadataId])
        metadataIdsDict[metadataId] = urls
        for url in urls.split(SPACE): urlsDict[url] = metadataId
    return(metadataIdsDict)

def main(argv):
    metadataList = readCsv(METADATAFILE)
    annotationsList = readCsv("-",TAB)
    annotationsDict = removeDuplicates(annotationsList)
    listOut = combineLists(metadataList,annotationsDict)
    writeCsv(listOut)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

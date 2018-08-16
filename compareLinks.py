#!/usr/bin/python3 -W all
"""
    compareLinks.py: compare text-metadata links by two annotators
    usage: compareLinks.py file1 file2
    20180726 erikt(at)xs4all.nl
"""

import csv
import re
import sys
import warnings

COMMAND = sys.argv.pop(0)
IDFIELD = "Artikel ID"
KBIDFIELD = "KB-identifier"
GENREFIELD = "Genre"
METADATAIDFIELD = "metadataId"
DATEFIELD = "Datum"
PAGEFIELD = "Paginanummer"
SURFACEFIELD = "Oppervlakte"
TOPICFIELD = "Onderwerp"
TEXTIDSFIELD = "textIds"
LOCATIONSFIELD = "locations"
SEPARATORCOMMA = ","
SEPARATORTAB = "\t"
OCRSUFFIX = r":ocr\b"
EMPTYSTRING = ""

def makeReverse(annotated):
    reverse = {}
    for thisKey in annotated:
        for textId in annotated[thisKey]["textIds"].split():
            if textId in reverse:
                print("<p><font style=\"color:red;\">error: duplicate key "+thisKey)
            reverse[textId] = thisKey
    return(reverse)

def removeLink(annotated,reverse,textId):
    thisKey = reverse[textId]
    textIds = annotated[thisKey][TEXTIDSFIELD].split()
    index = textIds.index(textId)
    textIds.pop(index)
    del(reverse[textId])
    if len(textIds) > 0:
        annotated[thisKey][TEXTIDSFIELD] = " ".join(textIds)
    else:
        del(annotated[thisKey])
    return(annotated,reverse)

def readAnnotations(fileName,preAnnotated):
    annotated = dict(preAnnotated)
    reverse = makeReverse(annotated)
    try:
        inFile = open(fileName,"r",encoding="utf-8")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORTAB)
        for row in csvReader:
            if KBIDFIELD in row and IDFIELD in row and row[KBIDFIELD] != "":
                thisKey = row[IDFIELD]
                textIds = row[KBIDFIELD]
                for textId in textIds.split():
                    if textId in reverse: annotated,reverse = removeLink(annotated,reverse,textId)
                if thisKey in annotated:
                    for textId in annotated[thisKey][TEXTIDSFIELD].split():
                        annotated,reverse = removeLink(annotated,reverse,textId)
                for textId in textIds.split(): reverse[textId] = thisKey
                annotated[thisKey] = {TEXTIDSFIELD:textIds}
        inFile.close()
    except Exception as e: 
        sys.exit(COMMAND+": error processing file "+fileName+": "+str(e))
    return(annotated)

def readMetadata(fileName):
    genres = {}
    locations = {}
    try:
        inFile = open(fileName,"r",encoding="utf-8")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORCOMMA)
        for row in csvReader:
            genres[row[IDFIELD]] = row[GENREFIELD]
            locations[row[IDFIELD]] = row[DATEFIELD]+" "+row[PAGEFIELD]
    except Exception as e:
        sys.exit(COMMAND+": error processing file "+fileName+": "+str(e))
    inFile.close()
    return(genres,locations)

def flatten(annotations):
    links = {}
    for metadataId in annotations:
        textIds = annotations[metadataId][TEXTIDSFIELD]
        for textId in textIds.split():
            textId = re.sub(OCRSUFFIX,EMPTYSTRING,textId)
            if textId in links: sys.exit(COMMAND+": cannot happen\n")
            links[textId] = metadataId
    return(links)

def compare(annotations1,annotations2,locations,genres):
    links1 = flatten(annotations1)
    links2 = flatten(annotations2)
    totalPairs1 = len(links1)
    totalPairs2 = len(links2)
    totalEqualPairs = 0
    totalEqualGenres = 0
    noLinks = 0
    for textId in links1:
        if not textId in links2: 
            noLinks += 1
            print("no link: ",links1[textId],"-",locations[links1[textId]],textId.split(":")[4])
        else:
            if links2[textId] == links1[textId]:
                totalEqualPairs += 1
            else: 
                if links1[textId] in locations:
                    print("article:",links1[textId],links2[textId],locations[links1[textId]],textId.split(":")[4])
                else:
                    print("article:",links1[textId],links2[textId],"LOC",textId.split(":")[4])
            if links1[textId] in genres and links2[textId] in genres:
                if genres[links1[textId]] == genres[links2[textId]]:
                    totalEqualGenres += 1
                else: 
                    if links1[textId] in locations:
                        print("genre:",links1[textId],links2[textId],locations[links1[textId]],textId.split(":")[4],genres[links1[textId]],genres[links2[textId]])
                    else:
                        print("genre:",links1[textId],links2[textId],"LOC",textId.split(":")[4],genres[links1[textId]],genres[links2[textId]])
            elif links1[textId] in genres:
                print("incomplete genre (1):",links1[textId],links2[textId],textId,genres[links1[textId]])
            elif links2[textId] in genres:
                print("incomplete genre (2):",links1[textId],links2[textId],textId,genres[links2[textId]])
    return(totalPairs1,totalPairs2,totalEqualPairs,totalEqualGenres,noLinks)

def main(argv):
    try: annotationFile1,annotationFile2,metadataFile = argv
    except: sys.exit("usage:",COMMAND,"file1 file2")
    annotations1 = readAnnotations(annotationFile1,[])
    annotations2 = readAnnotations(annotationFile2,[])
    genres,locations = readMetadata(metadataFile)
    totalPairs1,totalPairs2,totalEqualPairs,totalEqualGenres,noLinks = \
        compare(annotations1,annotations2,locations,genres)
    print("size file 1:",totalPairs1,"size file2:",totalPairs2,"article agreement:",totalEqualPairs,"genre agreement:",totalEqualGenres,"no links:",noLinks)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

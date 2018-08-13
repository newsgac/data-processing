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
SEPARATORTAB = "\t"
OCRSUFFIX = r":ocr\b"
EMPTYSTRING = ""

def readAnnotations(fileName,preAnnotated):
    annotated = list(preAnnotated)
    locations = {}
    try:
        inFile = open(fileName,"r",encoding="utf-8")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORTAB)
        for row in csvReader:
            if KBIDFIELD in row and IDFIELD in row and row[KBIDFIELD] != "":
                annotated.append({"metadataId":row[IDFIELD], \
                                  "textIds":row[KBIDFIELD]})
                if DATEFIELD in row:
                    locations[row[IDFIELD]] = row[DATEFIELD]+" "+row[PAGEFIELD]
        inFile.close()
    except Exception as e: 
        sys.exit(COMMAND+": error processing file "+fileName+": ",str(e))
    return(annotated,locations)

def flatten(annotations):
    links = {}
    genres = {}
    metadataLinks = {}
    for data in annotations:
        metadataId = data[METADATAIDFIELD]
        textIds = data[TEXTIDSFIELD]
        if metadataId in metadataLinks:
            for textId in metadataLinks[metadataId].split(): 
                del(links[textId])
            del(metadataLinks[metadataId])
        for textId in textIds.split():
            textId = re.sub(OCRSUFFIX,EMPTYSTRING,textId)
            if textId in links:
                siblings = metadataLinks[links[textId]].split()
                index = siblings.index(textId)
                siblings = siblings[0:index]+siblings[(index+1):]
                metadataLinks[links[textId]] = " ".join(siblings)
            links[textId] = metadataId
        if GENREFIELD in data: genres[metadataId] = data[GENRE]
        else: genres[metadataId] = EMPTYSTRING
        metadataLinks[metadataId] = re.sub(OCRSUFFIX,EMPTYSTRING,textIds)
    return(links,genres)

def compare(annotations1,annotations2,locations):
    links1,genres1 = flatten(annotations1)
    links2,genres2 = flatten(annotations2)
    totalPairs1 = len(links1.keys())
    totalPairs2 = len(links2.keys())
    totalEqualPairs = 0
    totalEqualGenres = 0
    for textId in links1:
        if textId in links2:
            if links2[textId] == links1[textId]:
                totalEqualPairs += 1
            else: 
                if links1[textId] in locations:
                    print("link:",links1[textId],links2[textId],locations[links1[textId]],textId)
                else:
                    print("link:",links1[textId],links2[textId],"LOC",textId)
            if links2[textId] in genres1 and \
               genres1[links2[textId]] == genres1[links1[textId]]:
                totalEqualGenres += 1
            else: 
                if links1[textId] in locations:
                    print("genre:",links1[textId],links2[textId],locations[links1[textId]],textId)
                else:
                    print("genre:",links1[textId],links2[textId],"LOC",textId)
    return(totalPairs1,totalPairs2,totalEqualPairs,totalEqualGenres)

def main(argv):
    try: fileName1,fileName2 = argv
    except: sys.exit("usage:",COMMAND,"file1 file2")
    annotations1,locations1 = readAnnotations(fileName1,[])
    annotations2,locations2 = readAnnotations(fileName2,[])
    if len(locations1) > 0: locations = locations1
    else: locations = locations2
    totalPairs1,totalPairs2,totalEqualPairs,totalEqualGenres = \
        compare(annotations1,annotations2,locations)
    print("size file 1:",totalPairs1,"size file2:",totalPairs2,"article agreement:",totalEqualPairs,"genre agreement:",totalEqualGenres)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

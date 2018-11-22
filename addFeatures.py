#!/usr/bin/env python3
"""
    addFeatures.py: add linguistic features to fasttext file
    usage: addFeatures.py < file
    20181122 erikt(at)xs4all.nl
"""

import re
import spacy
import sys

COMMAND = sys.argv.pop(0)
SHORTTEXT = 1349
MEDIUMTEXT = 3516
LONGTEXT = 6210
SMALLI = 0.002171552660152009
MEDIUMI = 0.005797101449275362
LARGEI = 0.012850467289719626
SMALLADJADV = 0.1073558648111332
MEDIUMADJADV = 0.13556618819776714
LARGEADJADV = 0.152401853206535
SMALLENT = 0.044374009508716325
MEDIUMENT = 0.06188340807174888
LARGEENT = 0.09246575342465753
SMALLNUM = 0.011776251226692836
MEDIUMNUM = 0.020022667170381564
LARGENUM = 0.034198860037998734

def getTextLengthLabel(text):
    textLength = len(text)
    if textLength < SHORTTEXT: return(["VERYSHORT","SHORT"])
    elif textLength < MEDIUMTEXT: return(["SHORT","MEDIUM"])
    elif textLength < LONGTEXT: return(["MEDIUM","LONG"])
    else: return(["LONG","VERYLONG"])

def getILabel(frac):
    if frac == 0.0: return(["NO"])
    elif frac < SMALLI: return(["NO","SMALL"])
    elif frac < MEDIUMI: return(["SMALL","MEDIUM"])
    elif frac < LARGEI: return(["MEDIUM","LARGE"])
    else: return(["LARGE","VERYLARGE"])

def getFracLabel(frac,small,medium,large):
    if frac < small: return(["VERYSMALL","SMALL"])
    elif frac < medium: return(["SMALL","MEDIUM"])
    elif frac < large: return(["MEDIUM","LARGE"])
    else: return(["LARGE","VERYLARGE"])

def getAdjAdvLabel(frac):
    return(getFracLabel(frac,SMALLADJADV,MEDIUMADJADV,LARGEADJADV))

def getEntLabel(frac):
    return(getFracLabel(frac,SMALLENT,MEDIUMENT,LARGEENT))

def getNumLabel(frac):
    return(getFracLabel(frac,SMALLNUM,MEDIUMNUM,LARGENUM))

def countI(text):
    iCount = 0
    for word in text.split():
        if re.search(r"^[iI][Kk]$",word): iCount += 1
    return(iCount)

def countAdjAdv(postags):
    adjAdvCount = 0
    for pos in postags:
        if re.search(r"^(Adj|Adv)",pos.tag_): adjAdvCount += 1
    return(adjAdvCount)

def countNum(postags):
    numCount = 0
    for pos in postags:
        if re.search(r"^(Num|NUM)",pos.tag_): numCount += 1
    return(numCount)

def getSyntaxCounts(text,dutchTagger):
    pos = dutchTagger(text)
    iCount = countI(text)
    adjAdvCount = countAdjAdv(pos)
    entityCount = len(pos.ents)
    numCount = countNum(pos)
    textLength = len(text.split())
    if textLength == 0: return(0.0,0.0,0.0)
    else: return(iCount/textLength,adjAdvCount/textLength,entityCount/textLength,numCount/textLength)

def getLabelDateText(line):
    try:
        fields = line.split()
        label = fields.pop(0)
        date = fields.pop(0)
        text = " ".join(fields)
    except Exception as e:
        sys.exit(COMMAND+": error: "+str(e))
    return(label,date,text)

def readFileFromStdin():
    data = []
    for line in sys.stdin:
        line = line.strip()
        label,date,text = getLabelDateText(line)
        data.append({"label":label,"date":date,"text":text})
    return(data)

def printData(data):
    dutchTagger = spacy.load("nl")
    for d in data:
        iFrac,adjAdvFrac,entFrac,numFrac = getSyntaxCounts(d["text"],dutchTagger) 
        print(d["label"],d["date"],end=" ")
        for length in getTextLengthLabel(d["text"]): 
            print("FTCLEN"+length,end=" ")
        for iString in getILabel(iFrac):
            print("FTICOU"+iString,end=" ")
        for adjAdvString in getAdjAdvLabel(adjAdvFrac):
            print("FTADJA"+adjAdvString,end=" ")
        for entString in getEntLabel(entFrac):
            print("FTENTI"+entString,end=" ")
        for numString in getNumLabel(numFrac):
            print("FTNUMB"+numString,end=" ")
        print(d["text"])

def main(argv):
    data = readFileFromStdin()
    printData(data)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

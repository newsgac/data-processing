#!/usr/bin/env python3
"""
    addFeatures.py: add linguistic features to fasttext file
    usage: addFeatures.py < file
    20181122 erikt(at)xs4all.nl
"""

import re
import spacy
import sys
import xml.etree.ElementTree as ET

COMMAND = sys.argv.pop(0)
PATTERNDICTDIR = "/home/erikt/projects/newsgac/data-processing"
PATTERNDICTFILENAME = PATTERNDICTDIR+"/nl-sentiment.xml"
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
SMALLQUOTE = 0.001876172607879925
MEDIUMQUOTE = 0.004545454545454545
LARGEQUOTE = 0.010410641989589358
SMALLINT = 0.03063829787234043
MEDIUMINT = 0.041703056768558955
LARGEINT = 0.05049504950495049
SMALLPOL = -0.00048622366288492695
MEDIUMPOL = 0.001670146137787057
LARGEPOL = 0.004369414101290964
SMALLSUBJ = 0.015544675642594862
MEDIUMSUBJ = 0.02238636363636363
LARGESUBJ = 0.028221415607985478
INTENSIFIERS = { "zeer":True, "erg":True, "veel":True, "vele":True, "heel":True, "hele":True, "echt":True, "zwaar":True, "zware":True, "te":True, "zelfs":True, "zeker":True, "nadrukkelijk":True, "buitengewoon":True, "goed":True, "totaal":True, "totale":True, "pijnlijk":True, "sterk":True, "graag":True, "nogal":True, "zo":True, "heus":True, "hartstikke":True, "onvergetelijk":True }

def getTextLengthLabel(text):
    textLength = len(text)
    if textLength < SHORTTEXT: return(["VERYSHORT","SHORT"])
    elif textLength < MEDIUMTEXT: return(["SHORT","MEDIUM"])
    elif textLength < LONGTEXT: return(["MEDIUM","LONG"])
    else: return(["LONG","VERYLONG"])

def getFracLabel(frac,small,medium,large):
    if frac < small: return(["VERYSMALL","SMALL"])
    elif frac < medium: return(["SMALL","MEDIUM"])
    elif frac < large: return(["MEDIUM","LARGE"])
    else: return(["LARGE","VERYLARGE"])

def getFracLabelZero(frac,small,medium,large):
    if frac == 0.0: return(["ZERO"])
    elif frac < small: return(["ZERO","SMALL"])
    elif frac < medium: return(["SMALL","MEDIUM"])
    elif frac < large: return(["MEDIUM","LARGE"])
    else: return(["LARGE","VERYLARGE"])

def getILabel(frac):
    return(getFracLabelZero(frac,SMALLI,MEDIUMI,LARGEI))

def getAdjAdvLabel(frac):
    return(getFracLabel(frac,SMALLADJADV,MEDIUMADJADV,LARGEADJADV))

def getEntLabel(frac):
    return(getFracLabel(frac,SMALLENT,MEDIUMENT,LARGEENT))

def getNumLabel(frac):
    return(getFracLabel(frac,SMALLNUM,MEDIUMNUM,LARGENUM))

def getQuoteLabel(frac):
    return(getFracLabelZero(frac,SMALLQUOTE,MEDIUMQUOTE,LARGEQUOTE))

def getIntLabel(frac):
    return(getFracLabel(frac,SMALLINT,MEDIUMINT,LARGEINT))

def getPolLabel(frac):
    return(getFracLabel(frac,SMALLPOL,MEDIUMPOL,LARGEPOL))

def getSubjLabel(frac):
    return(getFracLabel(frac,SMALLSUBJ,MEDIUMSUBJ,LARGESUBJ))

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

def countQuotes(text):
    quoteCount = 0
    for word in text.split():
        if word == '"' or word == "'": quoteCount += 1
    return(quoteCount)

def countIntensifiers(postags):
    intCount = 0
    for p in range(0,len(postags)):
        if p > 0 and re.search(r"^(Adv|Adj)",postags[p].tag_) and \
           re.search(r"^(Adv|Adj)",postags[p-1].tag_) and \
           (str(postags[p]).lower() in INTENSIFIERS or \
            str(postags[p]).lower()+"e" in INTENSIFIERS):
           intCount += 1
    return(intCount)

def getSyntaxCounts(text,dutchTagger):
    pos = dutchTagger(text)
    iCount = countI(text)
    adjAdvCount = countAdjAdv(pos)
    entityCount = len(pos.ents)
    numCount = countNum(pos)
    textLength = len(text.split())
    quoteCount = countQuotes(text)
    intCount = countIntensifiers(pos)
    if textLength == 0: return(0.0,0.0,0.0)
    else: return(iCount/textLength,adjAdvCount/textLength,entityCount/textLength,numCount/textLength,quoteCount/textLength)

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

def readPatternDict(fileName):
    try: dataRoot = ET.parse(fileName).getroot()
    except Exception as e: 
        sys.exit(COMMAND+": cannot read file "+fileName+"; "+str(e))
    dict = {}
    for word in dataRoot:
        dict[word.attrib["form"]] = { \
            "intensity":float(word.attrib["intensity"]), \
            "polarity":float(word.attrib["polarity"]), \
            "subjectivity":float(word.attrib["subjectivity"])}
    return(dict)

def getSentimentScores(text,dictionary):
    intensity = 0.0
    polarity = 0.0
    subjectivity = 0.0
    words = text.lower().split()
    textLength = len(words)
    for word in words:
        if word in dictionary:
            intensity += dictionary[word]["intensity"]
            polarity += dictionary[word]["polarity"]
            subjectivity += dictionary[word]["subjectivity"]
    return(intensity/textLength,polarity/textLength,subjectivity/textLength)

def printData(data):
    dutchTagger = spacy.load("nl")
    patternDict = readPatternDict(PATTERNDICTFILENAME)
    for d in data:
        iFrac,adjAdvFrac,entFrac,numFrac,quoteFrac = \
            getSyntaxCounts(d["text"],dutchTagger) 
        intFrac,polFrac,subjFrac = getSentimentScores(d["text"],patternDict)
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
        for quoteString in getQuoteLabel(quoteFrac):
            print("FTQUOT"+quoteString,end=" ")
        for intString in getIntLabel(intFrac):
            print("FTINTE"+intString,end=" ")
        for polString in getPolLabel(polFrac):
            print("FTPOLA"+polString,end=" ")
        for subjString in getSubjLabel(subjFrac):
            print("FTSUBJ"+subjString,end=" ")
        print(d["text"])

def main(argv):
    data = readFileFromStdin()
    printData(data)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

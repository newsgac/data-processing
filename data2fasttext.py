#!/usr/bin/python3
"""
    data2fasttext.py: convert NEWSGAC data format to fasttext format
    usage: ./data2fasttext.py < file
    notes: expects comma-separated file with fields Genre Identifier Date
    20171120 erikt(at)xs4all.nl
"""

import csv
import html
import nltk
import re
import sys
import time
from datetime import datetime
from pynlpl.clients.frogclient import FrogClient

from io import BytesIO
from urllib.request import urlopen

COMMAND = sys.argv.pop(0)
CACHEDIR = "/home/erikt/projects/newsgac/article-linking/data/cache"
HEADINGDATE = "Datum"
HEADINGGENRE = "Genre"
HEADINGNEWSTYPE = "Aard nieuws"
HEADINGSELFCLASS = "Zelfclassificatie"
HEADINGQUOTES = "Directe quotes"
HEADINGTOPIC = "Onderwerp"
HEADINGAUTHOR = "Soort Auteur"
HEADINGIDENTIFIER = "KB-identifier"
HEADINGNEWSPAPER = "Titel krant"
HEADINGPAGE = "Paginanummer"
INSECUREURL = r"^http:"
LABELLENGTH = 3
LABELPREFIX = "__label__"
SECUREURL = r"https:"
SEPARATOR = ","
URLPREFIX = r"http"
URLSUFFIX = ":ocr"
FROGPORT = 8080

def standardizeDate(dateString):
    if re.search("^\d+-\d+-\d+$",dateString):
        try: date = datetime.strptime(dateString,"%d-%m-%Y")
        except Exception as e: sys.exit(COMMAND+": unexpected date string: "+dateString)
    elif re.search("^\d+/\d+/\d+$",dateString):
        try: date = datetime.strptime(dateString,"%m/%d/%Y")
        except Exception as e: sys.exit(COMMAND+": unexpected date string: "+dateString)
    return(date.strftime("%m/%d/%Y"))

def readFile():
    articles = []
    lineNbr = 0
    csvReader = csv.DictReader(sys.stdin,delimiter=SEPARATOR)
    for row in csvReader:
        lineNbr += 1
        try:
            row[HEADINGDATE] = standardizeDate(row[HEADINGDATE])
            articles.append(row)
        except Exception as e: sys.exit(COMMAND+": missing data on line "+str(lineNbr)+": "+row+": "+str(e))
    return(articles)

def abbreviateName(name): 
    return(name[0:LABELLENGTH].upper())

def urlToFileName(url):
    return(re.sub("^.*=","",url))

def getTextFromCache(url):
    inFileName = urlToFileName(url)
    try:
        text = ""
        inFile = open(CACHEDIR+"/"+inFileName,"r")
        for line in inFile: text += line
        inFile.close()
        return(text)
    except:
        return("")

def storeTextInCache(url,text):
    outFileName = urlToFileName(url)
    try:
        outFile = open(CACHEDIR+"/"+outFileName,"w")
        print(text,file=outFile)
        outFile.close()
    except Exception as e:
        sys.exit(COMMAND+": error writing file "+CACHEDIR+"/"+outFileName)

def readWebPage(url):
    text = getTextFromCache(url)
    if text != "": return(text)
    else:
        try:
            time.sleep(1)
            text = str(urlopen(url,data=None).read(),encoding="utf-8")
            storeTextInCache(url,text)
            return(text)
        except Exception as e:
            print(COMMAND+": problem retrieving url: "+url+" "+str(e),file=sys.stderr)
            return("( geen tekst beschikbaar )")

def removeXML(text):
    text = re.sub(r"<[^<>]*>",r" ",text)
    text = html.unescape(text)
    return(text)

def removeRedundantWhiteSpace(text):
    text = re.sub(r"\s+",r" ",text)
    text = re.sub(r"^\s+",r"",text)
    text = re.sub(r"\s+$",r"",text)
    return(text)

def tokenizeNLTK(text):
    tokenizedSentenceList = nltk.word_tokenize(text)
    tokenizedText = " ".join(tokenizedSentenceList)
    return(tokenizedText)

def tokenizeFROG(text,frogClient):
    resultList = frogClient.process(text)
    resultString = ""
    for x in resultList:
        if x[0] != None:
            if resultString == "": resultString = x[0]
            else: resultString += " "+x[0]
    return(resultString)

def isUrl(url):
    return(re.search(URLPREFIX,url))

def makeUrlSecure(url):
    return(re.sub(INSECUREURL,SECUREURL,url))

def addUrlSuffix(url):
    if not re.search(URLSUFFIX+"$",url): url += URLSUFFIX
    return(url)

def cleanup(text):
    linesIn = text.split("\n")
    linesOut = []
    WORDCHARS = r"a-zA-ZÀ-ÖØ-öø-þ0-9-"
    for line in linesIn:
        wordsIn = line.split()
        wordsOut = []
        for word in wordsIn:
            if re.search(r"["+WORDCHARS+"]",word): 
                word = re.sub(r"(["+WORDCHARS+"])[^"+WORDCHARS+"]+(["+WORDCHARS+"])",r"\1\2",word)
                word = re.sub(r"(["+WORDCHARS+"])[^"+WORDCHARS+"]+(["+WORDCHARS+"])",r"\1\2",word)
                word = re.sub(r"[^"+WORDCHARS+"][^"+WORDCHARS+"][^"+WORDCHARS+"]+",r"",word)
                if len(word) > 0: wordsOut.append(word)
        if len(wordsOut) > 0: linesOut.append(" ".join(wordsOut))
    return("\n".join(linesOut))

def printData(articles):
    cache = {}
    frogClient = FrogClient('localhost',FROGPORT,returnall=True)

    for i in range(0,len(articles)):
        genre = abbreviateName(articles[i][HEADINGGENRE])
        allText = ""
        for url in articles[i][HEADINGIDENTIFIER].rstrip().split():
            if not isUrl(url): 
                sys.exit(COMMAND+": not an url: "+url)
            url = addUrlSuffix(url)
            if url in cache: 
                text = cache[url]
            else:
                text = removeRedundantWhiteSpace(tokenizeFROG(cleanup(removeXML(readWebPage(url))),frogClient))
                cache[url] = text
            if allText == "": allText = text
            else: allText += " "+text
        print(LABELPREFIX+genre,end="")
        print(" DATE="+articles[i][HEADINGDATE],end="")
        print(" NEWSPAPER="+re.sub("\s","_",articles[i][HEADINGNEWSPAPER]),end="")
        print(" PAGE="+articles[i][HEADINGPAGE],end="")
        print(" LENGTH="+str(len(allText)),end="")
        print(" URLS="+re.sub(" ",",",re.sub(":ocr","",articles[i][HEADINGIDENTIFIER])),end="")
        print(" NEWSTYPE="+articles[i][HEADINGNEWSTYPE],end="")
        print(" SELFCLASS="+articles[i][HEADINGSELFCLASS],end="")
        print(" QUOTES="+articles[i][HEADINGQUOTES],end="")
        articles[i][HEADINGTOPIC] = re.sub(r" ","_",articles[i][HEADINGTOPIC])
        print(" TOPIC="+articles[i][HEADINGTOPIC],end="")
        articles[i][HEADINGAUTHOR] = re.sub(r" ","_",articles[i][HEADINGAUTHOR])
        print(" AUTHOR="+articles[i][HEADINGAUTHOR],end="")
        print(" "+allText)

def main(argv):
    articles = readFile()
    printData(articles)
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

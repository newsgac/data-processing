#!/usr/bin/python3
"""
    data2fasttext.py: convert NEWSGAC data format to fasttext format
    usage: ./data2fasttext.py < file
    notes: expects comma-separated file with fields Genre Identifier Date Artikel-ID
    20171120 erikt(at)xs4all.nl
"""

import csv
import html
import nltk
import re
import sys
import time

from io import BytesIO
from urllib.request import urlopen

COMMAND = sys.argv.pop(0)
HEADINGDATE = "Date"
HEADINGGENRE = "Genre"
HEADINGIDENTIFIER = "Artikel-ID"
INDEXDATE = 0
INDEXGENRE = 3
INDEXIDENTIFIER = 5
INSECUREURL = r"^http:"
LABELLENGTH = 3
LABELPREFIX = "__label__"
SECUREURL = r"https:"
SEPARATOR = ","
URLPREFIX = r"http"
URLSUFFIX = ":ocr"

def readFile():
    articles = []
    lineNbr = 0
    csvReader = csv.reader(sys.stdin,delimiter=SEPARATOR)
    next(csvReader)
    for row in csvReader:
        lineNbr += 1
        try:
            date = row[INDEXDATE]
            genre = row[INDEXGENRE]
            identifier = row[INDEXIDENTIFIER]
            for i in range(INDEXIDENTIFIER+1,len(row)):
                if isUrl(row[i]): identifier +=  " "+row[i]
            articles.append({"date":date,"genre":genre,"identifier":identifier})
        except: sys.exit(COMMAND+": missing data on line "+str(lineNbr))
    return(articles)

def abbreviateName(name): 
    return(name[0:LABELLENGTH].upper())

def readWebPage(url):
    time.sleep(1)
    return(str(urlopen(url,data=None).read(),encoding="utf-8"))

def removeXML(text):
    text = re.sub(r"<[^<>]*>",r" ",text)
    text = html.unescape(text)
    return(text)

def removeRedundantWhiteSpace(text):
    text = re.sub(r"\s+",r" ",text)
    text = re.sub(r"^\s+",r"",text)
    text = re.sub(r"\s+$",r"",text)
    return(text)

def tokenize(text):
    tokenizedSentenceList = nltk.word_tokenize(text)
    tokenizedText = " ".join(tokenizedSentenceList)
    return(tokenizedText)

def isUrl(url):
    return(re.search(URLPREFIX,url))

def makeUrlSecure(url):
    return(re.sub(INSECUREURL,SECUREURL,url))

def addUrlSuffix(url):
    if not re.search(URLSUFFIX+"$",url): url += URLSUFFIX
    return(url)

def printData(articles):
    cache = {}
    for i in range(0,len(articles)):
        date = articles[i]["date"]
        genre = abbreviateName(articles[i]["genre"])
        allText = ""
        for url in articles[i]["identifier"].rstrip().split():
            if not isUrl(url): 
                sys.exit(COMMAND+": not an url: "+url)
            url = addUrlSuffix(makeUrlSecure(url))
            if url in cache: 
                    text = cache[url]
            else:
                text = removeRedundantWhiteSpace(tokenize(removeXML(readWebPage(url))))
                cache[url] = text
            if allText == "": allText = text
            else: allText += " "+text
        print(LABELPREFIX+genre+" DATE="+date+" "+allText)

def main(argv):
    articles = readFile()
    printData(articles)
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

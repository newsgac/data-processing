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

from io import BytesIO
from urllib.request import urlopen

COMMAND = sys.argv.pop(0)
HEADINGDATE = "Datum"
HEADINGGENRE = "Genre"
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

def readWebPage(url):
    time.sleep(1)
    try:
        text = str(urlopen(url,data=None).read(),encoding="utf-8")
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
        genre = abbreviateName(articles[i][HEADINGGENRE])
        allText = ""
        for url in articles[i][HEADINGIDENTIFIER].rstrip().split():
            if not isUrl(url): 
                sys.exit(COMMAND+": not an url: "+url)
            url = addUrlSuffix(url)
            if url in cache: 
                    text = cache[url]
            else:
                text = removeRedundantWhiteSpace(tokenize(removeXML(readWebPage(url))))
                cache[url] = text
            if allText == "": allText = text
            else: allText += " "+text
        print(LABELPREFIX+genre,end="")
        print(" DATE="+articles[i][HEADINGDATE],end="")
        print(" NEWSPAPER="+re.sub("\s","_",articles[i][HEADINGNEWSPAPER]),end="")
        print(" PAGE="+articles[i][HEADINGPAGE],end="")
        print(" LENGTH="+str(len(allText)),end="")
        print(" URLS="+re.sub(" ",",",re.sub(":ocr","",articles[i][HEADINGIDENTIFIER])),end="")
        print(" "+allText)

def main(argv):
    articles = readFile()
    printData(articles)
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

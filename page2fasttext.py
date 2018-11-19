#!/usr/bin/python3
"""
    page2fasttext.py: convert KB newspaper page format to fasttext format
    usage: ./page2fasttext.py file
    notes: expects xml file with containing one newspaper page
           based on data2fasttext.py
    20181119 erikt(at)xs4all.nl
"""

import nltk
import re
import sys
from datetime import datetime
import xml.etree.ElementTree as ET

COMMAND = sys.argv.pop(0)
DATEFIELD = 2
DATEPATTERN = "^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$"
LABEL = "__label__UNL"
INSECUREURL = r"^http:"
SECUREURL = r"https:"

def standardizeDate(dateString):
    try: date = datetime.strptime(dateString,"%Y%m%d")
    except Exception as e: sys.exit(COMMAND+": unexpected date string: "+dateString)
    return(date.strftime("%m/%d/%Y"))

def makeUrlSecure(url):
    return(re.sub(INSECUREURL,SECUREURL,url))

def tokenize(text):
    tokenizedSentenceList = nltk.word_tokenize(text)
    tokenizedText = " ".join(tokenizedSentenceList)
    return(tokenizedText)

def getArticles(fileName):
    try: dataRoot = ET.parse(fileName).getroot()
    except: sys.exit(COMMAND+": cannot read file "+fileName)
    articles = []
    for text in dataRoot:
        try: url = makeUrlSecure(text.attrib["id"])
        except: url = "EMPTY-ID!"
        articles.append({"url":url})
        for par in text:
            if not "text" in articles[-1]: articles[-1]["text"] = par.text
            else: articles[-1]["text"] += " "+par.text
    return(articles)

def getDate(fileName):
    fields = fileName.split("/")
    fields = fields[-1].split("-")
    if len(fields) <= DATEFIELD or not re.search(DATEPATTERN,fields[DATEFIELD]):
        sys.exit(COMMAND+": no valid date in file name "+fields[DATEFIELD])
    return(standardizeDate(fields[DATEFIELD]))

def main(argv):
    for fileName in argv:
        date = getDate(fileName)
        articles = getArticles(fileName)
        for art in articles:
            print(art["url"],LABEL,"DATE="+date,tokenize(art["text"]))
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

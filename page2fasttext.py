#!/usr/bin/python3
"""
    page2fasttext.py: convert KB newspaper page format to fasttext format
    usage: ./page2fasttext.py file
    notes: expects xml file with containing one newspaper page
           based on data2fasttext.py
    20181119 erikt(at)xs4all.nl
"""

import gzip
import nltk
import os
import pipes
import random
import re
import sys
from datetime import datetime
import xml.etree.ElementTree as ET
from pynlpl.clients.frogclient import FrogClient

COMMAND = sys.argv.pop(0)
DATEPATTERN = "^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]$"
FROG = "frog"
NLTK = "nltk"
EUROPARL = "europarl"
EUROPARLCOMMAND = "/usr/bin/perl /home/erikt/software/tools/tokenizer.perl -q"
FROGPORT = 8080
INSECUREURL = r"^http:"
LABEL = "__label__UNL"
NLTK = "nltk"
SECUREURL = r"https:"
PARFROG = "-f"
PARNLTK = "-n"
PAREUROPARL = "-e"
TMPFILE = "page2fasttext."+str(os.getpid())+"."+str(int(99999*random.random()))

frogClient = None
tokenizer = NLTK

def standardizeDate(dateString):
    try: date = datetime.strptime(dateString,"%Y%m%d")
    except Exception as e: sys.exit(COMMAND+": unexpected date string: "+dateString)
    return(date.strftime("%m/%d/%Y"))

def makeUrlSecure(url):
    return(re.sub(INSECUREURL,SECUREURL,url))

def tokenizeNLTK(text):
    tokenizedSentenceList = nltk.word_tokenize(text)
    tokenizedText = " ".join(tokenizedSentenceList)
    return(tokenizedText)

def tokenizeFROG(text):
    global frogClient
    resultList = frogClient.process(text)
    resultString = ""
    for x in resultList:
        if x[0] != None:
            if resultString == "": resultString = x[0]
            else: resultString += " "+x[0]
    return(resultString)

def tokenizeEUROPARL(text):
    template = pipes.Template()
    template.append(EUROPARLCOMMAND,"--")
    f = template.open(TMPFILE,"w")
    f.write(text)
    f.close()
    f = open(TMPFILE,"r")
    resultString = f.read()
    f.close()
    os.remove(TMPFILE)
    return(resultString.strip())

def tokenize(text):
    global tokenizer
    if tokenizer == EUROPARL: return(tokenizeEUROPARL(text))
    elif tokenizer == NLTK: return(tokenizeNLTK(text))
    elif tokenizer == FROG: return(tokenizeFROG(text))
    else: sys.exit("cannot happen")

def getArticles(fileName):
    if re.match(r"^.*\.gz$",fileName):
        with gzip.open(fileName,"rb") as f: text = f.read()
        dataRoot = ET.fromstring(text)
    else:
        try: dataRoot = ET.parse(fileName).getroot()
        except: sys.exit(COMMAND+": cannot read file "+fileName)
    articles = []
    for text in dataRoot:
        try: url = makeUrlSecure(text.attrib["id"])
        except: url = "EMPTY-ID!"
        articles.append({"url":url})
        for par in text:
            if par.text != None:
                if not "text" in articles[-1]: articles[-1]["text"] = par.text
                else: articles[-1]["text"] += " "+par.text
        if not "text" in articles[-1]: articles[-1]["text"] = ""
    return(articles)

def getDate(fileDirName):
    fileName = fileDirName.split("/")[-1]
    fileBaseName = fileName.split(".")[0]
    date = fileBaseName.split("-")[-1]
    if not re.search(DATEPATTERN,date):
        sys.exit(COMMAND+": no valid date in file name "+fileDirName+" found: "+date)
    return(standardizeDate(date))

def getNewspaperTitle(fileName):
    fields = fileName.split("/")
    fields = fields[-1].split("-")
    return("-".join(fields[0:-1]))

def main(argv):
    global frogClient,tokenizer
    sys.stdout = open(sys.stdout.fileno(),mode="w",encoding="utf8",buffering=1)
    tokenizer = NLTK
    if len(argv) > 0 and argv[0] == PARNLTK:
        tokenizer = NLTK
        argv.pop(0)
    elif len(argv) > 0 and argv[0] == PARFROG: 
        tokenizer = FROG
        frogClient = FrogClient('localhost',FROGPORT,returnall=True)
        argv.pop(0)
    for fileName in argv:
        date = getDate(fileName)
        articles = getArticles(fileName)
        newspaperTitle = getNewspaperTitle(fileName)
        for art in articles:
            print(art["url"],LABEL,newspaperTitle,"DATE="+date,tokenize(art["text"]),sep="\t")
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

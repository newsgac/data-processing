#!/usr/bin/python3 -W all
"""
    getArticleText.py: retrieve text of all newspaper articles on a page
    usage: getArticleText.py < file
    note: expects db.txt format: tab separated with dates like d-m-y
    20180416 erikt(at)xs4all.nl
"""

import csv
import os
import re
import sys
import time
from urllib.request import urlopen
import xml.etree.ElementTree as ET

ARTICLEURLPATH = "./{http://www.loc.gov/zing/srw/}records/{http://www.loc.gov/zing/srw/}record/{http://www.loc.gov/zing/srw/}recordData/{http://purl.org/dc/elements/1.1/}identifier"
COMMAND = sys.argv.pop(0)
MAXYEAR = 1995
SEPARATOR = "\t"
URLPREFIX = "http://jsru.kb.nl/sru/sru?query=type=artikel+and+page="
URLINFIX1 = "+and+date="
URLINFIX2 = "+and+ppn="
URLPOSTFIX = r"&x-collection=DDD_artikel"

ppns = { "00Algemeen Handelsblad":"400374129", 
         "05NRC Handelsblad":"400367629", 
         "06De Telegraaf":"832675288", 
         "07De Maasbode":"842126635", 
         "08De Volkskrant":"412869594" }

def makeDateId(newspaper,date,pageNbr): 
    return(newspaper+SEPARATOR+date+SEPARATOR+pageNbr)

def splitDateId(date):
    return(date.split(SEPARATOR))

def checkDate(dateId):
    newspaper,date,pageNbr = splitDateId(dateId)
    try: day,month,year = date.split("-")
    except: sys.exit(COMMAND+": error processing date "+date)
    return(int(year) <= MAXYEAR)

def readDBFile():
    dateIds = {}
    csvReader = csv.DictReader(sys.stdin,delimiter=SEPARATOR)
    lineNbr = 0
    for row in csvReader:
        lineNbr += 1
        try: dateId = makeDateId(row["Titel krant"],row["Datum"],row["Paginanummer"])
        except: sys.exit(COMMAND+": missing data on line "+str(lineNbr))
        if checkDate(dateId): dateIds[dateId] = True
    return(dateIds)

def convertDate(date):
    try: day,month,year = date.split("-")
    except: sys.exit(COMMAND+": error processing date "+date)
    if len(day) == 1: day = "0"+day
    if len(month) == 1: month = "0"+month
    return(year+month+day)

def makeUrl(date):
    newspaper,date,pageNbr = splitDateId(date)
    url = URLPREFIX+str(pageNbr)+URLINFIX1+convertDate(date)+URLINFIX2+ppns[newspaper]+URLPOSTFIX
    return(url)

def getUrlData(url):
    print(url)
    time.sleep(1)
    return(str(urlopen(url,data=None).read(),encoding="utf-8"))

def getArticleUrls(dateId):
    url = makeUrl(dateId)
    htmlData = getUrlData(url)
    root = ET.fromstring(htmlData)
    articleUrls = []
    for articleUrl in root.findall(ARTICLEURLPATH):
        articleUrls.append(articleUrl.text)
    return(articleUrls)

def getArticleTexts(articleUrls):
    articleTexts = []
    for articleUrl in articleUrls:
        articleTexts.append(getUrlData(articleUrl))
    return(articleTexts)

def makeFileName(dateId):
    newspaper,date,pageNbr = splitDateId(dateId)
    dateId = makeDateId(newspaper,convertDate(date),pageNbr)
    return(re.sub(r"\s",r"-",dateId)+".xml")

def storeArticleTexts(dateId,articleUrls,articleTexts):
    fileName = makeFileName(dateId)
    with open(fileName,"w") as outFile:
        outFile.write("<container>")
        for i in range(0,len(articleTexts)):
            articleText = re.sub(r"<.xml [^>]*>","",articleTexts[i])
            articleText = re.sub(r"<text>","<text id=\""+articleUrls[i]+"\">",articleText)
            outFile.write(articleText)
        outFile.write("</container>")
        outFile.close()
    return()

def main(argv):
    dateIds = readDBFile()
    print(str(dateIds))
    for dateId in dateIds:
        fileName = makeFileName(dateId)
        if not os.path.isfile(fileName):
            articleUrls = getArticleUrls(dateId)
            articleTexts = getArticleTexts(articleUrls)
            storeArticleTexts(dateId,articleUrls,articleTexts)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

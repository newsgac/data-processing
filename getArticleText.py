#!/usr/bin/python3 -W all
"""
    getArticleText.py: retrieve text of all newspaper articles on a page
    usage: getArticleText.py [newspaper date page] < file
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

ARTICLEBASEPATH = "./{http://www.loc.gov/zing/srw/}records/{http://www.loc.gov/zing/srw/}record/{http://www.loc.gov/zing/srw/}recordData"
ARTICLEURLPATH = "./{http://purl.org/dc/elements/1.1/}identifier"
ARTICLETYPEPATH = "./{http://purl.org/dc/elements/1.1/}type"
ADVERTISEMENT = "advertentie"
ARTICLE = "artikel"
ILLUSTRATION = "illustratie met onderschrift"
COMMAND = sys.argv.pop(0)
MAXYEAR = 1995
MAXRECORDS = 1000
SEPARATOR = "\t"
SOFTWAREDIR = os.path.abspath(os.path.dirname(__file__))
URLPREFIX = "http://jsru.kb.nl/sru"
URLINFIX0 = "?query=date="
URLINFIX1 = "+and+ppn="
URLINFIX2 = "+and+page="
URLPOSTFIX = r"&x-collection=DDD_artikel&maximumRecords="+str(MAXRECORDS)
APIKEYFILENAME = SOFTWAREDIR+"/key-api.txt"
NOWAIT = "NOWAIT"

wait = True
ppns =   { "00Algemeen Handelsblad":"400374129", 
           "05NRC Handelsblad":"400367629", 
           "06De Telegraaf":"832675288", 
           "07De Maasbode":"842126635", 
           "08De Volkskrant":"412869594",
           "Nederlands Dagblad":"810209039",
           "Staatscourant":"400915472",
           "De Tijd":"400383764",
           "Het Vrije Volk":"832737143",
           "De Waarheid":"832737666",
           "Trouw":"412789353"
         }
titles = { "AH":"00Algemeen Handelsblad", 
           "NRC":"05NRC Handelsblad", 
           "Telegraaf":"06De Telegraaf", 
           "Maasbode":"07De Maasbode", 
           "Volkskrant":"08De Volkskrant",
           "ND":"Nederlands Dagblad",
           "Staatscourant":"Staatscourant",
           "Tijd":"De Tijd",
           "HVV":"Het Vrije Volk",
           "Waarheid":"De Waarheid",
           "Trouw":"Trouw"
         }

def readApiKey():
    apiKey = ""
    try:
        apiKeyFile = open(APIKEYFILENAME,"r")
        apiKey = apiKeyFile.readline().strip()
        apiKeyFile.close()
        apiKey = "/" + apiKey
    except: pass
    return(apiKey)

APIKEY = readApiKey()

def makeDatePageId(newspaper,date,pageNbr=None):
    if newspaper in titles: newspaper = titles[newspaper]
    if pageNbr == None: return(newspaper+SEPARATOR+date)
    else: return(newspaper+SEPARATOR+date+SEPARATOR+pageNbr)

def splitDatePageId(date):
    items = date.split(SEPARATOR)
    while len(items) < 3: items.append(None)
    return(items)

def checkDate(datePageId):
    newspaper,date,pageNbr = splitDatePageId(datePageId)
    try: day,month,year = date.split("-")
    except Exception as e: sys.exit(COMMAND+": error processing date "+date+": "+str(e))
    return(int(year) <= MAXYEAR)

def readDBFile():
    datePageIds = {}
    csvReader = csv.DictReader(sys.stdin,delimiter=SEPARATOR)
    lineNbr = 0
    for row in csvReader:
        lineNbr += 1
        try: datePageId = makeDatePageId(row["Titel krant"],row["Datum"],row["Paginanummer"])
        except: sys.exit(COMMAND+": missing data on line "+str(lineNbr))
        if checkDate(datePageId): datePageIds[datePageId] = True
    return(datePageIds)

def convertDate(date):
    try: day,month,year = date.split("-")
    except: sys.exit(COMMAND+": error processing date "+date)
    if len(day) == 1: day = "0"+day
    if len(month) == 1: month = "0"+month
    return(year+month+day)

def makeUrl(date):
    newspaper,date,pageNbr = splitDatePageId(date)
    if newspaper in ppns: newspaper = ppns[newspaper]
    url = URLPREFIX+APIKEY+URLINFIX0+convertDate(date)+URLINFIX1+newspaper
    if pageNbr != None: url += URLINFIX2+str(pageNbr)
    url +=URLPOSTFIX
    return(url)

def getUrlData(url):
    global wait

    #print(url)
    if wait: time.sleep(1)
    try: result = str(urlopen(url,data=None).read(),encoding="utf-8")
    except Exception as e:
        result = "TEXT NOT FOUND!"
        print("cannot open url:",url,file=sys.stderr)
    return(result)

def getArticleUrls(datePageId):
    url = makeUrl(datePageId)
    htmlData = getUrlData(url)
    root = ET.fromstring(htmlData)
    articleUrls = []
    for article in root.findall(ARTICLEBASEPATH):
        for articleUrl in article.findall(ARTICLEURLPATH):
            articleType = article.findall(ARTICLETYPEPATH)[0]
            if articleType.text != ADVERTISEMENT:
                articleUrls.append(articleUrl.text)
    return(articleUrls)

def getArticleTexts(articleUrls):
    articleTexts = []
    for articleUrl in articleUrls:
        articleTexts.append(getUrlData(articleUrl))
    return(articleTexts)

def makeFileName(datePageId):
    newspaper,date,pageNbr = splitDatePageId(datePageId)
    datePageId = makeDatePageId(newspaper,convertDate(date),pageNbr)
    return(re.sub(r"\s",r"-",datePageId)+".xml")

def storeArticleTexts(datePageId,articleUrls,articleTexts):
    fileName = makeFileName(datePageId)
    with open(fileName,"w",encoding="utf8") as outFile:
        outFile.write("<container>")
        for i in range(0,len(articleTexts)):
            articleText = re.sub(r"<.xml [^>]*>","",articleTexts[i])
            articleText = re.sub(r"<text>","<text id=\""+articleUrls[i]+"\">",articleText)
            outFile.write(articleText)
        outFile.write("</container>")
        outFile.close()
    return()

def main(argv):
    global wait

    datePageIds = readDBFile()
    if len(argv) > 0 and argv[0] == NOWAIT:
        wait = False
        argv.pop(0)
    if len(argv) == 2:
        datePageIds[makeDatePageId(argv[0],argv[1])] = True
    elif len(argv) == 3:
        datePageIds[makeDatePageId(argv[0],argv[1],argv[2])] = True
    for datePageId in datePageIds:
        fileName = makeFileName(datePageId)
        if not os.path.isfile(fileName):
            print("Fetching",re.sub(r"\t",r"#",datePageId),"...")
            articleUrls = getArticleUrls(datePageId)
            articleTexts = getArticleTexts(articleUrls)
            storeArticleTexts(datePageId,articleUrls,articleTexts)
        else:
            print(re.sub(r"\t",r"#",datePageId),"is already in the text collection")
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python
"""
    fixPageFeature.py: convert absolute page number to relative value
    usage: python fixPageFeature.py < file
    note: expected line input: label ... DATE=... ... PAGE=...
    20190429 erikt(at)xs4all.nl
"""

import re
import sys

COMMAND = sys.argv.pop(0)
PAGELABELS = [ "PGLBZERO","PGLBONE","PGLBTWO","PGLBTHREE","PGLBFOUR" ]

def readArticles():
    articles = []
    pages = []
    dates = []
    maxPages = {}
    for line in sys.stdin:
        articles.append(line)
        fields = line.split()
        counter = 0
        while len(articles) > len(pages) or len(articles) > len(dates):
            match = re.search("^DATE=(.*)$",fields[counter])
            if match: 
                dates.append(match.group(1))
            match = re.search("^PAGE=(.*)$",fields[counter])
            if match: 
                pages.append(int(match.group(1)))
            counter += 1
            if counter >= len(fields):
                sys.exit(COMMAND+": incomplete line: "+line)
        if not dates[-1] in maxPages or pages[-1] > maxPages[dates[-1]]:
            maxPages[dates[-1]] = pages[-1]
    return(articles,dates,pages,maxPages)

def getGenreLabel(article):
    fields = article.split()
    label = fields.pop(0)
    article = " ".join(fields)
    return(label,article)

def getPageLabels(page,maxPage):
    relativePage = (page-1)/(maxPage-1)
    if relativePage <= 0.25: return(PAGELABELS[0],PAGELABELS[1])
    if relativePage <= 0.50: return(PAGELABELS[1],PAGELABELS[2])
    if relativePage <= 0.75: return(PAGELABELS[2],PAGELABELS[3])
    else: return(PAGELABELS[3],PAGELABELS[4])

def printArticles(articles,dates,pages,maxPages):
    for i in range(0,len(articles)):
        genreLabel,article = getGenreLabel(articles[i])
        pageLabel1,pageLabel2 = getPageLabels(pages[i],maxPages[dates[i]])
        print(genreLabel,pageLabel1,pageLabel2,article)

def main(argv):
    articles,dates,pages,maxPages = readArticles()
    printArticles(articles,dates,pages,maxPages)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

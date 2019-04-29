#!/usr/bin/env python
"""
    addWeekDay.py: add day of the week as feature 
    usage: python addWeekDay < file
    note: expected line input: label ... DATE=...
    20190429 erikt(at)xs4all.nl
"""

import datetime
import re
import sys

COMMAND = sys.argv.pop(0)
WEEKDAYLABELS = [ "WKLBMON","WKLBTUE","WKLBWED","WDLBTHU","WKLBFRI",\
                  "WKLBSAT","WKLBSUN" ]

def readArticles():
    articles = []
    dates = []
    for line in sys.stdin:
        articles.append(line)
        fields = line.split()
        counter = 0
        while len(articles) > len(dates):
            match = re.search("^DATE=(.*)$",fields[counter])
            if match: 
                dates.append(match.group(1))
            counter += 1
            if counter >= len(fields):
                sys.exit(COMMAND+": incomplete line: "+line)
    return(articles,dates)

def getGenreLabel(article):
    fields = article.split()
    label = fields.pop(0)
    article = " ".join(fields)
    return(label,article)

def getWeekDay(date):
    try:
        month,day,year = date.split("/")
        date = datetime.date(int(year),int(month),int(day))
        return(date.weekday())
    except Exception as e:
        sys.exit(COMMAND+": problem processing date: "+date+": "+str(e))

def printArticles(articles,dates):
    for i in range(0,len(articles)):
        genreLabel,article = getGenreLabel(articles[i])
        weekDayId = getWeekDay(dates[i])
        print(genreLabel,WEEKDAYLABELS[weekDayId],article)

def main(argv):
    articles,dates = readArticles()
    printArticles(articles,dates)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

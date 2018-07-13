#!/usr/bin/env python
# csv2tsv.py: convert table from Frank Harbers to data format of linking script
# notes: Frank Harbers tables: frank-LANG.csv for LANG = british dutch french
#        Juliette Lonij's linking software: match.py (reads from file db.txt)
# usage: csv2tsv < file.csv
# 20180713 erikt(at)xs4all.nl

import csv
import sys

SEPARATOR = ","
# field names
ARTICLEID = "Artikel ID"
TITLE = "Titel krant"
DATE = "Datum"
EDITION = "Editie"
PAGE = "Paginanummer"
ENTRYID = "Invoernummer"
SURFACE = "Oppervlakte"
QUOTESHEADING = "Directe quotes in kop"
QUOTES = "Directe quotes"
GENRE = "Genre"
TOPIC = "Onderwerp"
AUTHORTYPE1 = "Soort auteur"
AUTHORTYPE2 = "Soort Auteur"
NBROFIMAGES = "Aantal afbeeldingen"
SURFACEIMAGES = "Oppervlakte afbeeldingen"
KBID = "KB-identifier"
KBIDSOURCE = "KB-identifier-bron"
KBIDCONFIDENCE = "KB-identifier-confidence"
# default values
DEFAULTEDITION = "Middag/avond"
DEFAULTQUOTESHEADING = "FALSE"
DEFAULTNBROFIMAGES = "0"
DEFAULTSURFACEIMAGES = "0"
DEFAULTKBID = ""
DEFAULTKBIDSOURCE = ""
DEFAULTKBIDCONFIDENCE = "0"

COMMAND = sys.argv[0]
HEADING = ARTICLEID+"\t"+TITLE+"\t"+DATE+"\t"+EDITION+"\t"+PAGE+"\t"+ENTRYID+"\t"+SURFACE+"\t"+QUOTESHEADING+"\t"+QUOTES+"\t"+GENRE+"\t"+TOPIC+"\t"+AUTHORTYPE1+"\t"+NBROFIMAGES+"\t"+SURFACEIMAGES+"\t"+KBID+"\t"+KBIDSOURCE+"\t"+KBIDCONFIDENCE

def processDate(date):
    fields = date.split("/")
    if len(fields) != 3: sys.exit(COMMAND+": unexpected date: "+date)
    return(fields[1]+"-"+fields[0]+"-"+fields[2])

def main(argv):
    csvReader = csv.DictReader(sys.stdin,delimiter=SEPARATOR)
    print(HEADING)
    for row in csvReader:
        row[DATE] = processDate(row[DATE])
        print(row[ARTICLEID]+"\t",end="")
        print(row[TITLE]+"\t",end="")
        print(row[DATE]+"\t",end="")
        print(DEFAULTEDITION+"\t",end="")
        print(row[PAGE]+"\t",end="")
        print(row[ENTRYID]+"\t",end="")
        print(row[SURFACE]+"\t",end="")
        print(DEFAULTQUOTESHEADING+"\t",end="")
        print(row[QUOTES]+"\t",end="")
        print(row[GENRE]+"\t",end="")
        print(row[TOPIC]+"\t",end="")
        print(row[AUTHORTYPE2]+"\t",end="")
        print(DEFAULTNBROFIMAGES+"\t",end="")
        print(DEFAULTSURFACEIMAGES+"\t",end="")
        print(DEFAULTKBID+"\t",end="")
        print(DEFAULTKBIDSOURCE+"\t",end="")
        print(DEFAULTKBIDCONFIDENCE)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

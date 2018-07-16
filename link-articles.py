#!/usr/bin/python -W all
# link-articles.py: link meta data to newspaper article texts
# usage: link-articles.py (via cgi)
# 20180706 erikt(at)xs4all.nl

import cgi
import cgitb
import csv
import re
import sys
import xml.etree.ElementTree as ET
 
NEWSPAPERMETA = "05NRC Handelsblad"
NEWSPAPERXML = "00Algemeen-Handelsblad"
PAPERFIELD = "Titel krant"
DATEFIELD = "Datum"
PAGEFIELD = "Paginanummer"
XMLDIR = "/var/www/data"
METADATAFILE = XMLDIR+"/frank-dutch.csv"
SEPARATOR = ","
SCRIPTURL = "http://localhost/cgi-bin/link-articles.py"
SCRIPTTEXT = """
<script>
    //source: https://www.w3schools.com/HTML/html5_draganddrop.asp
    function allowDrop(ev) {
        ev.preventDefault();
    }
    
    function drag(ev) {
        ev.dataTransfer.setData("text", ev.target.id);
    }
    
    function drop(ev) {
        ev.preventDefault();
        var data = ev.dataTransfer.getData("text");
        ev.target.appendChild(document.getElementById(data));
    }
</script>
"""

def readTexts(newspaper,date,page):
    dataOut = []
    xmlFileName = XMLDIR+"/"+newspaper+"-"+date+"-"+page+".xml"
    try: 
        dataRoot = ET.parse(xmlFileName).getroot()
        for text in dataRoot:
            textData = ""
            for paragraph in text: textData += paragraph.text
            utfData = textData.encode("utf-8")
            utfData = re.sub(r'"',"''",utfData)
            dataOut.append(utfData)
        dataOut = sorted(dataOut,key=lambda s: len(s),reverse=True)
    except: pass
    return(dataOut)
 
def readMetaData(newspaper,date,page):
    dataOut = []
    try:
        inFile = open(METADATAFILE,"r")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATOR)
        for row in csvReader:
            if row[PAPERFIELD] == newspaper and \
               row[DATEFIELD] == date and \
               row[PAGEFIELD] == page: dataOut.append(row)
        dataOut = sorted(dataOut,key=lambda r: float(r["Oppervlakte"]),reverse=True)
    except: pass
    return(dataOut)

def printLine(texts,metadata,i):
    print("<tr>")
    if i >= len(metadata): print("<td></td><td></td><td></td><td></td><td>")
    else:
        metadataText = ""
        for key in metadata[i]: metadataText += " "+key+":"+metadata[i][key]
        print("<td>"+metadata[i]["Soort Auteur"])
        print("</td><td>"+metadata[i]["Aard nieuws"])
        print("</td><td>"+metadata[i]["Genre"])
        print("</td><td>"+metadata[i]["Onderwerp"])
        print('</td><td><font title="'+metadataText+'">'+metadata[i]["Oppervlakte"]+"</font>")
    print("</td><td>#")
    print('</td><td id="td'+str(i)+'" ondrop="drop(event)" ondragover="allowDrop(event)"><div id="div'+str(i)+'" draggable="true" ondragstart="drag(event)">')
    if i < len(texts):
        shortText = texts[i][0:80]
        print(str(len(texts[i])))
        print("<font title=\""+texts[i]+"\">"+shortText+"</font>")
    print("</div></td></tr>")
    return()

def printPageLinks(date,page):
    print("<p>")
    if int(page) > 1:
        print("<a href=\""+SCRIPTURL+"?page={0:d}\">Prev</a>".format(int(page)-1))
    print("<a href=\""+SCRIPTURL+"?page={0:d}\">Next</a>".format(int(page)+1))
    return()

def printData(newspaper,date,page,texts,metadata):
    maxIndex = max(len(texts),len(metadata))
    printPageLinks(date,page)
    print("<h2>"+newspaper+" "+date+" page "+page+"</h2>")
    print("<table>")
    print("<tr><td><strong>Author</strong></td><td><strong>Type of news</strong></td><td><strong>Genre</strong></td><td><strong>Topic</strong></td><td><strong>Surface</strong></td><td></td><td><strong>Chars Text</strong></td></tr>")
    for i in range(0,maxIndex): printLine(texts,metadata,i)
    printLine(texts,metadata,maxIndex)
    print("</table>")
    return()

def main(argv):
    print("Content-Type: text/html\n")
    print("<html><head>"+SCRIPTTEXT+"</head><body>")
    cgitb.enable()
    cgiData = cgi.FieldStorage()
    year = str(1965)
    pageNbr = 1
    if cgiData.has_key("page"): pageNbr = cgiData["page"].value
    month = str(12)
    day = str(4)
    pageNbr = str(pageNbr)
    newspaper = NEWSPAPERMETA
    date = month+"/"+day+"/"+year
    metaData = readMetaData(newspaper,date,pageNbr)
    newspaper = NEWSPAPERXML
    if len(month) < 2: month = "0"+month
    if len(day) < 2: day = "0"+day
    date = year+month+day
    texts = readTexts(newspaper,date,pageNbr)
    printData(newspaper,date,pageNbr,texts,metaData)
    print("</body></html>")
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))


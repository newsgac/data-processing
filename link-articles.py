#!/usr/local//bin/python3 -W all
# link-articles.py: link meta data to newspaper article texts
# usage: link-articles.py (via cgi)
# 20180706 erikt(at)xs4all.nl

import cgi
import cgitb
import codecs
import csv
import os
import pwd
import re
import sys
import xml.etree.ElementTree as ET
 
COMMAND = sys.argv[0]
YEAR = 1965
MONTH = 1
DAY = 2
NEWSPAPERMETA = "05NRC Handelsblad"
NEWSPAPERXML = "00Algemeen-Handelsblad"
PAPERFIELD = "Titel krant"
DATEFIELD = "Datum"
PAGEFIELD = "Paginanummer"
IDFIELD = "Artikel ID"
KBIDFIELD = "KB-identifier"
XMLDIR = "/home/erikt/projects/newsgac/article-linking/data"
OCRSUFFIX = ":ocr"
METADATAFILE = XMLDIR+"/frank-dutch.csv"
PREANNOTATEDFILE = XMLDIR+"/db.txt.org"
ANNOTATIONSFILE = XMLDIR+"/annotations.tsv"
SEPARATORCOMMA = ","
SEPARATORTAB = "\t"
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
        var dropTarget = ev.target
        while (dropTarget.tagName != "TD") {
            dropTarget = dropTarget.parentElement
        }
        dropTarget.appendChild(document.getElementById(data));
    }

    function submitLine(el) {
        trElement = el.parentElement.parentElement;
        tdElements = trElement.children;
        for (var i = 0; i < tdElements.length; i++) {
            if (tdElements[i].id != "") {
                divElements = tdElements[i].children;
                textIds = ""
                for (var j = 0; j < divElements.length; j++) {
                    if (divElements[j].id != "") {
                        if (textIds == "") {
                            textIds = divElements[j].id;
                        } else {
                            textIds += " "+divElements[j].id;
                        }
                    }
                }
                if (textIds != "") {
                    form = document.forms["saveAnnotation"];
                    form.elements["textId"].value = textIds;
                    form.elements["metadataId"].value = tdElements[i].id.slice(2);
                    form.submit()
                    trElement.style.backgroundColor = "lightblue"
                }
            }
        }
    }
</script>
"""

def readTexts(newspaper,date,page):
    texts = []
    xmlFileName = XMLDIR+"/"+newspaper+"-"+date+"-"+page+".xml"
    try: 
        dataRoot = ET.parse(xmlFileName).getroot()
        for text in dataRoot:
            textData = ""
            for paragraph in text: 
                textData += paragraph.text + " "
            textData = re.sub(r'"',"''",textData)
            texts.append({"text":textData,"id":text.attrib["id"]})
        texts = sorted(texts,key=lambda s: len(s["text"]),reverse=True)
    except: pass
    return(texts)
 
def readMetaData(newspaper,date,page):
    dataOut = []
    try:
        inFile = open(METADATAFILE,"r",encoding="utf-8")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORCOMMA)
        for row in csvReader:
            if row[PAPERFIELD] == newspaper and \
               row[DATEFIELD] == date and \
               row[PAGEFIELD] == page: dataOut.append(row)
        dataOut = sorted(dataOut,key=lambda r: float(r["Oppervlakte"]),reverse=True)
        inFile.close()
    except: pass
    return(dataOut)

def readAnnotations(fileName,preAnnotated):
    annotated = list(preAnnotated)
    try: 
        inFile = open(fileName,"r",encoding="utf-8")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORTAB)
        for row in csvReader:
            if KBIDFIELD in row and IDFIELD in row and row[KBIDFIELD] != "":
                annotated.append({"metadataId":row[IDFIELD],"textIds":row[KBIDFIELD]})
        inFile.close()
    except: sys.exit(COMMAND+": error processing file "+fileName)
    return(annotated)
 
def printLine(texts,metadata,annotated,metadataIndex):
    annotatedKeys = {}
    for i in range(0,len(annotated)): 
        annotatedKeys[annotated[i]["metadataId"]] = True
    if metadataIndex >= len(metadata): 
        print("<td id=\""+str(metadataIndex)+"\"></td><td></td><td></td><td></td><td>")
        print("</td><td><div onclick=\"submitLine(this)\">#</div>")
        print('</td><td id="td'+str(metadataIndex)+'" ondrop="drop(event)" ondragover="allowDrop(event)">')
    else:
        if not metadata[metadataIndex][IDFIELD] in annotatedKeys or len(texts[metadataIndex]) == 0: print("<tr>")
        else: print("<tr style=\"background-color:lightblue;\">")
        metadataText = ""
        for key in metadata[metadataIndex]: metadataText += " "+key+":"+metadata[metadataIndex][key]
        print("<td>"+metadata[metadataIndex]["Soort Auteur"])
        print("</td><td>"+metadata[metadataIndex]["Aard nieuws"])
        print("</td><td>"+metadata[metadataIndex]["Genre"])
        print("</td><td>"+metadata[metadataIndex]["Onderwerp"])
        print('</td><td><font title="'+metadataText+'">'+metadata[metadataIndex]["Oppervlakte"]+"</font>")
        print("</td><td><div onclick=\"submitLine(this)\">#</div>")
        print('</td><td id="td'+metadata[metadataIndex][IDFIELD]+'" ondrop="drop(event)" ondragover="allowDrop(event)">')
    if metadataIndex < len(texts) and len(texts[metadataIndex]) > 0:
        for text in texts[metadataIndex]:
            shortText = text["text"][0:80]
            print('<div id="'+text["id"]+'" draggable="true" ondragstart="drag(event)">')
            print(str(len(text["text"])))
            print("<font title=\""+str(text["text"])+"\">"+str(shortText)+"</font>")
            print("</div>")
    print("</td></tr>")
    return()

def printPageLinks(date,page):
    print("<p>")
    if int(page) == 1: print("Prev")
    else: print("<a href=\""+SCRIPTURL+"?page={0:d}\">Prev</a>".format(int(page)-1))
    print("<a href=\""+SCRIPTURL+"?page={0:d}\">Next</a>".format(int(page)+1))
    return()

def reorderTexts(metadata,texts,annotated):
    for i in range(0,len(texts)): texts[i] = [texts[i]]
    for i in range(len(texts),len(metadata)):
        texts.append([])
    metadataKeys = {}
    for i in range(0,len(metadata)): metadataKeys[metadata[i][IDFIELD]] = i
    for i in range(0,len(annotated)):
        metadataKey = annotated[i]["metadataId"]
        if metadataKey in metadataKeys:
            metadataIndex = metadataKeys[metadataKey]
            textIds = annotated[i]["textIds"]
            targetIds = textIds.split(" ")
            for j in range(0,len(texts)):
                for k in range(0,len(texts[j])):
                    if metadataIndex != j and targetIds[0] == texts[j][k]["id"]:
                        if len(texts[metadataIndex]) > 0 and len(texts[metadataIndex][0]) > 0:
                            texts[j].extend(texts[metadataIndex])
                        texts[metadataIndex] = [texts[j][k]]
                        texts[j] = texts[j][0:k]+texts[j][k+1:]
                        break
            for t in range(1,len(targetIds)):
                for j in range(0,len(texts)):
                    for k in range(0,len(texts[j])):
                        if metadataIndex != j and targetIds[t] == texts[j][k]["id"]:
                            texts[metadataIndex].append(texts[j][k])
                            texts[j] = texts[j][0:k]+texts[j][k+1:]
                            break
    return(texts)

def printData(newspaper,date,page,texts,metadata,annotated):
    maxIndex = max(len(texts),len(metadata))
    print("<h2>"+newspaper+" "+date+" page "+page+"</h2>")
    print("<table>")
    print("<tr><td><strong>Author</strong></td><td><strong>Type of news</strong></td><td><strong>Genre</strong></td><td><strong>Topic</strong></td><td><strong>Surface</strong></td><td></td><td><strong>Chars Text</strong></td></tr>")
    texts = reorderTexts(metadata,texts,annotated)
    for i in range(0,maxIndex): 
        printLine(texts,metadata,annotated,i)
    printLine(texts,metadata,annotated,i+1)
    print("</table>")
    return()

def storeAnnotations(metadataId,textId):
    try:
        outFile = open(ANNOTATIONSFILE,"a")
        outFile.write(str(metadataId)+SEPARATORTAB+str(textId)+"\n")
        outFile.close()
    except:
        sys.exit(COMMAND+": problem processing file "+ANNOTATIONSFILE)
    return()

def main(argv):
    # make sure stdout accepts utf data
    sys.stdout = open(sys.stdout.fileno(),mode="w",encoding="utf-8",buffering=1)
    cgitb.enable(logdir="/tmp")
    cgiData = cgi.FieldStorage()
    print("Content-Type: text/html\n")
    print("<html><head>"+SCRIPTTEXT+"</head><body>")
    print("""
<form id="saveAnnotation" action="/cgi-bin/link-articles.py" method="post">
<input type="hidden" name="textId">
<input type="hidden" name="metadataId">
""")
    if "textId" in cgiData and "metadataId" in cgiData:
        storeAnnotations(cgiData["metadataId"].value,cgiData["textId"].value)
    annotated = readAnnotations(PREANNOTATEDFILE,[])
    annotated = readAnnotations(ANNOTATIONSFILE,annotated)
    year = str(YEAR)
    pageNbr = 1
    if "page" in cgiData: pageNbr = cgiData["page"].value
    print('<input type="hidden" name="page" value="'+str(pageNbr)+'">\n</form>')
    month = str(MONTH)
    day = str(DAY)
    pageNbr = str(pageNbr)
    newspaper = NEWSPAPERMETA
    date = month+"/"+day+"/"+year
    metadata = readMetaData(newspaper,date,pageNbr)
    newspaper = NEWSPAPERXML
    if len(month) < 2: month = "0"+month
    if len(day) < 2: day = "0"+day
    date = year+month+day
    texts = readTexts(newspaper,date,pageNbr)
    printPageLinks(date,pageNbr)
    if len(texts) > 0: 
        printData(newspaper,date,pageNbr,texts,metadata,annotated)
    else: print("<p>\nNo newspaper text found (metadata: "+str(len(metadata))+")\n")
    print("</body>\n</html>")
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

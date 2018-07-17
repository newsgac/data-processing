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
XMLDIR = "/var/www/data"
METADATAFILE = XMLDIR+"/frank-dutch.csv"
PREANNOTATEDFILE = XMLDIR+"/db.txt.org"
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
        ev.target.appendChild(document.getElementById(data));
        // document.getElementById(data).id
        // ev.target.id)
    }

    function submitLine(el) {
        trElement = el.parentElement.parentElement;
        tdElements = trElement.children;
        for (var i = 0; i < tdElements.length; i++) {
            if (tdElements[i].id != "") {
                divElements = tdElements[i].children;
                for (var j = 0; j < divElements.length; j++) {
                    if (divElements[j].id != "") {
                        alert(tdElements[i].id.slice(2)+" "+divElements[j].id)
                    }
                }
                trElement.style.backgroundColor = "lightgreen"
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
            for paragraph in text: textData += paragraph.text+" "
            utfData = textData.encode("utf-8")
            utfData = re.sub(r'"',"''",utfData)
            texts.append({"text":utfData,"id":text.attrib["id"]})
        texts = sorted(texts,key=lambda s: len(s["text"]),reverse=True)
    except: pass
    return(texts)
 
def readMetaData(newspaper,date,page):
    dataOut = []
    try:
        inFile = open(METADATAFILE,"r")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORCOMMA)
        for row in csvReader:
            if row[PAPERFIELD] == newspaper and \
               row[DATEFIELD] == date and \
               row[PAGEFIELD] == page: dataOut.append(row)
        dataOut = sorted(dataOut,key=lambda r: float(r["Oppervlakte"]),reverse=True)
        inFile.close()
    except: pass
    return(dataOut)

def readPreannotated():
    dataOut = {}
    try: 
        inFile = open(PREANNOTATEDFILE,"r")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORTAB)
        for row in csvReader:
            if row[KBIDFIELD] != "":
                dataOut[row[IDFIELD]] = row[KBIDFIELD]
        inFile.close()
    except: sys.exit(COMMAND+": error processing file "+PREANNOTATEDFILE)
    return(dataOut)
 
def printLine(text,metadata,textId,metaDataId,preAnnotated):
    if metadata == None: 
        print("<td id=\""+metaDataId+"\"></td><td></td><td></td><td></td><td>")
    else:
        if not metadata[IDFIELD] in preAnnotated: print("<tr>")
        else: print("<tr style=\"background-color:lightblue;\">")
        metadataText = ""
        for key in metadata: metadataText += " "+key+":"+metadata[key]
        # print("<td>"+metadata[IDFIELD])
        print("<td>"+metadata["Soort Auteur"])
        print("</td><td>"+metadata["Aard nieuws"])
        print("</td><td>"+metadata["Genre"])
        print("</td><td>"+metadata["Onderwerp"])
        print('</td><td><font title="'+metadataText+'">'+metadata["Oppervlakte"]+"</font>")
    print("</td><td><div onclick=\"submitLine(this)\">#</div>")
    print('</td><td id="td'+metaDataId+'" ondrop="drop(event)" ondragover="allowDrop(event)"><div id="'+textId+'" draggable="true" ondragstart="drag(event)">')
    if text != None:
        shortText = text[0:80]
        print(str(len(text)))
        print("<font title=\""+text+"\">"+shortText+"</font>")
    print("</div></td></tr>")
    return()

def printPageLinks(date,page):
    print("<p>")
    if int(page) > 1:
        print("<a href=\""+SCRIPTURL+"?page={0:d}\">Prev</a>".format(int(page)-1))
    print("<a href=\""+SCRIPTURL+"?page={0:d}\">Next</a>".format(int(page)+1))
    return()

def reorderTexts(metadata,texts,preAnnotated):
    for i in range(0,len(metadata)):
        if metadata[i][IDFIELD] in preAnnotated:
            for j in range(0,len(texts)):
                if i != j and \
                   preAnnotated[metadata[i][IDFIELD]]+":ocr" == texts[j]["id"]:
                    # print("SWAPPING "+str(i)+" "+str(j)+" "+texts[j]["id"])
                    texts[i],texts[j] = texts[j],texts[i]
    return(texts)

def printData(newspaper,date,page,texts,metadata,preAnnotated):
    maxIndex = max(len(texts),len(metadata))
    printPageLinks(date,page)
    print("<h2>"+newspaper+" "+date+" page "+page+"</h2>")
    print("<table>")
    print("<tr><td><strong>Author</strong></td><td><strong>Type of news</strong></td><td><strong>Genre</strong></td><td><strong>Topic</strong></td><td><strong>Surface</strong></td><td></td><td><strong>Chars Text</strong></td></tr>")
    texts = reorderTexts(metadata,texts,preAnnotated)
    for i in range(0,maxIndex): 
        if i < len(texts): 
            text = texts[i]["text"]
            textId = texts[i]["id"]
        else: 
            text = None
            textId = "div"+str(i)
        if i < len(metadata): 
            metadatum = metadata[i]
            metaDataId = metadatum[IDFIELD]
        else: 
            metadatum = None
            metaDataId = str(i)
        printLine(text,metadatum,textId,metaDataId,preAnnotated)
    printLine(None,None,"div"+str(maxIndex),str(maxIndex),preAnnotated)
    print("</table>")
    return()

def main(argv):
    print("Content-Type: text/html\n")
    print("<html><head>"+SCRIPTTEXT+"</head><body>")
    preAnnotated = readPreannotated()
    cgitb.enable()
    cgiData = cgi.FieldStorage()
    year = str(YEAR)
    pageNbr = 1
    if cgiData.has_key("page"): pageNbr = cgiData["page"].value
    month = str(MONTH)
    day = str(DAY)
    pageNbr = str(pageNbr)
    newspaper = NEWSPAPERMETA
    date = month+"/"+day+"/"+year
    metaData = readMetaData(newspaper,date,pageNbr)
    newspaper = NEWSPAPERXML
    if len(month) < 2: month = "0"+month
    if len(day) < 2: day = "0"+day
    date = year+month+day
    texts = readTexts(newspaper,date,pageNbr)
    printData(newspaper,date,pageNbr,texts,metaData,preAnnotated)
    print("""
<form id="saveAnnotation" action="/cgi-bin/link-articles.py" method="post">
</form>
</body>
</html>")
    sys.exit(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))


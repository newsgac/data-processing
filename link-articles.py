#!/usr/bin/env python3
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
NEWSPAPER = "telegraaf"
DATE = "1/2/1965"
PAPERFIELD = "Titel krant"
DATEFIELD = "Datum"
PAGEFIELD = "Paginanummer"
GENREFIELD = "Genre"
IDFIELD = "Artikel ID"
KBIDFIELD = "KB-identifier"
IDENTIFIERFIELD = "Identifier"
TEXTIDSFIELD = "textIds"
XMLDIR = "/home/erikt/projects/newsgac/article-linking/data"
OCRSUFFIX = ":ocr"
METADATAFILE = XMLDIR+"/frank-dutch.csv"
PREANNOTATEDFILE = XMLDIR+"/db.txt.org"
ANNOTATIONSFILE = XMLDIR+"/annotations.tsv"
SEPARATORCOMMA = ","
SEPARATORTAB = "\t"
SCRIPTNAME = sys.argv[0].split("/")[-1]
SCRIPTURL = "http://localhost/cgi-bin/"+SCRIPTNAME
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
        children = dropTarget.childNodes;
        for (var i=0;i<children.length;i++) {
            if (children[i].id == "metadataId") {
                dropTarget.removeChild(children[i]); 
            }
        }
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
                form = document.forms["saveAnnotation1"];
                form.elements["textId"].value = textIds;
                form.elements["metadataId"].value = tdElements[i].id.slice(2);
                form.submit()
                trElement.style.backgroundColor = "lightblue"
            }
        }
    }
</script>
"""

def decodeDate(date):
    try:
        month,day,year = date.split("/")
        return(year,month,day)
    except Exception as e:
        sys.exit(COMMAND+": error decoding date: "+date)

def readTexts(newspaper,date,page):
    texts = []
    xmlFileName = XMLDIR+"/"+newspaper+"-"+date+"-"+page+".xml"
    try: 
        dataRoot = ET.parse(xmlFileName).getroot()
        for text in dataRoot:
            textData = ""
            for paragraph in text:
                if type(paragraph.text) == type("string"):
                    textData += paragraph.text + " "
            textData = re.sub(r'"',"''",textData)
            texts.append({"text":textData,"id":text.attrib["id"]})
        texts = sorted(texts,key=lambda s: s["id"])
    except: 
        print("<p><font style=\"color:red\">Failed while reading file: "+xmlFileName+"</font>")
    return(texts)
 
def readMetaDataByKey(lastKey):
    try:
        inFile = open(METADATAFILE,"r",encoding="utf-8")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORCOMMA,quotechar='"')
        for row in csvReader:
            if row[IDFIELD] == lastKey:
                return(row[PAPERFIELD],row[DATEFIELD],row[PAGEFIELD])
        inFile.close()
        return(NEWSPAPER,DATE,"1")
    except Exception as e:
        sys.exit(COMMAND+": error processing file "+METADATAFILE+": "+str(e))

def readMetaDataByPage(newspaper,date,page):
    try:
        dataOut = []
        maxPages = {}
        inFile = open(METADATAFILE,"r",encoding="utf-8")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORCOMMA,quotechar='"')
        for row in csvReader:
            if row[PAPERFIELD] == newspaper:
                if row[DATEFIELD] == date:
                    if row[PAGEFIELD] == page: 
                        dataOut.append(row)
                    if not date in maxPages or \
                       int(row[PAGEFIELD]) > maxPages[date]:
                        maxPages[date] = int(row[PAGEFIELD])
        dataOut = sorted(dataOut,key=lambda r: float(r["Invoernummer"]))
        inFile.close()
        return(dataOut,maxPages)
    except Exception as e:
        sys.exit(COMMAND+": error processing file "+METADATAFILE+": "+str(e))

def readMetaDataIds(ids):
    dataOut = {}
    try:
        inFile = open(METADATAFILE,"r",encoding="utf-8")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORCOMMA)
        for row in csvReader:
            if row[IDFIELD] in ids: dataOut[row[IDFIELD]] = row
        inFile.close()
    except: pass
    return(dataOut)

def makeReverse(annotated):
    reverse = {}
    for thisKey in annotated:
        for textId in annotated[thisKey]["textIds"].split():
            if textId in reverse:
                print("<p><font style=\"color:red;\">error: duplicate key "+thisKey)
            reverse[textId] = thisKey
    return(reverse)

def removeLink(annotated,reverse,textId):
    thisKey = reverse[textId]
    textIds = annotated[thisKey][TEXTIDSFIELD].split()
    index = textIds.index(textId)
    textIds.pop(index)
    del(reverse[textId])
    if len(textIds) > 0:
        annotated[thisKey][TEXTIDSFIELD] = " ".join(textIds)
    else:
        del(annotated[thisKey])
    return(annotated,reverse)

def readAnnotations(fileName,preAnnotated):
    annotated = dict(preAnnotated)
    reverse = makeReverse(annotated)
    lastKey = ""
    try:
        inFile = open(fileName,"r",encoding="utf-8")
        csvReader = csv.DictReader(inFile,delimiter=SEPARATORTAB)
        for row in csvReader:
            if IDFIELD in row:
                thisKey = row[IDFIELD]
                lastKey = thisKey
                if KBIDFIELD in row: textIds = row[KBIDFIELD]
                else: textIds = ""
                for textId in textIds.split():
                    if textId in reverse: annotated,reverse = removeLink(annotated,reverse,textId)
                if thisKey in annotated:
                    for textId in annotated[thisKey][TEXTIDSFIELD].split():
                        annotated,reverse = removeLink(annotated,reverse,textId) 
                for textId in textIds.split(): reverse[textId] = thisKey
                if textIds != "": 
                    annotated[thisKey] = {TEXTIDSFIELD:textIds}
        inFile.close()
    except Exception as e: 
        sys.exit(COMMAND+": error processing file "+fileName+": "+str(e))
    return(annotated,lastKey)
 
def printText(text):
    shortText = text["text"][0:80]
    longText = text["text"][0:800]+" ### "+text["text"][-800:]
    thisId = text["id"].split(":")[4]
    print('<div id="'+text["id"]+'" draggable="true" ondragstart="drag(event)">')
    print("<font title=\""+longText+"\">")
    print(str(len(text["text"])),thisId)
    print("</font>",str(shortText))
    print("</div>")
    return()

def printLine(texts,metadata,annotated,metadataIndex):
    if metadataIndex >= len(metadata): 
        print("<tr><td id=\""+str(metadataIndex)+"\"></td><td></td><td></td><td></td><td></td><td>")
        print("</td><td><div onclick=\"submitLine(this)\">#</div>")
        print('</td><td id="td'+str(metadataIndex)+'" ondrop="drop(event)" ondragover="allowDrop(event)">')
    else:
        if not metadata[metadataIndex][IDFIELD] in annotated: print("<tr>")
        else: print("<tr style=\"background-color:lightblue;\">")
        metadataText = ""
        for key in metadata[metadataIndex]: metadataText += " "+key+":"+metadata[metadataIndex][key]
        print("<td>"+metadata[metadataIndex]["Soort Auteur"])
        print("</td><td>"+metadata[metadataIndex]["Aard nieuws"])
        metadata[metadataIndex]["Genre"] = re.sub(r"/"," ",metadata[metadataIndex]["Genre"])
        print("</td><td>"+metadata[metadataIndex]["Genre"])
        print("</td><td>"+metadata[metadataIndex]["Onderwerp"])
        print("</td><td>"+metadata[metadataIndex]["Invoernummer"])
        print('</td><td><font title="'+metadataText+'">'+metadata[metadataIndex]["Oppervlakte"]+"</font>")
        print("</td><td><div onclick=\"submitLine(this)\">#</div>")
        print('</td><td id="td'+metadata[metadataIndex][IDFIELD]+'" ondrop="drop(event)" ondragover="allowDrop(event)">')
    if metadataIndex < len(texts) or \
       (metadataIndex < len(metadata) and metadata[metadataIndex][IDFIELD] in annotated):
        if metadataIndex < len(metadata) and metadata[metadataIndex][IDFIELD] in annotated:
            for link in annotated[metadata[metadataIndex][IDFIELD]][TEXTIDSFIELD].split():
                textId = -1
                for i in range(0,len(texts[metadataIndex])):
                    if texts[metadataIndex][i]["id"] == link: textId = i
                if textId >= 0: printText(texts[metadataIndex][textId])
                else: print("<a href=\""+link+"\">"+link+"</a> ")
        else:
            if len(texts[metadataIndex]) > 0:
                for text in texts[metadataIndex]: printText(text)
            elif metadataIndex < len(metadata):
                print("<div id=\"metadataId\"><font style=\"color:grey\">"+metadata[metadataIndex]["Artikel ID"]+"</font></div>")

    print("</td></tr>")
    return()

def moveIds(texts,targetIds,metadataIndex):
    for t in range(0,len(targetIds)):
        for j in range(0,len(texts)):
            for k in range(0,len(texts[j])):
                if metadataIndex != j and targetIds[t] == texts[j][k]["id"]:
                    if t == 0 and len(texts[metadataIndex]) > 0 and len(texts[metadataIndex][0]) > 0:
                        texts[j].extend(texts[metadataIndex])
                    texts[metadataIndex].append(texts[j][k])
                    texts[j] = texts[j][0:k] + texts[j][k+1:]
                    break
    return(texts)

def reorderTexts(metadata,texts,annotated):
    for i in range(0,len(texts)): texts[i] = [texts[i]]
    for i in range(len(texts),len(metadata)):
        texts.append([])
    metadataKeys = {}
    for i in range(0,len(metadata)): metadataKeys[metadata[i][IDFIELD]] = i
    for metadataKey in annotated:
        if metadataKey in metadataKeys:
            metadataIndex = metadataKeys[metadataKey]
            textIds = annotated[metadataKey]["textIds"]
            targetIds = textIds.split(" ")
            #texts = moveIds(texts,targetIds,metadataIndex)
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
    metadataIds = {}
    for i in range(0,len(texts)):
        for j in range(0,len(texts[i])):
            thisId = texts[i][j]["id"].split(":")[-2]
            metadataIds[thisId] = i
    sortedTextIds = sorted(metadataIds.keys())
    blockedIds = {}
    for i in range(1,len(sortedTextIds)):
        thisTextId = sortedTextIds[i]
        lastTextId = sortedTextIds[i-1]
        metadataId = metadataIds[thisTextId]
        nextMetadataId = metadataIds[lastTextId]+1
        if (metadataId >= len(metadata) or not metadata[metadataId][IDFIELD] in annotated) and \
           (nextMetadataId >= len(metadata) or not metadata[nextMetadataId][IDFIELD] in annotated) and \
           nextMetadataId <= len(texts) and not nextMetadataId in blockedIds:
            if nextMetadataId == len(texts): texts.append([])
            texts[nextMetadataId],texts[metadataId] = texts[metadataId],texts[nextMetadataId]
            swappedMetadataIds = False
            for j in range(0,len(sortedTextIds)):
                if metadataIds[sortedTextIds[j]] == nextMetadataId:
                    metadataIds[sortedTextIds[j]],metadataIds[thisTextId] = \
                        metadataIds[thisTextId],metadataIds[sortedTextIds[j]]
                    swappedMetadataIds = True
                    break
            if not swappedMetadataIds: metadataIds[thisTextId] = nextMetadataId
            blockedIds[nextMetadataId] = True
    for i in range(1,len(sortedTextIds)):
        thisTextId = sortedTextIds[i]
        metadataId = int(metadataIds[thisTextId])
        if metadataId >= len(metadata) or not metadata[metadataId][IDFIELD] in annotated:
            nextMetadataId = int(metadataId)
            while nextMetadataId > 0 and not nextMetadataId-1 in metadataIds.values(): nextMetadataId -= 1
            if nextMetadataId < metadataId:
                texts[nextMetadataId], texts[metadataId] = texts[metadataId], texts[nextMetadataId]
                metadataIds[thisTextId] = nextMetadataId
    return(texts)

def convertDate(date):
    year = date[0:4]
    month = str(int(date[4:6]))
    day = str(int(date[6:8]))
    dateSlash = month+"/"+day+"/"+year
    return(dateSlash)

def printData(newspaper,date,page,texts,metadata,annotated,maxPages):
    dateSlash = convertDate(date)
    print("<h2>"+newspaper+" "+date+" page "+page+"/"+str(maxPages[dateSlash])+"</h2>")
    print("<table>")
    print("<tr><td><strong>Author</strong></td><td><strong>Type of news</strong></td><td><strong>Genre</strong></td><td><strong>Topic</strong></td><td><strong>Nr</strong><td><strong>Surface</strong></td><td></td><td><strong>Chars Id Text</strong></td></tr>")
    texts = reorderTexts(metadata,texts,annotated)
    maxIndex = max(len(texts),len(metadata))
    for i in range(0,maxIndex):
        if i < len(metadata) or len(texts[i]) > 0:
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

def printAnnotated(annotated):
    metadata = readMetaDataIds(annotated)
    csvwriter = csv.DictWriter(sys.stdout,fieldnames=[IDFIELD,DATEFIELD,GENREFIELD,IDENTIFIERFIELD])
    csvwriter.writeheader()
    for thisKey in annotated:
        csvwriter.writerow({IDFIELD:thisKey,DATEFIELD:metadata[thisKey][DATEFIELD],GENREFIELD:metadata[thisKey][GENREFIELD],IDENTIFIERFIELD:annotated[thisKey]["textIds"]})
    sys.exit(0)

def main(argv):
    cgitb.enable(logdir="/tmp")
    cgiData = cgi.FieldStorage()
    if "textId" in cgiData and "metadataId" in cgiData:
        storeAnnotations(cgiData["metadataId"].value,cgiData["textId"].value)
    elif "metadataId" in cgiData:
        storeAnnotations(cgiData["metadataId"].value,"")
    annotated,lastKey = readAnnotations(PREANNOTATEDFILE,{})
    annotated,lastKey = readAnnotations(ANNOTATIONSFILE,annotated)
    lastNewspaper,lastDate,lastPageNbr = readMetaDataByKey(lastKey)
    if len(argv) > 1: printAnnotated(annotated)

    # make sure stdout accepts utf data
    sys.stdout = open(sys.stdout.fileno(),mode="w",encoding="utf-8",buffering=1)
    print("Content-Type: text/html\n")
    print("<html><head>"+SCRIPTTEXT+"</head><body>")

    newspaper = lastNewspaper
    if "newspaper" in cgiData: newspaper = cgiData["newspaper"].value.lower()
    if newspaper == "volkskrant" or newspaper == "08De Volkskrant":
        newspaper = "volkskrant"
        NEWSPAPERMETA = "08De Volkskrant"
        NEWSPAPERXML1965 = "08De-Volkskrant"
        NEWSPAPERXML1985 = "08De-Volkskrant"
    elif newspaper == "nrc" or newspaper == "05NRC Handelsblad":
        newspaper = "nrc"
        NEWSPAPERMETA = "05NRC Handelsblad"
        NEWSPAPERXML1965 = "00Algemeen-Handelsblad"
        NEWSPAPERXML1985 = "05NRC-Handelsblad"
    elif newspaper == "telegraaf" or newspaper == "06De Telegraaf":
        newspaper = "telegraaf"
        NEWSPAPERMETA = "06De Telegraaf"
        NEWSPAPERXML1965 = "06De-Telegraaf"
        NEWSPAPERXML1985 = "06De-Telegraaf"
    else: sys.exit("unknown newspaper")

    year,month,day = decodeDate(lastDate)
    if "year" in cgiData: year = cgiData["year"].value
    if "month" in cgiData: month = cgiData["month"].value
    if "day" in cgiData: day = cgiData["day"].value
    pageNbr = lastPageNbr
    if "page" in cgiData:
        if "prev" in cgiData: pageNbr = str(int(cgiData["page"].value)-1)
        elif "next" in cgiData: pageNbr = str(int(cgiData["page"].value)+1)
        else: pageNbr = cgiData["page"].value
    offset = 0
    if "offset" in cgiData: offset = int(cgiData["offset"].value)
    print("""
<form id="saveAnnotation1" action="/cgi-bin/link-articles.py" method="put">
<input type="hidden" name="textId">
<input type="hidden" name="metadataId">
""")
    print('<input type="hidden" name="year" size="5" value="'+str(year)+'">')
    print('<input type="hidden" name="month" size="5" value="'+str(month)+'">')
    print('<input type="hidden" name="day" size="5" value="'+str(day)+'">')
    print('<input type="hidden" name="page" value="'+str(pageNbr)+'">')
    print('<input type="hidden" name="offset" value="'+str(offset)+'">\n</form>')
    print("""
<form id="saveAnnotation2" action="/cgi-bin/link-articles.py" method="put">
""")
    print('Newspaper: <input type="newspaper" size="7" name="newspaper" value="'+str(newspaper)+'">')
    print('Year: <input type="text" name="year" size="5" value="'+str(year)+'">')
    print('Month: <input type="text" name="month" size="2" value="'+str(month)+'">')
    print('Day: <input type="text" name="day" size="2" value="'+str(day)+'">')
    print('Page: <input type="text" name="page" size="2" value="'+str(pageNbr)+'">')
    print('Offset: <input type="text" name="offset" size="1" value="'+str(offset)+'">')
    print('<input type="submit" name="submit" value="submit">')
    print('<input type="submit" name="prev" value="prev">')
    print('<input type="submit" name="next" value="next">\n</form>')
    pageNbr = str(pageNbr)
    newspaper = NEWSPAPERMETA
    date = month+"/"+day+"/"+year
    metadata,maxPages = readMetaDataByPage(newspaper,date,pageNbr)
    if year == "1965": newspaper = NEWSPAPERXML1965
    else: newspaper = NEWSPAPERXML1985
    if len(month) < 2: month = "0"+month
    if len(day) < 2: day = "0"+day
    date = year+month+day
    texts = readTexts(newspaper,date,str(int(pageNbr)+offset))
    if len(texts) > 0 or len(metadata) > 0: 
        printData(newspaper,date,pageNbr,texts,metadata,annotated,maxPages)
    else: print("<p>\nNo newspaper text found (metadata: "+str(len(metadata))+")\n")
    print("</body>\n</html>")
    sys.stdout.close()

if __name__ == "__main__":
    sys.exit(main(sys.argv))

#!/usr/bin/env python3
"""
    removeQuotedText.py: remover text between quotes from text
    usage: removeQuotedText.py < file.txt
    20181127 erikt(at)xs4all.nl
"""

import re
import sys

QUOTE = "QUOTE"
OPENQUOTE = "„"
CLOSEQUOTE = '"'
UNSEENQUOTE = -1

def process(line):
    if not re.search(OPENQUOTE,line) or not re.search(CLOSEQUOTE,line): 
        return(line)
    words = line.split()
    lastOpenQuote = UNSEENQUOTE
    for i in range(0,len(words)):
        if words[i] == OPENQUOTE: lastOpenQuote = i
        elif words[i] == CLOSEQUOTE and lastOpenQuote != UNSEENQUOTE:
            for j in range(lastOpenQuote+1,i): words[j] += QUOTE
            lastOpenQuote = UNSEENQUOTE
    line = " ".join(words)
    return(line)

def main(argv):
    for line in sys.stdin:
        line = line.strip()
        print(process(line))

if __name__ == "__main__":
    sys.exit(main(sys.argv))

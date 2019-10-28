#!/usr/bin/env python3
"""
    tokenizeNLTK.py: tokenize lines of text
    usage: python3  tokenizeNLTK.py < file.in > file.out
    note: assumes input file contains one paragraph per line
    20191028 erikt(at)xs4all.nl
"""

import nltk
import sys

def main(argv):
    for line in sys.stdin:
        sentences = nltk.sent_tokenize(line.strip())
        tokenizedLine = ""
        for s in sentences:
            tokenizedS = nltk.word_tokenize(s)
            if tokenizedLine == "": tokenizedLine = " ".join(tokenizedS)
            else: tokenizedLine += " "+" ".join(tokenizedS)
        print(tokenizedLine)
    return(0)

if __name__ == "__main__":
    sys.exit(main(sys.argv))

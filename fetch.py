from urllib2 import urlopen
from flask import Flask, jsonify
from pytube import YouTube
from xml.etree import ElementTree
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from sets import Set

import os
import sys
import numpy
import math
import json
import subprocess
import re

entities = {}

app = Flask(__name__)

@app.route("/")
def main():
    print "Main page hit"
    return jsonify(status="ok")

# Get video captions
@app.route("/captions/<id>")
def processCaptions(id=None):
    video_url = "https://www.youtube.com/watch?v=" + id
    # navigate to path
    path = "/Users/mukul/Dropbox/RPI/Fall 2016/Natural Language Processing/Term Project/Project/captions"
    os.chdir(path)
    # get captions in srt
    f = os.popen("youtube-dl --list-subs --skip-download --output " + "'" + id + ".%(ext)s' " + video_url)
    info = f.read()
    print info
    searchObj = re.search(r'(no subtitles)', info, re.M|re.I)
    if searchObj:
        return jsonify(downloaded = False)
    else:
        os.system("youtube-dl --write-srt --sub-lang en --skip-download --output " + "'" + id + ".%(ext)s' " + video_url)
        return jsonify(downloaded = True)

# Extract named entities
@app.route("/ner/<id>")
def extractNamedEntities(id=None):
    st = StanfordNERTagger('/Users/mukul/NLP/stanford-ner-2015-12-09/classifiers/english.muc.7class.distsim.crf.ser.gz',
					       '/Users/mukul/NLP/stanford-ner-2015-12-09/stanford-ner.jar',
                           encoding='utf-8')

    completed = 0
    # Decode each line to utf-8 into one string.
    lines_str = ""
    for line in open("captions/" + id + ".en.vtt", 'r'):
        if line != '\n' and line[0] != '0':
            lines_str += line.decode('utf-8').rstrip() + " "

    # Create an array of sentences.
    sents = lines_str.split(".")

    # Groups 5 sentences together and extract the named entities.
    text = ""
    i = 0
    texts = []
    # while i < 10:
    while i < len(sents) - 5:
        s = " "
        seq = (sents[i].rstrip() + '.', sents[i + 1].rstrip() + '.', sents[i + 2].rstrip() + '.', sents[i + 3].rstrip() + '.', sents[i + 4].rstrip() + '.')
        text = s.join(seq)
        texts.append(text)
        i += 5

    for text in texts:

        tokenized_text = word_tokenize(text)
        classified_text = st.tag(tokenized_text)
        completed += 5
        print float(completed)/float(len(sents)) * 100
        j = 0
        while j < len(classified_text):
            category = classified_text[j][1]
            if category != 'O':
                word = ""
                while classified_text[j][1] != 'O' and classified_text[j][1] == category:
                    word += classified_text[j][0] + " "
                    j += 1

                word = word.strip()

                if category not in entities:
                    entities[category] = [word]
                else:
                    if word not in entities[category]:
                        entities[category].append(word)
            else:
                j += 1

    return jsonify(entities)



if __name__ == "__main__":
    app.run(host="localhost", port=int("8000"), threaded=True)

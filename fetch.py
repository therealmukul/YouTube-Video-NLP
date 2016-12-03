from urllib2 import urlopen
from flask import Flask, jsonify
from pytube import YouTube
from xml.etree import ElementTree
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from sets import Set
from textblob import TextBlob

import os
import sys
import numpy
import math
import json
import subprocess
import re
import operator
import re
import datetime



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
    entities = {}
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
    while i < 50:
    # while i < len(sents) - 5:
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
                    entities[category] = {}
                    entities[category][word] = 1
                else:
                    if word not in entities[category]:
                        entities[category][word] = 1
                    else:
                        entities[category][word] += 1
            else:
                j += 1

    # Sort the values in each cateory by frequency
    for category in entities:
        sort_list = sorted(entities[category].items(), key=lambda x: x[1], reverse=True)
        top = []
        for item in sort_list:
            top.append(item[0])
        entities[category]["TOP"] = top

    print "NER Complete"
    return jsonify(entities)

@app.route('/sentiment/<id>')
def sentiment(id=None):


    chunks = []
    chunk = []
    for line in open("captions/" + id + ".en.vtt", 'r'):
        if line != '\n':
            line = line.decode('utf-8').strip()
            chunk.append(line)
        else:
            chunks.append(chunk)
            chunk = []

    sentiments = {}
    for chunk in chunks:
        time = chunk[0]
        time_range = time.split('-->')

        if len(time_range) > 1:

            start = time_range[0].strip()
            end = time_range[1].strip()

            h1, m1, s1 = re.split(':', start)
            h2, m2, s2 = re.split(':', end)

            start_int = int(datetime.timedelta(hours=int(h1),minutes=int(m1),seconds=float(s1)).total_seconds())
            end_int = int(datetime.timedelta(hours=int(h2),minutes=int(m2),seconds=float(s2)).total_seconds())

            print start_int, end_int

            for i in xrange(1, len(chunk)):
                text = TextBlob(chunk[i])
                if time not in sentiments:
                    senti = text.sentiment.polarity
                    sentiments[time] = {}
                    sentiments[time]["start"] = start_int
                    sentiments[time]["end"] = end_int
                    sentiments[time]["sentiment"] = senti

    return jsonify(sentiments)

if __name__ == "__main__":
    app.run(host="localhost", port=int("8000"), threaded=True)

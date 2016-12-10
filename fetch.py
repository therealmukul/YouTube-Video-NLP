from urllib2 import urlopen
from flask import Flask, jsonify
from pytube import YouTube
from xml.etree import ElementTree
from nltk.tag import StanfordNERTagger
from nltk.tokenize import word_tokenize
from sets import Set
from textblob import TextBlob
from OpenSSL import SSL
from datetime import timedelta
from flask import Flask, make_response, request, current_app
from functools import update_wrapper

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

context = ('/Users/mukul/SSL.crt', '/Users/mukul/SSL.key')

app = Flask(__name__)

def crossdomain(origin=None, methods=None, headers=None, max_age=21600, attach_to_all=True, automatic_options=True):
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, basestring):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, basestring):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator


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
        entities[category]["TOP"] = top[0:5]

    print "NER Complete"
    return jsonify(entities)

@app.route('/sentiment/<id>')
@crossdomain(origin='*')
def sentiment(id=None):
    chunks = []
    chunk = []
    negative_words = []
    positive_words = []

    for line in open("captions/" + id + ".en.vtt", 'r'):
        if line != '\n':
            line = line.decode('utf-8').strip()
            chunk.append(line)
        else:
            chunks.append(chunk)
            chunk = []

    for word in open('negativewords.txt', 'r'):
        negative_words.append(word.rstrip())
    for word in open('positivewords.txt', 'r'):
        positive_words.append(word.rstrip())

    sentiments = []
    times = Set()

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

            for i in xrange(1, len(chunk)):
                # if time not in times:
                text = TextBlob(chunk[i])
                senti = text.sentiment.polarity
                words = (chunk[i].lower()).split()

                for word in words:
                    # print word
                    word = re.sub("[\.\t\,\:;\(\)\.]", "", word, 0, 0)
                    if word in positive_words:
                        print "pos", word
                        senti += 0.2
                    elif word in negative_words:
                        print "neg", word
                        senti += -0.2

                sentiments.append([start_int, end_int, senti])
                times.add(time)

    print "Sentiment Analysis Complete"
    return jsonify(sentiments)

if __name__ == "__main__":
    app.run(host='localhost', port=int("8000"), threaded=True, ssl_context=context)

#! /usr/bin/env python3

import string
import sys
from os import system, execl, listdir, path
from resources import helper
import speech_recognition as sr
import re
import multiprocessing
import webbrowser
import requests
import spacy
from bs4 import BeautifulSoup
from krystal import Detector, EXECUTABLE
import logging
from conversation import response
from uni import UNKNOWNFACEFILES, SAVEDFACES

# needs
logging.basicConfig(filename='commands.log', format='%(levelname)s:%(asctime)s:%(message)s', level=logging.DEBUG)
r = sr.Recognizer()
FOUNDIT = True
stop = 0
hold = []
nlp = spacy.load('en')


def restart():
    execl(EXECUTABLE, 'Krystal', __file__, *sys.argv[1:])


def backhome():
    sys.stdout.write('Background Enabled\n')
    Detector()


def startmic():
    with sr.Microphone() as ausource:
        num = 0
        try:
            sys.stdout.write('Listening...\n')
            audio = r.listen(source=ausource)
            user = r.recognize_wit(audio, key='CGTT3OA7XGQCF3HOB2J4GBISOIXBUAZR')
            logging.info(user)
            print('Audio Captured: {}\n'.format(user))
            # usersanitized = re.sub(r'[?|$.,!]', r'', user)
            KrystalCommands(user)
        except sr.UnknownValueError:
            sys.stdout.write("I didn't catch that.")
        except sr.RequestError as e:
            conv = str(e)
            sys.stdout.write(conv + '\n' + "Sorry I didn't catch that. One more time?\n")
            num += 1
            if num > 2:
                sys.stdout.write('Too many request errors. Restarting.')
                restart()
            startmic()


def is_word_character(c):
    return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9' or c == '_'


def word_count(sentence):
    c = 0
    for i in range(1, len(sentence)):
        if not is_word_character(sentence[i]) and is_word_character(sentence[i-1]):
            c += 1
    if is_word_character(sentence[-1]):
        c += 1
    if c != 250:
        c = 250
    return c


def KrystalCommands(word):
    res = response.response(word)
    try:
        for sx in helper.specialrequests:
            if sx == word:
                specialRequests(sx)
                return

        for gx in helper.startrequests:
            if word.startswith(gx):
                searchExecution(gx, word[6:])
                return

        for ox in helper.requestoptions:
            if ox in word:
                word_option = word.index(ox)
                word_len = len(ox)
                combo = word_option + word_len
                after_word = word[combo:]
                if ox in helper.requestoptions and not after_word.startswith('your'):
                    searchExecution(ox, after_word)
                else:
                    vocalfeedback(res)
                    return
    except ValueError:
        vocalfeedback('Encountered an error')
    finally:
        backhome()


def specialRequests(phrase):
    if phrase == helper.specialrequests[0]:
        from resources import vision
        vision_snap = multiprocessing.Process(name='vision_snapshot', target=vision.snapshot())
        vision_snap.daemon = True
        vision_snap.start()
        for img_path in listdir(UNKNOWNFACEFILES):
            preds = vision.predict(path.join(UNKNOWNFACEFILES, img_path), model_save_path=SAVEDFACES)
            name = ''.join(preds).title()
            vocalfeedback(name)
    if phrase == helper.specialrequests[1]:
        from resources import Detection
        det_thread = multiprocessing.Process(name='detection', target=Detection.Detection())
        det_thread.daemon = True
        det_thread.start()
    backhome()
    return


def searchExecution(param, option):
    if param == 'open ':
        upper = string.capwords(option)
        openresults = 'Opening ' + upper
        vocalfeedback(openresults)
        system('open -a /Applications/{}.app'.format(upper))
    elif param in helper.requestoptions[1:3] or param in helper.startrequests:
        nospace = re.sub(r"\s+", '+', option)
        searchresults = 'Searching Google for ' + option
        vocalfeedback(searchresults)
        finalstringrequest = 'https://www.google.com/search?q=' + nospace + '&ie=UTF-8'
        webbrowser.open(finalstringrequest)
    elif param in helper.requestoptions[4:8]:
        conv = param + option
        nospace = re.sub(r"\s+", '+', conv)
        finalstringrequest = 'https://www.google.com/search?q=' + nospace
        page = requests.get(finalstringrequest)
        tree = BeautifulSoup(page.text, 'lxml')
        data = [page.text for page in tree.find_all("span", class_="st")]
        temp = ''.join(data)
        removefp = temp.find('(')
        if removefp:
            removelp = temp.find(')')
            withoutp = temp.replace(temp[removefp:removelp], '')
            doc = nlp(withoutp)
            doc_sentence = list(doc.sents)[0]
            vocalfeedback(doc_sentence)
        else:
            doc = nlp(temp)
            doc_sentence = list(doc.sents)[0]
            vocalfeedback(doc_sentence)
    backhome()
    return


def vocalfeedback(phrase):
    # print(textwrap.wrap(phrase, 40) + '\n')
    try:
        sys.stdout.write(phrase)
    except TypeError:
        print(phrase + '\n')
    system('say -v Ava -r 195 "{}"'.format(phrase))
    return


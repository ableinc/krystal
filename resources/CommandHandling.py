#! /usr/bin/env python3

import logging
import multiprocessing
import sys
from datetime import datetime
from os import system, execl, listdir, path

import requests
import spacy
import speech_recognition as sr

from conversation import response
from engine import language_engine
from krystal import Detector, EXECUTABLE
from resources import helper
from uni import UNKNOWNFACEFILES, SAVEDFACES, COMMANDURL

# needs
AI = language_engine.LanguageEngine()
logging.basicConfig(filename='commands.log', format='%(levelname)s:%(asctime)s:%(message)s', level=logging.DEBUG)
r = sr.Recognizer()
FOUNDIT = True
stop = 0
hold = []
nlp = spacy.load('en')


def restart():
    execl(EXECUTABLE, 'Krystal', __file__, *sys.argv[1:])


def backhome():
    print('Background Enabled\n')
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
            if num > 1:
                sys.stdout.write('Too many request errors.')
                return
            startmic()


def KrystalCommands(word):
    res = response.response(word)
    try:
        if word == helper.specialrequests[0]:
            specialRequests(whos_that=True)
        elif word == helper.specialrequests[1]:
            specialRequests(whats_that=True)

        for gx in helper.startrequests or helper.defaultrequests:
            if word.startswith(gx):
                paramlen = len(gx)
                AI.DetailClassifier(gx, ''.join(word[paramlen:]))
            else:
                whole = word.index(gx) + len(gx)
                removed_whole = word[whole:]
                AI.DetailClassifier(gx, removed_whole)
                # searchExecution(gx, word[paramlen:])
                # sendinfo(gx, word[paramlen:])
            decision = AI.DetailClassifier.basic_legacy_operations
            vocalfeedback(decision)

        for ox in helper.uniquerequests:
            if ox in word:
                whole = word.index(ox) + len(ox)
                sub_whole = word[whole:]
                if not sub_whole.startswith('your'):
                    AI.DetailClassifier(ox, word[sub_whole:])
                    # searchExecution(ox, sub_whole)
                    # sendinfo(ox, sub_whole)
                else:
                    vocalfeedback(res)
    except ValueError:
        vocalfeedback('Encountered an error')
    finally:
        backhome()
        return


def specialRequests(whos_that=False, whats_that=False):
    if whos_that is True:
        from resources import vision
        vision_snap = multiprocessing.Process(name='vision_snapshot', target=vision.snapshot())
        vision_snap.daemon = True
        vision_snap.start()
        for img_path in listdir(UNKNOWNFACEFILES):
            preds = vision.predict(path.join(UNKNOWNFACEFILES, img_path), model_save_path=SAVEDFACES)
            name = ''.join(preds).title()
            vocalfeedback(name)
    if whats_that is True:
        from resources import Detection
        det_thread = multiprocessing.Process(name='detection', target=Detection.Detection())
        det_thread.daemon = True
        det_thread.start()
    backhome()
    return


# def searchExecution(param, option):
#     if param == 'open ':
#         upper = string.capwords(option)
#         openresults = 'Opening ' + upper
#         vocalfeedback(openresults)
#     elif param in helper.defaultrequests or helper.startrequests:
#         searchresults = 'Searching Google for ' + option
#         webbrowser.open_new(finalstringrequest)
#         vocalfeedback(searchresults)
#     elif param in helper.uniquerequests:
#         # combination = param + option
#         information = AI.DetailClassifier(param, option)
#         information.isanoun('detect')
#         resource = AI.InformationHandler()
#         output = ''.join(resource.search_engine())
#         vocalfeedback(output)
#     backhome()
#     return


def sendinfo(opt, cmd):
    cur_date = datetime.now().strftime('%Y-%m-%d')
    params = dict(
        date=cur_date,
        option=opt,
        command=cmd
    )
    resp = requests.get(url=COMMANDURL, params=params)
    if resp:
        resp.close()
        return


def vocalfeedback(phrase):
    # print(textwrap.wrap(phrase, 40) + '\n')
    try:
        sys.stdout.write(phrase)
    except TypeError:
        print(phrase)
        print('\n')
    system('say -v Ava -r 195 "{}"'.format(phrase))
    return


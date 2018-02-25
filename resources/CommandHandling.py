#! /usr/bin/env python3
# python specific
import logging
import multiprocessing
import sys
from os import system, execl, listdir, path

import speech_recognition as sr

# krystal
from conversation import response
from engine.operations.language_engine import LanguageEngine
from krystal import Detector, EXECUTABLE
from resources.helper import specialrequests, defaultrequests, uniquerequests, startrequests
from uni import TEST_FACES_DIR, FACES_MODEL

# initialize
r = sr.Recognizer()
FOUNDIT = True
stop = 0
hold = []


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


def KrystalCommands(sentence):
    AI = LanguageEngine()
    new_info_handler = AI.InformationHandler()
    res = response.response(sentence)
    try:
        if sentence == specialrequests[0]:
            specialRequests(whos_that=True)
        elif sentence == specialrequests[1]:
            specialRequests(whats_that=True)

        for phrase in startrequests, defaultrequests, uniquerequests:
            if phrase in sentence:
                sub = sentence.index(phrase) + len(phrase)
                removed_sub = sentence[sub:]
                if not removed_sub.startswith('your'):
                    classify = AI.DetailClassifier(phrase, removed_sub)
                    classify.isanoun()
                    legacy = classify.basic_legacy_operations()
                    vocalfeedback(legacy)
                else:
                    new_info_handler.search_engine()
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
        for img_path in listdir(TEST_FACES_DIR):
            preds = vision.predict(path.join(TEST_FACES_DIR, img_path), model_save_path=FACES_MODEL)
            name = ''.join(preds).title()
            vocalfeedback(name)
    if whats_that is True:
        from resources import Detection
        det_thread = multiprocessing.Process(name='detection', target=Detection.Detection())
        det_thread.daemon = True
        det_thread.start()
    backhome()
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


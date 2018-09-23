#! /usr/bin/env python3
# python specific
import logging
import multiprocessing
import sys
from os import system, execl, listdir, path
import speech_recognition as sr
import webbrowser
# krystal
from conversation import response
from engine.operations import LanguageEngine
from krystal import Detector, EXECUTABLE, returner
from resources.helper import ALL_REQUEST_OPTIONS, preferences
from uni import TEST_FACES_DIR, FACES_MODEL, EVENT_LOG, accessURL

# initialize
r = sr.Recognizer()
FOUNDIT = True
stop = 0
hold = []
logging.basicConfig(filename=EVENT_LOG, format='%(asctime)s:%(levelname)s:%(name)s - %(message)s', level=logging.INFO)
log_events = logging.getLogger('CommandHandling')


def restart():
    execl(EXECUTABLE, 'Krystal', __file__, *sys.argv[1:])


def backhome():
    print('\nBackground Enabled\n')
    Detector()


def startmic():
    with sr.Microphone() as ausource:
        num = 0
        try:
            sys.stdout.write('Listening...\n')
            audio = r.listen(source=ausource)
            user = r.recognize_wit(audio, key='CGTT3OA7XGQCF3HOB2J4GBISOIXBUAZR')
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
    return


def KrystalCommands(sentence):
    res = response.response(sentence)
    try:
        if sentence == ALL_REQUEST_OPTIONS[0]:
            specialRequests(whos_that=True)
        elif sentence == ALL_REQUEST_OPTIONS[1]:
            specialRequests(whats_that=True)
        elif sentence == preferences[0] or sentence == preferences[1]:
            vocalfeedback('Enable these features on Able Digital Access')
            returner(sentence, 'Enable these features on Able Digital Access')
            webbrowser.open_new(accessURL)
        for i in range(len(ALL_REQUEST_OPTIONS[1:])):
            phrase = ALL_REQUEST_OPTIONS[i]
            if phrase in sentence:
                length_of_phrase = sentence.index(phrase) + len(phrase)
                string_after_phrase = sentence[length_of_phrase:]
                # phrase, string_after_phrase
                if not string_after_phrase.startswith('your'):
                    krystalReponse = LanguageEngine.LanguageEngine(words=sentence)
                    vocalfeedback(krystalReponse)
                    returner(userStatement=sentence, krystalStatement=krystalReponse)
                else:
                    vocalfeedback(res)
                break
    except ValueError as ve:
        vocalfeedback('Encountered an error')
        log_events.error(ve)
    except TypeError as te:
        log_events.error(te)
    finally:
        backhome()


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


def vocalfeedback(phrase, speed=''):
    # print(textwrap.wrap(phrase, 40) + '\n')
    try:
        sys.stdout.write(phrase)
    except TypeError:
        print(phrase)
        print('\n')
    system('say -v Ava -r 195 "{}"'.format(phrase))
    return


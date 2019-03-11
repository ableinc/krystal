#! /usr/bin/env python3
import logging
import multiprocessing
import sys
import webbrowser
from os import listdir, path
from threading import Thread

import speech_recognition as sr

from conversation import response
from engine.operations import LanguageEngine, AssistantEngine
from resources.speech import speech_recognizer
from resources.verbal_feedback import verbal_feedback
from resources.vocab import available_request_commands, statement_types
from root import TEST_FACES_DIR, FACES_MODEL, EVENT_LOG, Endpoints

# initialize
r = sr.Recognizer()
logging.basicConfig(filename=EVENT_LOG, format='%(asctime)s:%(levelname)s:%(name)s - %(message)s', level=logging.INFO)
log_events = logging.getLogger('CommandHandling')


def command_handler(test: bool = False, args: tuple = None):
    if test and args is not None:
        t = Thread(target=process_available_commands, args=args)
        t.daemon = False
        t.start()
        return True
    sentence, str_concat = capture_request_deepspeech()
    t = Thread(target=process_available_commands, args=(sentence, str_concat))
    t.daemon = False
    t.start()
    return True


def capture_request_wit():
    request = ''
    with sr.Microphone() as ausource:
        try:
            audio = r.listen(source=ausource)
            user_statement = r.recognize_wit(audio, key='CGTT3OA7XGQCF3HOB2J4GBISOIXBUAZR')
            request = user_statement
        except sr.UnknownValueError:
            sys.stdout.write("I didn't catch that.")
        except sr.RequestError as e:
            log_events.debug(e)
            request = 'Sorry, I could not handle your request.'
        finally:
            return request


def capture_request_deepspeech():
    request = speech_recognizer()
    return process_request_text(request)


def determine_statement_type(statement):
    for key in statement_types.keys():
        for prefix in statement_types[key]:
            if statement.startswith(prefix):
                return key


def process_request_text(txt):
    if 'krystal' in txt: txt = txt.replace('krystal', '')
    txt2list = txt.split()
    result = None
    try:
        for word in range(len(txt2list)):
            for key in available_request_commands.keys():
                if txt2list[word] == key and type(available_request_commands[key]) == dict:
                    str_concat = available_request_commands[key].get(txt2list[word + 1], None)
                    result = txt, str_concat
                    break
                elif txt2list[word] == key and type(available_request_commands[key] == str):
                    str_concat = available_request_commands[key]
                    result = txt, str_concat
                    break
                else:
                    result = txt, '{0}'
            break
    except TypeError:
        result = 'NoneValueType', 'NoneValueType'
    finally:
        print(f'RESULT: {result}')
        return result


def process_available_commands(request, string_concat):
    txt_type = determine_statement_type(request)
    message = ''
    try:
        if request == 'NoneValueType':
            raise TypeError
        elif request.startswith('who is that'):
            msg = special_requests(whos_that=True)
            message = string_concat.format(msg)
        elif request.startswith('what is that'):
            msg = special_requests(whats_that=True)
            message = string_concat.format(msg)
        elif request.startswith('sign in'):
            message = 'Enable these features on Able Digital Access. Opening browser.'
            webbrowser.open_new(Endpoints.access_url.value)
        elif request.startswith('search') or request.startswith('google'):
            search_param = request[request.find('for'):]
            AssistantEngine.AssistantOperations('search', search_param)
            message = string_concat.format(search_param)
        elif request.startswith('open'):
            application = request[request.find('open'):]
            AssistantEngine.AssistantOperations('open', application)
            message = string_concat.format(application)
        elif request != '':
            res = response.response(request)
            message = string_concat.format(res)
        else:
            message = "Sorry, I can't help at the moment."
    except ValueError as ve:
        message = 'Sorry, something went wrong.'
        log_events.error(ve)
    except TypeError as te:
        log_events.error(te)
        message = 'Sorry, I cannot help with that request.'
    except AttributeError as ae:
        log_events.error(ae)
        print(f'Attribute error in Command Handling: {ae}')
        pass
    finally:
        print(f'Statement type: {str(txt_type).title()}')
        verbal_feedback(message, vocal_speed=195)
        print('Sending information to Language Engine')
        LanguageEngine.LanguageEngine(request)


def special_requests(whos_that=False, whats_that=False):
    if whos_that is True:
        from resources import vision
        vision_snap = multiprocessing.Process(name='vision_snapshot', target=vision.snapshot())
        vision_snap.daemon = True
        vision_snap.start()
        for img_path in listdir(TEST_FACES_DIR):
            preds = vision.predict(path.join(TEST_FACES_DIR, img_path), model_save_path=FACES_MODEL)
            name = ''.join(preds).title()
            return name
    if whats_that is True:
        return 'FEATURE OFFLINE'

#! /usr/bin/env python3
# from setuptools.command.easy_install import main as install
# install(['tensorflow', 'pyaudio', 'spacy', 'opencv-python', 'face_recognition', 'speechrecognition', 'tflearn', 'beautifulsoup'])

from SBpy3 import snowboydecoder
import signal
from uni import MODEL, CONFIGJSON, APIURL, UPDATEURL
from os import system
import sys
import json
import logging
import time
import socket
import requests
from pathlib import Path
from datetime import datetime

# Start-ups
logging.basicConfig()
logger = logging.getLogger('Able - Krystal')
logger.setLevel(logging.INFO)
IPADDR = socket.gethostbyname(socket.gethostname())
EXECUTABLE = sys.executable

Welcome = "\nThank you for unpacking me!\nI'm starting to get comfy but...\nI don't really know much about you.\n" \
          "Soooo, first thing first,\nif you're registered at AbleInc.us go ahead\nand enter your " \
          "AbleAccess ID.\n"

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


def Detector():
    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    detector = snowboydecoder.HotwordDetector(MODEL, sensitivity=0.5)

    # main loop
    detector.start(detected_callback=snowboydecoder.play_audio_file,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)

    # detector.terminate()
    # print('detector terminated')


def update():
    sys.stdout.write('Checking Able for updates...')
    cur_date = datetime.now().strftime('%Y-%m-%d')
    params = dict(
        date=cur_date
    )
    resp = requests.get(url=UPDATEURL, params=params)
    data = json.loads(resp.text)
    vi = data['krystal'][0]['current_version']['versionid']
    nm = data['krystal'][0]['current_version']['name']
    url = data['krystal'][0]['current_version']['url']
    if data:
        sys.stdout.write("Current Version: {}\n".format(zip(nm, vi, url)))
    sys.stdout.write('Updates done.')
    return True


class KrystalStartup():
    def __init__(self):
        FreshStart = Path(CONFIGJSON)
        if FreshStart.is_file():
            with open(CONFIGJSON, 'r') as userdata:
                data = json.load(userdata)
                name = data['name']
                key = data['accessID']
                if key and name:
                    KrystalStartup.hello(self, name)
                    userdata.close()
                    Detector()
                    userdata.close()
                else:
                    logger.debug('Invalid/Improper User Configuration File')
                    logger.warning('Configuration File Error')
                    KrystalStartup.VerifyMember(self)
                    userdata.close()
        else:
            sys.stdout.write("Oh my goodness! Hello You!\nThis is our first time meeting :)")
            for c in Welcome:
                sys.stdout.write(c)
                sys.stdout.flush()
                time.sleep(0.10)
            KrystalStartup.VerifyMember(self)

    def VerifyMember(self):
        n = 0
        ableaccessID = input('AbleAccess ID: ')
        params = dict(
            user=ableaccessID
        )
        resp = requests.get(url=APIURL, params=params)
        data = json.loads(resp.text)
        name = data['krystal'][0]['user']['fname']
        email = data['krystal'][0]['user']['email']
        if name and email:
            message = "User: {0}/{1} verified on ".format(name, ableaccessID)
            message += time.strftime("%Y-%m-%d %H:%M:%S",
                                     time.localtime(time.time()))
            logger.debug(message)
            if KrystalStartup.AddUserData(name, ableaccessID, email):
                KrystalStartup.hello(self, name)
                return
        else:
            n += 1
            sys.stdout.write('Invalid ID / Unknown User')
            if n < 2:
                KrystalStartup.VerifyMember(self)
            else:
                sys.stdout.write('Too many tries. Verify account at ableinc.us/access')
                sys.exit(1)
        resp.close()

    @staticmethod
    def AddUserData(name,  aaid, email):
        data = {'name': '{}'.format(name),
                'accessID': '{}'.format(aaid),
                'email': '{}'.format(email)
                }
        with open(CONFIGJSON, 'w') as config:
            json.dump(data, config)
        config.close()
        return True

    def hello(self, user):
        # update()
        print('Hello, {}'.format(user.title()))
        system('say -v Ava -r 195 "Hello {}"'.format(user))
        Detector()
        return


if __name__ == '__main__':
    if (sys.platform.startswith('win32')) and (sys.version_info >= (3, 4)):
        sys.stdout.write('Though your Python version is compatible, '
                         'Windows is not yet hosted for Krystal. In the works!')
        exit(1)
    elif (sys.platform.startswith('linux')) and (sys.version_info >= (3, 4)):
        sys.stdout.write('Though your Python version is compatible, '
                         'Linux is not yet hosted for Krystal. In the works!')
        exit(1)
    elif sys.platform.startswith('cygwin'):
        sys.stdout.write('Cygwin not supported. Maybe in the future.')
        exit(1)
    elif (sys.platform.startswith('darwin')) and (sys.version_info >= (3, 4)):
        print("\nKRYSTAL BETA - THINGS MAY FAIL - DON'T BE ANGRY\n")
        time.sleep(3)
        KrystalStartup()

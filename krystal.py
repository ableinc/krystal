#! /usr/bin/env python3
from os import system, makedirs, environ
environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import io
import json
import logging
import signal
import socket
import sys
import time
import zipfile
from os.path import exists
from pathlib import Path

import requests

from SBpy3 import snowboydecoder
from uni import MODEL, CONFIGJSON, UPDATEURL, UNKNOWNFACEFILES, VERSION, UPDATEDUMP

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
    print('\nChecking Able for updates...')
    time.sleep(3)
    params = dict(
        version=VERSION
    )
    resp = requests.get(url=UPDATEURL, params=params)
    data = json.loads(resp.text)
    vi = data['krystal'][0]['current_version']['versionid']
    nm = data['krystal'][0]['current_version']['name']
    str(vi)
    print("You're running: {}".format(nm))
    if vi != VERSION:
        print('You have an outdated version Krystal. Downloading current version.\n')
        zipurl = requests.get('https://github.com/ableinc/krystal/archive/master.zip')
        zippath = zipfile.ZipFile(io.BytesIO(zipurl.content))
        zippath.extractall(UPDATEDUMP)
        print("Check 'updated' directory for updated files. Please copy 'userinfo.json' "
              "to the new 'resources' folder and restart krystal.\n")
    else:
        print('You are up-to-date.')
    print('Updates done.\n')
    return True


def importantFilesCheck():
    if not exists(UNKNOWNFACEFILES):
        makedirs(UNKNOWNFACEFILES)

    if not exists(UPDATEDUMP):
        makedirs(UPDATEDUMP)


class KrystalStartup:
    def __init__(self):
        importantFilesCheck()
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
        ableaccessID = input("AbleAccess ID [please enter 'demo']: ")
        if ableaccessID != 'demo':
            sys.exit(1)
        else:
            KrystalStartup.hello(self, 'Demo User')
        # params = dict(
        #     user=ableaccessID
        # )
        # resp = requests.get(url=APIURL, params=params)
        # data = json.loads(resp.text)
        # name = data['krystal'][0]['user']['fname']
        # email = data['krystal'][0]['user']['email']
        # if name and email:
        #     message = "User: {0}/{1} verified on ".format(name, ableaccessID)
        #     message += time.strftime("%Y-%m-%d %H:%M:%S",
        #                              time.localtime(time.time()))
        #     logger.debug(message)
        #     if KrystalStartup.AddUserData(name, ableaccessID, email):
        #         KrystalStartup.hello(self, name)
        #         return
        # else:
        #     n += 1
        #     sys.stdout.write('Invalid ID / Unknown User')
        #     if n < 2:
        #         KrystalStartup.VerifyMember(self)
        #     else:
        #         sys.stdout.write('Too many tries. Verify account at ableinc.us/access')
        #         sys.exit(1)
        # resp.close()

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
        update()
        print('Hello, {}'.format(user.title()))
        system('say -v Ava -r 195 "Hello {}"'.format(user))
        Detector()
        return


if __name__ == '__main__':
    if not (sys.platform.startswith('darwin') and (sys.version_info >= 3, 4)):
        print('At the moment {} is currently not supported. MacOS is currently the only '
              'supported platform.'.format(sys.platform))
        print("\nKrystal ------------- Beta Program v. 0.90.2\n")
        time.sleep(3)
        KrystalStartup()

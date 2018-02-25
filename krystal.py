#! /usr/bin/env python3
# python specific
import json
import signal
import socket
import sys
import time
from os import system, makedirs, environ
from os.path import exists
from pathlib import Path

from SBpy3 import snowboydecoder
from engine.push.dailyupdates import DailyUpdates
# krystal
from uni import AUDIOMODEL, APIURL, COMMANDURL, CONFIGJSON, UPDATEURL, TEST_FACES_DIR, VERSION, UPDATEDUMP

# initialize
environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
Updates = DailyUpdates(APIURL, UPDATEURL, UPDATEDUMP, VERSION, COMMANDURL, CONFIGJSON)
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

    detector = snowboydecoder.HotwordDetector(AUDIOMODEL, sensitivity=0.5)

    # main loop
    detector.start(detected_callback=snowboydecoder.play_audio_file,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)


def importantFilesCheck():
    if not exists(TEST_FACES_DIR):
        makedirs(TEST_FACES_DIR)

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
                    KrystalStartup.VerifyMember(self)
                    userdata.close()
        else:
            sys.stdout.write("Oh my goodness! Hello You!\nThis is our first time meeting :)")
            for word in Welcome:
                sys.stdout.write(word)
                sys.stdout.flush()
                time.sleep(0.10)
            KrystalStartup.VerifyMember(self)

    def VerifyMember(self):
        ableaccessID = input("AbleAccess ID [please enter 'demo']: ")
        if ableaccessID != 'demo':
            sys.exit(1)
        else:
            KrystalStartup.hello(self, 'User')
            # Updates.universal_handler('verify', opt=ableaccessID)

    def hello(self, user):
        print('\nHello, {}'.format(user.title()))
        system('say -v Ava -r 185 "Hello {}"'.format(user))
        Detector()
        return


if __name__ == '__main__':
    if not sys.platform.startswith('darwin') and (sys.version_info >= 3, 4):
        print('At the moment {} is currently not supported. MacOS is currently the only '
              'supported platform.'.format(sys.platform))
        sys.exit(1)
    print("\nKrystal ------------- Alpha (0.90.2)\n")
    # Updates.universal_handler('update')
    KrystalStartup()

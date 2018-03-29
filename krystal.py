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
from uni import AUDIOMODEL, APIURL, CONFIGJSON, TEST_FACES_DIR, VERSION, NOTIFICATIONS, ENGINE_DIR

# initialize
environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
Updates = DailyUpdates(APIURL, NOTIFICATIONS, VERSION, CONFIGJSON)
IPADDR = socket.gethostbyname(socket.gethostname())
EXECUTABLE = sys.executable

Welcome = "\nThank you for unpacking me!\nI'm starting to get comfy but...\nI don't really know much about you.\n" \
          "Soooo, first thing first,\nif you're registered at AbleInc.us go ahead\nand enter your " \
          "AbleAccess ID.\n"

interrupted = False


def returner(data_to_send):
    Updates.universal_handler(use='send_info', cmd=data_to_send)
    return


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
    if not exists(TEST_FACES_DIR or ENGINE_DIR):
        makedirs(TEST_FACES_DIR)
        makedirs(ENGINE_DIR)


class KrystalInitialStartup:
    def __init__(self):
        importantFilesCheck()
        FreshStart = Path(CONFIGJSON)
        if FreshStart.is_file():
            with open(CONFIGJSON, 'r') as userdata:
                data = json.load(userdata)
                name = data['name']
                key = data['accessID']
                if key and name:
                    KrystalInitialStartup.hello(self, name)
                    userdata.close()
                    Detector()
                else:
                    KrystalInitialStartup.VerifyMember(self)
                    userdata.close()
        else:
            sys.stdout.write("Oh my goodness! Hello You!\nThis is our first time meeting :)")
            for word in Welcome:
                sys.stdout.write(word)
                sys.stdout.flush()
                time.sleep(0.10)
            KrystalInitialStartup.VerifyMember(self)

    def VerifyMember(self):
        ableaccessID = input("AbleAccess ID: ")
        validUser = Updates.universal_handler('verify', opt=ableaccessID)
        if validUser:
            KrystalInitialStartup.hello(self, validUser)

    def hello(self, user):
        print('Hello, {}\n'.format(user.title()))
        system('say -v Ava -r 185 "Hello {}"'.format(user))
        Updates.universal_handler('push', opt='user')
        Detector()
        return


def start():
    if not sys.platform.startswith('darwin') and (sys.version_info >= 3, 4):
        print('At the moment {} is currently not supported. MacOS is currently the only '
              'supported platform.'.format(sys.platform))
        sys.exit(1)
    print("\nKrystal Alpha ------------- {}\n".format(VERSION))
    Updates.universal_handler('update')


if __name__ == '__main__':
    start()
    KrystalInitialStartup()

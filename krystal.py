#! /usr/bin/env python3
# python specific
import json
import logging
import signal
import socket
import sys
import time
from datetime import datetime
from os import system
from pathlib import Path
from SBpy3 import snowboydecoder
from engine.push.dailyupdates import DailyUpdates
from resources.helper import preferences
# krystal
import uni

# initialize
Updates = DailyUpdates()
IPADDR = socket.gethostbyname(socket.gethostname())
EXECUTABLE = sys.executable
logging.basicConfig(filename=uni.EVENT_LOG, format='%(asctime)s:%(levelname)s:%(name)s - %(message)s', level=logging.INFO)
log_events = logging.getLogger('Krystal_Main')
start_datetime = 'Krystal started on ' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
numberOfFailedLoginAttempts = []

Welcome = "\nThank you for unpacking me!\nI'm starting to get comfy but...\nI don't really know much about you.\n" \
          "Soooo, first thing first,\nif you're registered at AbleInc.us go ahead\nand enter your " \
          "AI Key.\n"

interrupted = False


def checkForValidOS():
    if not sys.platform.startswith('darwin') and (sys.version_info >= 3, 4):
        print('MacOS is currently the only supported platform. \
              Your platform: {}'.format(sys.platform))
        exit()


class KrystalInitialStartup:
    def __init__(self):
        FreshStart = Path(uni.CONFIGJSON)
        if FreshStart.is_file():
            with open(uni.CONFIGJSON, 'r') as userdata:
                data = json.load(userdata)
                name = data['name']
                key = data['AIKEY']
                usrnm = data['username']
                if key and name:
                    status = Updates.universal_handler('status', option=usrnm)
                    if status is False:
                        print(status)
                        exit(0)
                    KrystalInitialStartup.hello(self, name)
                    userdata.close()
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
        AIKEY = input("AI Key: ")
        validUser = Updates.universal_handler('verify', option=AIKEY)
        if validUser is not None:
            KrystalInitialStartup.hello(self, validUser)
        else:
            KrystalInitialStartup.VerifyMember(self)

    def hello(self, user):
        print('Hello, {}\n'.format(user.title()))
        system('say -v Ava -r 185 "Hello {}"'.format(user))
        Updates.universal_handler('push')
        Detector()
        return


def run_demo_version(user):
    print('Hello, {}\n'.format(user.title()))
    system('say -v Ava -r 185 "Hello {}"'.format(user))
    print("Thank you for using Krystal. When running in demo mode you will not receive \n "
          "notifications or automatic updates. This account is not personalized.")
    Detector()
    return


def returner(userStatement, krystalStatement):
    Updates.universal_handler(use='conversation', userStatement=userStatement, krystalStatement=krystalStatement)
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

    detector = snowboydecoder.HotwordDetector(uni.AUDIOMODEL, sensitivity=0.5)

    # main loop
    detector.start(detected_callback=snowboydecoder.play_audio_file,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)


def startup(position):
    if position.isdigit():
        if len(numberOfFailedLoginAttempts) > 1:
            numberOfFailedLoginAttempts.clear()
            print('Too many login attempts. Program terminating. \
                                 Try again later.')
        else:
            numberOfFailedLoginAttempts.append(datetime.today())
            time.sleep(1)
            print('Invalid entry. Please try again.')
            print('Your last attempt was at: ', numberOfFailedLoginAttempts[-1])
            initial()

    if position == 'Y':
        run_demo_version('demo user')

    if position == 'N':
        print("Krystal Alpha ------------- {}\n".format(uni.VERSION))
        # Updates.universal_handler('update')  # automatic updates temporarily disabled
        KrystalInitialStartup()


def userPreferences():
    print('Settings')
    for count, option in enumerate(preferences):
        print(count, ' --- ',  option)
    selection = input('Option selection > ')
    if selection == 0:
        return 'not yet enabled '


def initial():
    user_input = input('Start as Demo? (Y/N) > ')
    startup(user_input.title())


if __name__ == '__main__':
    checkForValidOS()
    log_events.info(start_datetime)
    initial()

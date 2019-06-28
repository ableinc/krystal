#! /usr/bin/env python3
import json
import logging
import signal
import sys
import time
from os import environ
from pathlib import Path

import netifaces

from engine.push.dailyupdates import DailyUpdates
from resources.command_handling import command_handler, process_request_text
from resources.verbal_feedback import verbal_feedback
from root import USER_JSON, EVENT_LOG, AUDIO_MODEL, check_valid_sys_requirements, initialize_env_variables
from snowboy import snowboydecoder

# initialize
welcome_msg = "\nThank you for unpacking me!\nI'm starting to get comfy but...\nI don't really know much about you.\n" \
              "Soooo, first thing first,\nif you're registered at https://able.digital go ahead\nand enter your " \
              "AiKey.\n"

interrupted = False


def determine_execution():
    print(f"Krystal Alpha ------------- {environ['VERSION']}\n")
    position = input('Start as Demo? (y/n) > ')
    if position.lower() == 'y':
        Startup(demo=True)
    else:
        Updates.universal_handler('update')
        Startup()


class Startup:
    def __init__(self, demo=False):
        self.data = None
        self.demo = demo
        self.first_name = None

        if self.demo:
            self.first_name = 'demo user'
            self.run_demo_version()
            # self.test()
            return

    def start(self):
        user_json_file = Path(USER_JSON)
        try:
            if not user_json_file.is_file():
                sys.stdout.write("Oh my goodness! Hello You!\nThis is our first time meeting :)")
                for word in welcome_msg:
                    sys.stdout.write(word)
                    sys.stdout.flush()
                    time.sleep(0.5)
                self.verify_member()
                return

            with open(USER_JSON, 'r') as userdata:
                data = json.load(userdata)
                name = data['name']
                key = data['AIKEY']
                username = data['username']

            self.first_name = name
            status = Updates.universal_handler('status', payload=username)
            if status[0] is False:
                print(status[1])
                sys.exit()
            self.run_main_version()
        except KeyError:
            self.verify_member()

    def verify_member(self):
        print('Verifying account...')
        aikey = input("AI Key: ")
        valid_user = Updates.universal_handler('verify', payload=aikey)
        if valid_user is None:
            print('Could not verify user account. Exiting program.')
            sys.exit()
        self.first_name = valid_user
        self.run_main_version()

    def hello(self):
        verbal_feedback(phrase=f'Hello, {self.first_name.title()}', vocal_tone='misc', vocal_speed=185,
                        vocal_volume=0.55)

    def test(self):
        try:
            while True:
                request = input('Yes? > ')
                prefix, str_concat = process_request_text(request)
                command_handler(True, (prefix, str_concat))
        except KeyboardInterrupt:
            sys.exit()

    def run_main_version(self):
        self.hello()
        Updates.universal_handler('push')
        hey_krytal()

    def run_demo_version(self):
        self.hello()
        print("Thank you for using Krystal. In demo mode you will not receive\n"
              "notifications or automatic updates. This account is not personalized.")
        while bool(environ['AUTO_REFRESH']):
            hey_krytal()


def returner(user_statement, krystal_statement):
    """
    Sends spoken and response conversation to Able servers. Conversation
    logs are kept for users to view in the Able Access Conversation Portal.
    :param user_statement: the user spoken dialogue
    :param krystal_statement: krystal's response to user
    :return:
    """
    Updates.universal_handler(use='conversation', user_statement=user_statement, krystal_statement=krystal_statement)
    return


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted


def hey_krytal():
    """
    Detects "Hey Krystal"
    :return:
    """
    # capture SIGINT signal, e.g., Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)

    detector = snowboydecoder.HotwordDetector(AUDIO_MODEL, sensitivity=0.5)

    # main loop
    detector.start(detected_callback=snowboydecoder.play_audio_file,
                   interrupt_check=interrupt_callback,
                   sleep_time=0.03)

    detector.terminate()

    verbal_feedback('Yes?')
    if not command_handler():
        log_events.error('COMMAND HELPER FAILURE')
        environ['AUTO_REFRESH'] = 'False'
    else:
        log_events.info('command handler - success')


if __name__ == '__main__':
    initialize_env_variables()
    check_valid_sys_requirements()
    # Logger
    logging.basicConfig(filename=EVENT_LOG, format='%(asctime)s:%(levelname)s:%(name)s - %(message)s',
                        level=logging.INFO)
    log_events = logging.getLogger('krystal.py')
    start_datetime = f' Started on {time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))}'
    try:
        ip4 = netifaces.ifaddresses('en0')[netifaces.AF_INET][0]['addr']
        ip6 = netifaces.ifaddresses('en0')[netifaces.AF_INET6][0]['addr']
    except KeyError:
        ip4 = netifaces.ifaddresses('en7')[netifaces.AF_INET][0]['addr']
        ip6 = netifaces.ifaddresses('en7')[netifaces.AF_INET6][0]['addr']
    network_msg = f' Network Info - IP4: {ip4}, IP6: {ip6}'
    log_events.info(start_datetime)
    log_events.info(network_msg)

    # Updates library
    Updates = DailyUpdates()
    # Start application
    determine_execution()

import io
import json
import logging
import sys
import textwrap
import time
import zipfile
from distutils.dir_util import copy_tree
from os import system, mkdir, environ
from shutil import rmtree, copy2

import requests

import root

main_script = root.KRYSTAL
environ['GLOG_minloglevel'] = '2'
logging.basicConfig(filename=root.EVENT_LOG, format='%(asctime)s:%(levelname)s:%(name)s - %(message)s',
                    level=logging.INFO)
log_events = logging.getLogger('Updates')


class DailyUpdates:
    def __init__(self):
        self.endpoint = root.Endpoints
        self.conversation = self.endpoint.conversations.value
        self.notifications = self.endpoint.notification.value
        self.system = self.endpoint.system.value
        self.users = self.endpoint.users.value
        self.version = environ['VERSION']
        self.user_data_file = root.USER_JSON

    def universal_handler(self, use, payload='', user_statement='', krystal_statement=''):
        if use == 'update':
            print('Checking Able for updates...')
            params = dict(
                version_id=self.version
            )
            data = self.commit_requests(self.system, params)
            vi = data['krystal']['versionId']
            url = data['krystal']['url']

            if vi != self.version:
                print('You have an outdated version of Krystal.')
                self.update_software(url, vi)
            else:
                print('Krystal is up-to-date!')

        elif use == 'conversation':
            aikey = self.get_aikey()
            params = dict(
                userStatment=user_statement,
                krystalStatement=krystal_statement,
                aikey=aikey,
            )
            self.commit_requests(self.notifications, params)

        elif use == 'verify':
            params = dict(
                aikey=payload
            )
            data = self.commit_requests(self.users, params)
            try:
                krystal = data['krystal'][0]  # the body_tag is the status of the request
                if str(krystal).lower() == 'user not found':
                    raise KeyError
                if payload == '' or not payload.isdigit():
                    raise TypeError

                role = krystal['role']
                first_name = krystal['firstName']
                last_name = krystal['lastName']
                username = krystal['username']
                email = krystal['email']
            except KeyError:
                log_events.info("User couldn't be found with given information")
                return None
            except TypeError:
                log_events.info('AbleAccess ID entry was left blank or non-numeric value')
                return None
            message = "{0} {1} ({2}) verified on ".format(first_name, last_name, payload)
            message += time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            if self.add_data(role, first_name, last_name, username, payload, email, message):
                return first_name

        elif use == 'push':
            params = dict(
                role=self.get_user_role()
            )
            data = self.commit_requests(self.notifications, params)
            publisher = data['publisher']
            memo = data['message']
            date = data['date']
            print(f'Message from {publisher}')
            print(publisher + ',                       ' + date + '\n')
            print('\n'.join(textwrap.wrap(memo, width=40)), '\n')

        elif use == 'status':
            # checks if user is banned by fetching AiKey by role
            params = dict(
                username=payload
            )
            data = self.commit_requests(self.notifications, params)
            if data['status'] == 'banned':
                log_events.info('User is banned from servers.')
                return [False, "Unfortunately you're banned. Do better things."]
            return True

    @staticmethod
    def commit_requests(url, params, respond=True):
        resp = requests.get(url=url, params=params)
        data = json.loads(resp.text)
        resp.close()
        if respond:
            return data

    def add_data(self, role, first_name, last_name, username, aikey, email, message):
        data = {'role': '{}'.format(role),
                'firstName': '{}'.format(first_name),
                'lastName': '{}'.format(last_name),
                'username': '{}'.format(username),
                'AIKEY': '{}'.format(aikey),
                'email': '{}'.format(email),
                'verification': '{}'.format(message)
                }
        with open(self.user_data_file, 'w') as config:
            json.dump(data, config)
        config.close()
        return True

    def get_aikey(self):
        with open(self.user_data_file, 'r') as userdata:
            data = json.load(userdata)
            aikey = data['AIKEY']
            userdata.close()
        return aikey

    def get_user_role(self):
        with open(self.user_data_file, 'r') as userdata:
            data = json.load(userdata)
            role = data['role']
            userdata.close()
        return role

    def update_software(self, url, vi, mode='git'):
        if mode is 'git':
            system('git pull')
        else:
            print('Downloading Krystal version {} ...'.format(vi))
            source = requests.get(url)
            source_file = zipfile.ZipFile(io.BytesIO(source.content))
            copy2(self.user_data_file, root.ROOT_OF_ROOT)
            rmtree(root.ROOT)
            mkdir(root.ROOT)
            source_file.extractall(root.ROOT)
            copy_tree(root.TEMP_UPDATE_DIR, root.ROOT)
            copy2(root.GRAB_USER_INFO, self.user_data_file)
            rmtree(root.TEMP_UPDATE_DIR)
            print('Thank you for downloading. Krystal will restart.')
            system('python3 {}'.format(main_script))
            sys.exit()

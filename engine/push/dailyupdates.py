import io
import json
import logging
import time
import zipfile
from datetime import datetime

import requests

from uni import ERROR_LOG

logging.basicConfig(filename=ERROR_LOG, format='%(asctime)s:%(levelname)s:%(message)s', level=logging.ERROR)
logger = logging.getLogger('Krystal')


class DailyUpdates:
    def __init__(self, default, update_dir, version_id, user_data_file):
        """
            :param: default: Krystal's main API url - APIURL
            :param: update_url: the API provided for the updating of Krystal -UPDATEURL
            :param: update_dir: the directory to store the update zip - UPDATEDUMP
            :param: version_id: your current running version of Krystal - VERSION
            :param: send_info_url: the API provided to send user data back to Able Inc. - COMMANDURL
            :param: add_user_file: the API provided to fetch if the provided AbleAccess ID is valid - CONFIGJSON

        """
        self.default = default
        self.update_dir = update_dir
        self.version_id = version_id
        self.user_data_file = user_data_file

    def universal_handler(self, use, opt='', cmd=''):
        """

        :param use: the call to which command you would like to use
        :param opt: the option you combined with the command (cmd) (i.e 'what is your' ... [cmd]
        :param cmd:
        :return:
        """
        if use == 'update':
            print('Checking Able for updates...')
            time.sleep(2)
            params = dict(
                version_id=self.version_id
            )
            resp = requests.get(url=self.default, params=params, verify=False)
            data = json.loads(resp.text)
            vi = data['krystal'][0]['versionid']
            # nm = data['krystal'][0]['name']
            url = data['krystal'][0]['url']
            if vi != self.version_id:
                new_version = input('You have an outdated version of Krystal. Download latest version? (Y/n) ')
                if new_version.lower() == 'y':
                    zipurl = requests.get(url)
                    zippath = zipfile.ZipFile(io.BytesIO(zipurl.content))
                    zippath.extractall(self.update_dir)
                    print("Check 'updated' directory for updated files. Please copy 'userinfo.json' "
                          "to the new 'resources' folder and restart krystal.\n")
                else:
                    pass

        elif use == 'send_data':
            cur_date = datetime.now().strftime('%Y-%m-%d')
            user_name, user_id = DailyUpdates.get_user_name(self)
            params = dict(
                id=user_id,
                name=user_name,
                version=self.version_id,
                command=cmd,
                date=cur_date
            )
            resp = requests.get(url=self.default, params=params, verify=False)
            if resp:
                resp.close()

        elif use == 'verify':
            params = dict(
                aid=opt
            )
            resp = requests.get(url=self.default, params=params, verify=False)
            data = json.loads(resp.text)
            name = data['krystal'][0]['user_info']['fname']
            username = data['krystal'][0]['user_info']['username']
            email = data['krystal'][0]['user_info']['email']

            if opt == '':
                raise AttributeError('AbleAccess ID cannot be left empty')

            message = "User: {0}/{1} verified on ".format(name, opt)
            message += time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            logger.debug(message)
            if DailyUpdates.add_data(self, name, username, opt, email):
                return name
            resp.close()

    def add_data(self, name, usrnm, aaid, email):
        data = {'name': '{}'.format(name),
                'username': '{}'.format(usrnm),
                'accessID': '{}'.format(aaid),
                'email': '{}'.format(email)
                }
        with open(self.user_data_file, 'w') as config:
            json.dump(data, config)
        config.close()
        return True

    def get_user_name(self):
        with open(self.user_data_file, 'r') as userdata:
            data = json.load(userdata)
            name = data['name']
            key = data['accessID']
            return name, key


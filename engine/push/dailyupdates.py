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
    def __init__(self, default, update_url, update_dir, version_id, send_info_url, add_user_file):
        """
            :param: default: Krystal's main API url - APIURL
            :param: update_url: the API provided for the updating of Krystal -UPDATEURL
            :param: update_dir: the directory to store the update zip - UPDATEDUMP
            :param: version_id: your current running version of Krystal - VERSION
            :param: send_info_url: the API provided to send user data back to Able Inc. - COMMANDURL
            :param: add_user_file: the API provided to fetch if the provided AbleAccess ID is valid - CONFIGJSON

        """
        self.default = default
        self.server_updates = update_url
        self.update_dir = update_dir
        self.version_id = version_id
        self.send_data = send_info_url
        self.add_user_data = add_user_file

    def universal_handler(self, use, opt='', cmd=''):

        if use == 'update':
            print('Checking Able for updates...')
            time.sleep(2)
            params = dict(
                version=self.version_id
            )
            resp = requests.get(url=self.server_updates, params=params)
            data = json.loads(resp.text)
            vi = data['krystal'][0]['current_version']['versionid']
            # nm = data['krystal'][0]['current_version']['name']
            url = data['krystal'][0]['current_version']['url']
            if vi != self.version_id:
                print('You have an outdated version of Krystal. Downloading current version.\n')
                zipurl = requests.get(url)
                zippath = zipfile.ZipFile(io.BytesIO(zipurl.content))
                zippath.extractall(self.update_dir)
                print("Check 'updated' directory for updated files. Please copy 'userinfo.json' "
                      "to the new 'resources' folder and restart krystal.\n")

        elif use == 'send_data':
            cur_date = datetime.now().strftime('%Y-%m-%d')
            params = dict(
                date=cur_date,
                option=opt,
                command=cmd
            )
            resp = requests.get(url=self.send_data, params=params)
            if resp:
                resp.close()

        elif use == 'verify':
            params = dict(
                user=opt
            )
            resp = requests.get(url=self.default, params=params)
            data = json.loads(resp.text)
            name = data['krystal'][0]['user']['fname']
            email = data['krystal'][0]['user']['email']

            if opt == '':
                raise AttributeError('AbleAccess ID cannot be left empty')

            message = "User: {0}/{1} verified on ".format(name, opt)
            message += time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            logger.debug(message)
            if DailyUpdates.add_data(self, name, opt, email):
                return True
            resp.close()

    def add_data(self, name, aaid, email):
        data = {'name': '{}'.format(name),
                'accessID': '{}'.format(aaid),
                'email': '{}'.format(email)
                }
        with open(self.add_user_data, 'w') as config:
            json.dump(data, config)
        config.close()
        return True


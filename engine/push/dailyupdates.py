import io, json, textwrap, time, zipfile
from datetime import datetime
from os import system, mkdir, environ
from distutils.dir_util import copy_tree
from shutil import rmtree, copy2
import requests
from uni import ERROR_LOGGER, TEMP_UPDATE_DIR, ROOT, ROOT_OF_ROOT, CONFIGJSON, KRYSTAL, GRAB_USER_INFO

main_script = KRYSTAL
environ['GLOG_minloglevel'] = '2'


class DailyUpdates:
    def __init__(self, default, notify, version_id, user_data_file):
        """
            :param: default: Krystal's main API url - APIURL
            :param: notify: Krystal's notification API url - NOTIFICATION
            :param: update_dir: the directory to store the update zip - UPDATEDUMP
            :param: version_id: your current running version of Krystal - VERSION
            :param: add_user_file: the API provided to fetch if the provided AbleAccess ID is valid - CONFIGJSON

        """
        self.default = default
        self.notify = notify
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
            # print('Checking Able for updates...')
            time.sleep(2)
            params = dict(
                version_id=self.version_id
            )
            resp = requests.get(url=self.default, params=params)
            data = json.loads(resp.text)
            vi = data['krystal'][0]['versionid']
            # nm = data['krystal'][0]['name']
            url = data['krystal'][0]['url']
            # vi_to_float = float(vi)
            # version_to_float = float(self.version_id)
            if vi != self.version_id:
                new_version = input('You have an outdated or unmaintained version of Krystal. '
                                    'Download latest version? (y/n) ')
                if new_version.lower() == 'y':
                    print('Downloading Krystal version {} ...'.format(vi))
                    source = requests.get(url)
                    source_file = zipfile.ZipFile(io.BytesIO(source.content))
                    copy2(self.user_data_file, ROOT_OF_ROOT)
                    rmtree(ROOT)
                    mkdir(ROOT)
                    source_file.extractall(ROOT)
                    copy_tree(TEMP_UPDATE_DIR, ROOT)
                    copy2(GRAB_USER_INFO, CONFIGJSON)
                    rmtree(TEMP_UPDATE_DIR)
                    print('Thank you for downloading. Krystal will restart.')
                    system('python3 {}'.format(main_script))
                    exit(0)
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
            resp = requests.get(url=self.default, params=params)
            if resp:
                resp.close()

        elif use == 'verify':
            params = dict(
                aid=opt
            )
            resp = requests.get(url=self.default, params=params)
            data = json.loads(resp.text)
            name = data['krystal'][0]['user_info']['fname']
            username = data['krystal'][0]['user_info']['username']
            email = data['krystal'][0]['user_info']['email']

            if opt == '' and opt.isdigit():
                ERROR_LOGGER.error('AbleAccess ID entry was left blank or non-numeric value')
                raise AttributeError('Invalid entry')

            message = "{0} ({1}) verified on ".format(name, opt)
            message += time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            if DailyUpdates.add_data(self, name, username, opt, email, message):
                return name
            resp.close()

        elif use == 'push':
            params = dict(
                memo=opt
            )
            resp = requests.get(url=self.notify, params=params)
            data = json.loads(resp.text)
            name = data['memo'][0]['name']
            memo = data['memo'][0]['message']
            date = data['memo'][0]['date']
            print('Message from Able')
            print(name + ',                       ' + date + '\n')
            print('\n'.join(textwrap.wrap(memo, width=40)))
            print('\n')
            resp.close()
        return

    def add_data(self, name, usrnm, aaid, email, message):
        data = {'name': '{}'.format(name),
                'username': '{}'.format(usrnm),
                'AIKEY': '{}'.format(aaid),
                'email': '{}'.format(email),
                'verification': '{}'.format(message)
                }
        with open(self.user_data_file, 'w') as config:
            json.dump(data, config)
        config.close()
        return True

    def get_user_name(self):
        with open(self.user_data_file, 'r') as userdata:
            data = json.load(userdata)
            name = data['name']
            key = data['AIKEY']
            userdata.close()
        return name, key

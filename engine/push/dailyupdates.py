import io, json, textwrap, time, zipfile, requests, logging
from os import system, mkdir, environ
from distutils.dir_util import copy_tree
from shutil import rmtree, copy2
import uni

main_script = uni.KRYSTAL
environ['GLOG_minloglevel'] = '2'
logging.basicConfig(filename=uni.EVENT_LOG, format='%(asctime)s:%(levelname)s:%(name)s - %(message)s', level=logging.INFO)
log_events = logging.getLogger('Updates')


class DailyUpdates:
    def __init__(self):
        self.endpoint = uni.Endpoints
        self.conversation = self.endpoint.conversations.value
        self.notifications = self.endpoint.notification.value
        self.system = self.endpoint.system.value
        self.users = self.endpoint.users.value
        self.version_id = uni.VERSION
        self.user_data_file = uni.CONFIGJSON

    def universal_handler(self, use, option='', userStatement='', krystalStatement=''):
        """

        :param use: the call to which command you would like to use
        :param
        :param
        :return:
        """
        if use == 'update':
            print('Checking Able for updates...')
            time.sleep(2)
            params = dict(
                version_id=self.version_id
            )
            resp = requests.get(url=self.system, params=params)
            data = json.loads(resp.text)
            vi = data['krystal']['versionid']
            url = data['krystal']['url']
            if vi != self.version_id:
                new_version = input('You have an outdated or unmaintained version of Krystal. '
                                    'Download latest version? (y/n) ')
                if new_version.lower() == 'y':
                    print('Downloading Krystal version {} ...'.format(vi))
                    source = requests.get(url)
                    source_file = zipfile.ZipFile(io.BytesIO(source.content))
                    copy2(self.user_data_file, uni.ROOT_OF_ROOT)
                    rmtree(uni.ROOT)
                    mkdir(uni.ROOT)
                    source_file.extractall(uni.ROOT)
                    copy_tree(uni.TEMP_UPDATE_DIR, uni.ROOT)
                    copy2(uni.GRAB_USER_INFO, self.user_data_file)
                    rmtree(uni.TEMP_UPDATE_DIR)
                    print('Thank you for downloading. Krystal will restart.')
                    system('python3 {}'.format(main_script))
                    exit(0)
                else:
                    pass
        elif use == 'conversation':
            aikey = self.getAiKey()
            params = dict(
                userStatment=userStatement,
                krystalStatement=krystalStatement,
                aikey=aikey,
            )
            resp = requests.get(url=self.notifications, params=params)
            if resp:
                resp.close()

        elif use == 'verify':
            params = dict(
                aikey=option
            )
            resp = requests.get(url=self.users, params=params)
            data = json.loads(resp.text)
            role = data['krystal'][0]['role']
            firstName = data['krystal'][0]['firstName']
            lastName = data['krystal'][0]['lastName']
            username = data['krystal'][0]['username']
            email = data['krystal'][0]['email']
            status = data['krystal'][0]

            if ((data and firstName and lastName and username and email) is None) or status == 'User Not Found':
                log_events.info("User couldn't be found with given information")
                print("Something went wrong. Verification may be down or information invalid.")
                return None

            if option == '' or not option.isdigit():
                log_events.error('AbleAccess ID entry was left blank or non-numeric value')
                print('Invalid entry. Try again.')
                return None

            message = "{0} {1} ({2}) verified on ".format(firstName, lastName, option)
            message += time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            if self.add_data(role, firstName, lastName, username, option, email, message):
                return firstName
            resp.close()

        elif use == 'push':
            params = dict(
                role=self.getUserRole()
            )
            resp = requests.get(url=self.notifications, params=params)
            data = json.loads(resp.text)
            publisher = data['memo'][0]['publisher']
            memo = data['memo'][0]['message']
            date = data['memo'][0]['date']
            print('Message from Able')
            print(publisher + ',                       ' + date + '\n')
            print('\n'.join(textwrap.wrap(memo, width=40)))
            print('\n')
            resp.close()

        elif use == 'status':
            # checks if user is banned by fetching AiKey by role
            params = dict(
                check_user=option
            )
            resp = requests.get(url=self.notifications, params=params)
            data = json.loads(resp.text)
            user_status = data['status'][0]
            resp.close()
            if user_status == 'banned':
                log_events.info('User is banned from servers.')
                msg = "Unfortunately you're banned. Do better things."
                return False, msg
            return True

    def add_data(self, role, firstName, lastName, username, aikey, email, message):
        data = {'role': '{}'.format(role),
                'firstName': '{}'.format(firstName),
                'lastName': '{}'.format(lastName),
                'username': '{}'.format(username),
                'AIKEY': '{}'.format(aikey),
                'email': '{}'.format(email),
                'verification': '{}'.format(message)
                }
        with open(self.user_data_file, 'w') as config:
            json.dump(data, config)
        config.close()
        return True

    def getAiKey(self):
        with open(self.user_data_file, 'r') as userdata:
            data = json.load(userdata)
            aikey = data['AIKEY']
            userdata.close()
        return aikey

    def getUserRole(self):
        with open(self.user_data_file, 'r') as userdata:
            data = json.load(userdata)
            role = data['role']
            userdata.close()
        return role

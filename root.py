import os.path as path
import sys
from enum import Enum
from os import makedirs, environ, execl

# main
ROOT = path.dirname(path.abspath(__file__))
ROOT_OF_ROOT = path.dirname(path.abspath(ROOT))
KRYSTAL = path.join(ROOT, 'krystal.py')

# krystal
TEMP_UPDATE_DIR = path.join(ROOT, 'krystal-master/')  # grabbing zipfile path, this cannot be changed
GRAB_USER_INFO = path.join(ROOT_OF_ROOT, 'userinfo.json')  # userinfo.json temp location during update
TEMP_DATA_DIR = path.join(ROOT, 'temp/')
USER_JSON = path.join(TEMP_DATA_DIR, 'userinfo.json')  # userinfo.json file location after update / original loc
EXECUTABLE = sys.executable

# models
TRAIN_DATA = path.join(ROOT, 'models/train/traindata.json')
TEST_DATA = path.join(ROOT, 'models/test/testdata.json')
TRAIN_FACES_DIR = path.join(ROOT, 'models/train')
TEST_FACES_DIR = path.join(ROOT, 'models/test')
FACES_MODEL = path.join(ROOT, 'models/faces.ai')
DET_PROTOTXT = path.join(ROOT, 'models/MobileNetSSD.prototxt.txt')
DET_MODEL = path.join(ROOT, 'models/MobileNetSSD.caffemodel')

# logs
EVENT_LOG = path.join(TEMP_DATA_DIR, 'events.log')  # this file will be sent to Able Inc for diagnostics

# conversation
PERSONMODEL = path.join(ROOT, 'conversation/krystal_beta_model')
PERSONMODEL_TRAIN = path.join(ROOT, 'conversation/training_data')
PERSONMODEL_JSON = path.join(ROOT, 'conversation/personality.json')
PERSONMODEL_LOG = path.join(ROOT, 'conversation/tflearn_logs')

# Snowboy
RESOURCE_FILE = path.join(ROOT, "snowboy/resources/common.res")
DETECT_DING = path.join(ROOT, "snowboy/resources/ding.wav")
DETECT_DONG = path.join(ROOT, "snowboy/resources/dong.wav")
AUDIO_MODEL = path.join(ROOT, 'snowboy/resources/Krystal.pmdl')

# Memory Engine
MEMORY_NEW_INFORMATION = path.join(ROOT, 'memory/newInformation.json')

# create necessary files and directories
if not path.exists(TEST_FACES_DIR):
    makedirs(TEST_FACES_DIR)
    makedirs(TEMP_DATA_DIR)


def initialize_env_variables():
    env_file = open('.env', 'r').readlines()
    for env in env_file:
        en_v = env.replace('\n', '')
        idx = en_v.find('=')
        environ[str(en_v[:idx])] = str(en_v[idx + 1:])


def restart():
    execl(EXECUTABLE, 'Krystal', __file__, *sys.argv[1:])


# Endpoints for Able Inc. API
class Endpoints(Enum):
    conversations = 'https://able.systems/krystal/conversations'
    notification = 'https://able.systems/krystal/push'
    system = 'https://able.systems/krystal/system'
    users = 'https://able.systems/krystal/users'
    local_host = 'http://localhost:3000/'  # developer purposes - do not remove
    access_url = 'https://www.able.digital/access'


def check_valid_sys_requirements():
    good = False
    if sys.version_info >= (3, 6):
        good = True
    if sys.platform == 'darwin':
        good = True
    if sys.platform == 'linux':
        good = True

    if good is False:
        print('! Unsupported Platform !\n')
        print(f"Python version 3.6 or higher is required on the Mac and Linux OS."
              f"\nYour platform: {[sys.platform if str(sys.platform) != 'darwin' else 'MacOS'][0]}\n"
              f"Your python version: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
        sys.exit()

# pre-processed
# ERROR_LOGGER = logging.basicConfig(filename=EVENT_LOG, format='%(asctime)s:%(levelname)s:%(message)s', level=logging.ERROR)
# DEBUG_LOGGER = logging.basicConfig(filename=EVENT_LOG, format='%(asctime)s:%(levelname)s:%(message)s', level=logging.DEBUG)
# INFO_LOGGER = logging.basicConfig(filename=EVENT_LOG, format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
# WARNING_LOGGER = logging.basicConfig(filename=EVENT_LOG, format='%(asctime)s:%(levelname)s:%(message)s', level=logging.WARNING)

import logging
import os

# main
ROOT = os.path.dirname(os.path.abspath(__file__))
ROOT_OF_ROOT = os.path.dirname(os.path.abspath(ROOT))
KRYSTAL = os.path.join(ROOT, 'krystal.py')

# krystal
VERSION = '0.90.3'
TEMP_UPDATE_DIR = os.path.join(ROOT, 'krystal-master/')
USER_INFO_MOVE_LOCATION = os.path.join(TEMP_UPDATE_DIR, 'engine/etc/userinfo.json')
CONFIGJSON = os.path.join(ROOT, 'engine/etc/userinfo.json')
DEFKEY = '23Able'

# model
TRAINDATA = os.path.join(ROOT, 'model/train/traindata.json')
TESTDATA = os.path.join(ROOT, 'model/test/testdata.json')
TRAIN_FACES_DIR = os.path.join(ROOT, 'model/train')
TEST_FACES_DIR = os.path.join(ROOT, 'model/test')
FACES_MODEL = os.path.join(ROOT, 'model/faces.ai')
AUDIOMODEL = os.path.join(ROOT, 'model/Krystal.pmdl')
DET_PROTOTXT = os.path.join(ROOT, 'model/MobileNetSSD.prototxt.txt')
DET_MODEL = os.path.join(ROOT, 'model/MobileNetSSD.caffemodel')

# logs
ERROR_LOG = os.path.join(ROOT, 'engine/etc/error.log')

# conversation
PERSONMODEL = os.path.join(ROOT, 'conversation/krystal_beta_model')
PERSONMODEL_TRAIN = os.path.join(ROOT, 'conversation/training_data')
PERSONMODEL_JSON = os.path.join(ROOT, 'conversation/personality.json')
PERSONMODEL_LOG = os.path.join(ROOT, 'conversation/tflearn_logs')

# EAS
EAS_NEWDATA = os.path.join(ROOT, 'resources/newdata.json')

# Able Inc. API
APIURL = 'https://ableinc.us/krystal/api/v0/'
NOTIFICATIONS = 'https://ableinc.us/krystal/push/'

# pre-processed
ERROR_LOGGER = logging.basicConfig(filename=ERROR_LOG, format='%(asctime)s:%(levelname)s:%(message)s', level=logging.ERROR)

import os

# main
ROOT = os.path.dirname(os.path.abspath(__file__))
KRYSTAL = os.path.join(ROOT, 'krystal.py')

# krystal
VERSION = '0902'
UPDATEDUMP = os.path.join(ROOT, 'resources/updates/')
IDENTPATH = os.path.join(ROOT, 'Identity.json')
CONFIGJSON = os.path.join(ROOT, 'resources/userinfo.json')
TRAINDATA = os.path.join(ROOT, 'model/test/traindata.json')
TESTDATA = os.path.join(ROOT, 'model/test/testdata.json')
TRAIN_FACES_DIR = os.path.join(ROOT, 'model/train')
TEST_FACES_DIR = os.path.join(ROOT, 'model/test')
FACES_MODEL = os.path.join(ROOT, 'model/faces.ai')
DEFKEY = '23Able'
AUDIOMODEL = os.path.join(ROOT, 'model/Krystal.pmdl')
DET_PROTOTXT = os.path.join(ROOT, 'model/MobileNetSSD.prototxt.txt')
DET_MODEL = os.path.join(ROOT, 'model/MobileNetSSD.caffemodel')

# conversation
PERSONMODEL = os.path.join(ROOT, 'conversation/krystal_beta_model')
PERSONMODEL_TRAIN = os.path.join(ROOT, 'conversation/training_data')
PERSONMODEL_JSON = os.path.join(ROOT, 'conversation/personality.json')
PERSONMODEL_LOG = os.path.join(ROOT, 'conversation/tflearn_logs')

# EAS
EAS_NEWDATA = os.path.join(ROOT, 'resources/newdata.json')

# Able Inc. API
APIURL = 'https://ableinc.us/krystal/api/'
UPDATEURL = 'https://ableinc.us/krystal/update/'
COMMANDURL = 'https://ableinc.us/krystal/commands/'

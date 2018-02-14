import os

ROOT = os.path.dirname(os.path.abspath(__file__))
KRYSTAL = os.path.join(ROOT, 'krystal.py')
VERSION = '0901'
APIURL = 'https://ableinc.us/krystal/api/'
UPDATEURL = 'https://ableinc.us/krystal/update/'
IDENTPATH = os.path.join(ROOT, 'Identity.json')
CONFIGJSON = os.path.join(ROOT, 'resources/userinfo.json')
TRAINDATA = os.path.join(ROOT, 'model/test/traindata.json')
TESTDATA = os.path.join(ROOT, 'model/test/testdata.json')
KNOWNFACEFILES = ROOT + '/model/train'
UNKNOWNFACEFILES = ROOT + '/model/test'
SAVEDFACES = ROOT + '/model/faces.ai'
DEFKEY = '23Able'
MODEL = ROOT + '/model/Krystal.pmdl'
DET_PROTOTXT = ROOT + '/model/MobileNetSSD.prototxt.txt'
DET_MODEL = ROOT + '/model/MobileNetSSD.caffemodel'

# conversation
PERSONMODEL = ROOT + '/conversation/krystal_beta_model'
PERSONMODEL_TRAIN = ROOT + '/conversation/training_data'
PERSONMODEL_JSON = ROOT + '/conversation/personality.json'
PERSONMODEL_LOG = ROOT + '/conversation/tflearn_logs'


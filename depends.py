import pip

toinstall = ['tensorflow', 'pyaudio', 'spacy', 'opencv-python', 'face_recognition', 'speechrecognition', 'tflearn', 'beautifulsoup', 'imutils']

def install(pkg):
    pip.main(['install', pkg])

if __name__ == '__main__':
  for x in toinstall:
      install(x)

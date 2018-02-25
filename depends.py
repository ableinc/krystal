import pip

toinstall = ['tensorflow', 'pyaudio', 'opencv-python', 'face_recognition', 'speechrecognition', 'tflearn', 'beautifulsoup', 'imutils']


def install(pkg):
    pip.main(['install', pkg])


if __name__ == '__main__':
    for x in toinstall:
        install(x)
    input('Remember to brew install portaudio, sox and swig. Press enter to exit.')

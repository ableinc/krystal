import subprocess, sys

pythonLibraries = ['tensorflow', 'pyaudio', 'opencv-python', 'face_recognition', 'speechrecognition',
                   'tflearn', 'beautifulsoup', 'imutils']

homebrewdependencies = ['portaudio', 'sox', 'swig']

# Krystal has not been tested on Python 3.7, though below you can install dependencies if you have 3.7. Please
# contact me via Github.com/ableinc or at http://able.digital/#contact to inform me if everything is compatible


def installPythonLibraries(pkg):
    if sys.version_info == (3, 7):
        subprocess.run(['pip', 'install', '--upgrade', '{}'.format(pkg)], capture_output=subprocess.PIPE)
    else:
        subprocess.run(['pip', 'install', '--upgrade', '{}'.format(pkg)], stdout=subprocess.PIPE)


def installBrewDependencies(pkg):
    if sys.version_info == (3, 7):
        subprocess.run(['brew', 'install', '{}'.format(pkg)], capture_output=subprocess.PIPE)
    else:
        subprocess.run(['brew', 'install', '{}'.format(pkg)], stdout=subprocess.PIPE)


def launchKrystal():
    if sys.version_info == (3, 7):
        subprocess.run(['python3', 'krystal.py'], capture_output=subprocess.PIPE)
    else:
        subprocess.run(['python3', 'krystal.py'], stdout=subprocess.PIPE)
    exit(0)


if __name__ == '__main__':
    if sys.platform.startswith('darwin') and sys.version_info >= (3, 4):
        print('This file will install all dependencies and libraries needed to run Krystal. Please do not interrupt.')
        subprocess.run(['brew', 'update'], stdout=subprocess.PIPE)

        for dep in homebrewdependencies:
            installBrewDependencies(dep)

        for lib in pythonLibraries:
            installPythonLibraries(lib)

        print('Installation complete. Running Krystal.')
        launchKrystal()
    else:
        print('MacOS is the only supported platform with Python version 3.4 or higher.'
              '\nYour platform & python version: {0} with python {1}.{2}.{3}'.format(sys.platform,
                                                                                     sys.version_info.major,
                                                                                     sys.version_info.minor,
                                                                                     sys.version_info.micro))
        exit(0)


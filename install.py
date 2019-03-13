import io
import shlex
import subprocess
from os.path import dirname, abspath

from root import check_valid_sys_requirements

python_libraries = ['tensorflow==1.10', 'netifaces', 'deepspeech', 'webrtcvad', 'halo', 'pyaudio', 'opencv-python',
                    'face_recognition', 'SpeechRecognition', 'tflearn', 'beautifulsoup', 'imutils', 'spacy', 'nltk',
                    'snowboy', 'beautifulsoup4', 'sklearn', 'requests', 'pyttsx3', 'pyobjc', 'uvloop', 'dlib',
                    'html5lib']

homebrew_formulas = ['cmake', 'portaudio', 'sox', 'swig']


def reader(buffer, title=None):
    print(f'{title}: ', '  '.join((io.TextIOWrapper(buffer.stderr, encoding='utf-8'))))
    return


def executor(app, pkg=None):
    commands = {
        'brew': f'brew install {pkg}',
        'brew update': 'brew update',
        'python': f'pip install {pkg}',
        'spacy': 'python -m spacy download en_core_web_lg'
    }
    command_line = commands.get(app, None)
    command = shlex.split(command_line)
    reader(subprocess.Popen(command, stderr=subprocess.PIPE, cwd=dirname(abspath(__file__))), app)
    return


if __name__ == '__main__':
    check_valid_sys_requirements()
    print('Installing dependencies for Krystal. Please do not interrupt.')
    executor('brew update')
    for x in homebrew_formulas: executor('brew', x)
    for x in python_libraries: executor('python', x)
    executor('spacy')
    print('Complete. You can now start Krystal.')

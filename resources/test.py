from resources import helper
from pathlib import Path
from resources import CommandHandling
from os import execl
import sys

d = Path(__file__).resolve().parents[1]
print(d)

prefix = ['whats your', 'what is your']
attrib = ['age', 'name', 'eye color']

sample = 'whats your age?'
sample2 = 'can you tell me what is your name?'
sample3 = 'eye color, please?'

# BOOLS ARE COOL
FOUNDIT = True


def restart():
    execl(sys.executable, 'test', __file__, *sys.argv[1:])


num = input('Enter a number > ')
if num.isalnum():
    restart()

# print(helper.requestoptions[0:2])

# if findit(sample):
    # print('True')


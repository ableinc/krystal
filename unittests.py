from engine.operations import LanguageEngine
from uni import MEMORY_NEWINFORMATION
import json
import pprint
from multiprocessing.pool import ThreadPool


def process(sentence):
    LanguageEngine.LanguageEngine(words=sentence)


if __name__ == '__main__':
    words = "i wonder could i ever meet barack obama. barack obama seems nice"
    process(sentence=words)

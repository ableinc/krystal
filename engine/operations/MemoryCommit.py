import json
from io import StringIO
from os import path

from root import MEMORY_NEW_INFORMATION


class CommitToMemory:

    def __init__(self, memory):
        """
        Commit new information to memory for training
        :param pos: Dictionary object of fetched information and part of speech
        """
        self.memory = memory
        self.error = None
        self.initialInputData = {
            "memory": [
                self.memory
            ]
        }
        self.write()

    def write(self):
        print(f'Committing to memory: \n {self.memory} ...')
        try:
            if not path.exists(MEMORY_NEW_INFORMATION):
                with open(MEMORY_NEW_INFORMATION, mode='w', encoding='utf-8') as newJson:
                    json.dump(obj=self.initialInputData, fp=newJson, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                memory_file = StringIO(open(MEMORY_NEW_INFORMATION, 'r', encoding='utf-8').read())
                memory_file_object = json.load(memory_file)
                different_keys = memory_file_object - self.memory
                if different_keys is not None:
                    memory_file_object.update(different_keys)
                else:
                    memory_file_object.update(self.memory)

                with open(MEMORY_NEW_INFORMATION, mode='w', encoding='utf-8') as updateJson:
                    json.dump(obj=memory_file_object, fp=updateJson, sort_keys=True, indent=4, separators=(',', ': '))
        except json.JSONDecodeError as je:
            print(f'Json Decoder Error: {je}')
            self.error = je
        except TypeError as te:
            print(f'TypeError in MemoryCommit: {te}')
            self.error = te
        finally:
            if self.error is not None:
                print(f'Failed to commit object to memory: \n{self.memory}')
            else:
                print(f'Successfully committed to memory: \n {self.memory}')


class Misc:
    def __init__(self):
        pass

    @staticmethod
    def is_word_character(c):
        return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9' or c == '_'

    def wordCount(self, sentence):
        c = 0
        for i in range(1, len(sentence)):
            if not self.is_word_character(sentence[i]) and self.is_word_character(sentence[i - 1]):
                c += 1
        if self.is_word_character(sentence[-1]):
            c += 1
        if c != 250:
            c = 250
        return c

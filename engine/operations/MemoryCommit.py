import json
from io import StringIO
from os import path, remove
from root import MEMORY_NEW_INFORMATION


class CommitToMemory:

    def __init__(self, memory):
        """
        Commit new information to memory for training
        :param pos: Dictionary object of fetched information and part of speech
        """
        self._memory = memory
        self.error = None
        self._init_data = {
            "memory": [
                self._memory
            ]
        }
        self.write()

    def write(self):
        similar_contents = False
        try:
            if not path.exists(MEMORY_NEW_INFORMATION):
                with open(MEMORY_NEW_INFORMATION, mode='w', encoding='utf-8') as newJson:
                    json.dump(obj=self._init_data, fp=newJson, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                memory_file = StringIO(open(MEMORY_NEW_INFORMATION, 'r', encoding='utf-8').read())
                memory_file_object = json.load(memory_file)
                for entry in memory_file_object['memory']:
                    if entry['phrase'] == self._memory['phrase']:
                        similar_contents = True
                if similar_contents is False:
                    memory_file_object['memory'].append(self._memory)
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
                print('Failed to commit object to memory. ')
                remove(MEMORY_NEW_INFORMATION)
            elif similar_contents is True:
                print('Information is already known.')
            else:
                print('Successfully committed to memory.')


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

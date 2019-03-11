import json
import webbrowser
from os import system
from threading import Thread

import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize

from engine.operations.MemoryCommit import CommitToMemory
from root import MEMORY_NEW_INFORMATION


class AssistantOperations:
    def __init__(self, operation_type, operation_parameter):
        """
        Search online or Open application
        :param operation_type: whether it is 'open' or 'search'
        :param operation_parameter: the item to 'open' or 'search'
        """
        self.searchParameters = operation_type
        self.searchObject = operation_parameter
        self.open_and_search()

    def open_and_search(self):
        if self.searchParameters == 'open':
            upper = str(self.searchObject).title()
            system('open -a /Applications/{}.app'.format(upper))
        elif self.searchParameters == 'search':
            google_search_string = 'https://www.google.com/search?q=' + self.searchObject.replace(' ', '') + '&ie=UTF-8'
            webbrowser.open_new(google_search_string)


class InformationFetcher:
    def __init__(self, full_context_dict: dict):
        """
        This class is used by Krystal to gather information from the web for later training.
        This is how Krystal learns new information, as well as when and how to use it. She
        will understand various types of sentence structures and properties of speech.

        ** Features will be deprecated in the future **

        :param full_context_dict: part of speech dictionary from Language Engine
        """
        self.full_context_dict = full_context_dict,
        self.online_content = None

    def parse_dict_information(self):
        for word, properties in self.full_context_dict:
            search_sentence = self.search_based_on_noun_type(properties['pos'], word)
            self.full_context_dict[word]['response'] = search_sentence

    def search_based_on_noun_type(self, noun_type, word):
        if noun_type == 'PROPN':
            request_link = 'https://en.wikipedia.org/wiki/' + word.replace(' ', '_')
            page = requests.get(request_link)
            tree = BeautifulSoup(page.text, 'html5lib')
            data = [page.text for page in tree.find_all("sup", class_="cite_ref-1")]
            page.close()
            self.online_content = data
        else:
            request_link = 'https://www.google.com/search?q=' + word.replace(' ', '') + '&oq=' + \
                           word.replace(' ', '') + '&ie=UTF-8'
            page = requests.get(request_link)
            tree = BeautifulSoup(page.text, 'html5lib')
            data = [page.text for page in tree.find_all("span", class_="st")]
            page.close()
            self.online_content = data
        return self.grab_sentence(self.online_content, word)

    @staticmethod
    def grab_sentence(data, search_object):
        temp_data = ''.join(data)
        grab_sentences = sent_tokenize(temp_data)
        response = []
        for sentences in range(len(grab_sentences)):
            if search_object in grab_sentences[sentences]:
                response.append(grab_sentences[sentences])
            else:
                response.append(grab_sentences[0])
        return response

    def send_for_memory_commit(self):
        CommitToMemory(memory=self.full_context_dict)

    @staticmethod
    def get_memories():
        with open(MEMORY_NEW_INFORMATION, 'r') as jsonFile:
            json_object = json.load(jsonFile)
            return json_object


class WorkerThread(Thread):
    def __init__(self, full_context_dict: dict):
        super(WorkerThread, self).__init__()
        self.fcd = full_context_dict

    def run(self):
        InformationFetcher(full_context_dict=self.fcd)

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
    def __init__(self, full_context_dict: dict, self_start: bool = False):
        """
        This class is used by Krystal to gather information from the web for later training.
        This is how Krystal learns new information, as well as when and how to use it. She
        will understand various types of sentence structures and properties of speech.

        ** Features will be deprecated in the future **

        :param full_context_dict: part of speech dictionary from Language Engine
        :param self_start: automatic memory commit (threading)
        """
        self.full_context_dict = full_context_dict
        self.self_start = self_start
        self.online_content = None
        self.parse_dict_information()

    def parse_dict_information(self):
        """
        Adding information to empty fields of the full context dictionary. Data is
        sent to search_based_on_noun_type() function to be gathered.
        :return:
        """
        response = self.full_context_dict['response']
        phrase = self.full_context_dict['phrase']
        try:
            if self.self_start:
                self.send_for_memory_commit()
                return
            for word, properties in self.full_context_dict[phrase].items():
                if properties['definition'] == '':
                    search_sentence = self.search_based_on_noun_type(properties['pos'], word)
                    self.full_context_dict[phrase][word]['definition'] = search_sentence
            if response == '':
                sentence = self.search_based_on_noun_type('phrase', phrase, False)
                self.full_context_dict['response'] = sentence
        except ValueError as ve:
            print(f'ValueError in InformationFetcher: {ve}')
        except KeyError as ke:
            print(f'KeyError in InformationFetcher: {ke}')

    @staticmethod
    def print_information(args):
        for x in args:
            print(f'Arg: {x}')

    def search_based_on_noun_type(self, noun_type, word, is_definition: bool = True):
        """
        Search Google or Wikipedia based on noun_type and is_definition boolean
        :param noun_type: Noun or Proper noun
        :param word: The word of the noun_type
        :param is_definition: Look up word as a definition
        :return:
        """
        if noun_type == 'PROPN':
            request_link = 'https://en.wikipedia.org/wiki/' + word.replace(' ', '_')
            page = requests.get(request_link)
            tree = BeautifulSoup(page.text, 'html5lib')
            data = [page.text for page in tree.find_all("sup", class_="cite_ref-1")]
            page.close()
            self.online_content = data
        else:
            if is_definition:
                request_link = 'https://www.google.com/search?q=definition+of+' + word.replace(' ', '+') + '&oq=' + \
                               'definition+of+' + word.replace(' ', '+') + '&ie=UTF-8'
            else:
                request_link = 'https://www.google.com/search?q=' + word.replace(' ', '+') + '&oq=' + \
                               word.replace(' ', '+') + '&ie=UTF-8'
            page = requests.get(request_link)
            tree = BeautifulSoup(page.text, 'html5lib')
            data = [page.text for page in tree.find_all("span", class_="st")]
            page.close()
            self.online_content = data
        return self.grab_sentence(self.online_content, word)

    @staticmethod
    def grab_sentence(content, subject, singular: bool = True):
        """
        Grab sentence from web content provided by BeautifulSoup
        :param content: Content from BeautifulSoup
        :param subject: What we're looking for in sentence
        :param singular: One sentence or many
        :return:
        """
        temp_data = ''.join(content)
        grab_sentences = sent_tokenize(temp_data)
        response = []
        if singular:
            return str(grab_sentences[0])
        for sentences in range(len(grab_sentences)):
            if subject in grab_sentences[sentences]:
                response.append(grab_sentences[sentences])
            else:
                response.append(grab_sentences[0])
        return response

    def send_for_memory_commit(self):
        """
        Send mutable memory data to memory commit function
        :return:
        """
        CommitToMemory(memory=self.full_context_dict)

    def return_full_memory_object(self):
        """
        Return full mutable memory data
        :return:
        """
        return self.full_context_dict

    @staticmethod
    def get_memories():
        """
        Get existing memories
        :return:
        """
        with open(MEMORY_NEW_INFORMATION, 'r') as jsonFile:
            json_object = json.load(jsonFile)
            return json_object


class WorkerThread(Thread):
    def __init__(self, full_context_dict: dict, self_start: bool = False):
        super(WorkerThread, self).__init__()
        self.fcd = full_context_dict
        self.self_start = self_start

    def run(self):
        InformationFetcher(full_context_dict=self.fcd, self_start=self.self_start)

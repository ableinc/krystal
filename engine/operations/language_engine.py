# This file was formally named 'Personification' that purpose was useless and has been replaced
import json
import re
import string
import webbrowser
from os import system

import nltk
import requests
from bs4 import BeautifulSoup
from nltk.tokenize import sent_tokenize, word_tokenize

from resources.helper import defaultrequests
from uni import EAS_NEWDATA

"""

                            Environmental Adaption Protocol - Language Engine:
                               Handles all information gathered by Krystal.

   

"""
important_sentence = []
isNoun = []
wholeName = []
nameStatus = 'False'
searchOGL = []
searchFGL = []


class LanguageEngine(object):

    class DetailClassifier:
        """

        search_parameter = the initiating question (i.e. 'who is.., where is..')
        search_object = the object to search following the search_parameter
        full_parameter = this is both search_parameter and search_object together

        """
        def __init__(self, search_parameter, search_object):
            self.ai_sp = search_parameter
            self.ai_so = search_object
            self.full_parameter = self.ai_sp + self.ai_so
            searchOGL.append(self.ai_so)

        def basic_legacy_operations(self):
            if self.ai_sp == 'open':
                upper = string.capwords(self.ai_so)
                results = 'Opening ' + upper
                system('open -a /Applications/{}.app'.format(upper))
                return results
            elif self.ai_sp == defaultrequests[1:3]:
                nospace = re.sub(r"\s+", '+', self.ai_so)
                finalstringrequest = 'https://www.google.com/search?q=' + nospace + '&ie=UTF-8'
                webbrowser.open_new(finalstringrequest)
                results = 'Searching Google for ' + self.ai_so
                return results

        def isanoun(self, decision=''):
            """
            :param decision: this is passed option:
                - detect_name: this detects if each pair (0:1 += 1 < length of proper nouns
                [first names, last names]) is related to one another by position, if so this is classified as a name
            """
            objecttokenized = word_tokenize(self.ai_so, 'english')
            tagged_tokens = nltk.pos_tag(objecttokenized)

            if decision == 'detect_name':
                proper_noun = [word for (word, tag) in tagged_tokens if tag == 'NNP']
                listlength = len(proper_noun)
                n = 0
                while n < listlength:
                    findfname = self.ai_so.find(''.join(proper_noun[n]))
                    n += 1
                    findlname = self.ai_so.find(''.join(proper_noun[n]))
                    if findfname:
                        back = n - 1
                        # wholename.append(proper_noun[back])
                        fnamelength = findfname + len(proper_noun[n])
                        if fnamelength == findlname:
                            wholeName.append((proper_noun[back], proper_noun[n]))
                        else:
                            wholeName.append((proper_noun[back]))
                    n += 1
                return [wholeName[0] if len(wholeName) > 0 else 'unknown']

            proper_noun = [word for (word, tag) in tagged_tokens if tag == 'NNP']
            singular_noun = [word for (word, tag) in tagged_tokens if tag == 'NN']
            if len(proper_noun) > 0 and not len(singular_noun) > 0:
                isNoun.append('NNP')
            else:
                isNoun.append('NN')
            return [isNoun[0] if len(isNoun) > 0 else 'unknown']

    class InformationHandler:
        """
        This class is to handle the background online search of new data. This class is passed the following arguments:

        - objectsearch = the full search parameter provided by the user (i.e the full question, not run through nltk)
        - search_type = this is the specific search engine you would like to use for the online search. by default it is
        'google' (this may be helpful if search web engines are easier to scrape)
        - noun_type = discovered from the DetailClassifier class
        """

        @staticmethod
        def search_engine(objectosearch=''.join(searchOGL), search_type='google', noun_type=''.join(isNoun)):
            if search_type == 'google' or noun_type == 'NN':
                removedspace = re.sub(r"\s+", '+', objectosearch)
                requestlink = 'https://www.google.com/search?q=' + removedspace + '&oq=' + \
                              removedspace + '&ie=UTF-8'
                page = requests.get(requestlink)
                tree = BeautifulSoup(page.text, 'lxml')
                data = [page.text for page in tree.find_all("span", class_="st")]
                page.close()
                LanguageEngine.InformationHandler.grab_sentence(data)

            if noun_type == 'NNP':
                removedspace = re.sub(r'\s+', '_', objectosearch)
                requestlink = 'https://en.wikipedia.org/wiki/' + removedspace
                page = requests.get(requestlink)
                tree = BeautifulSoup(page.text, 'lxml')
                data = [page.text for page in tree.find_all("span", class_="st")]
                page.close()
                LanguageEngine.InformationHandler.grab_sentence(data)

        @staticmethod
        def grab_sentence(data, object_from_search=''.join(searchOGL)):
            temp_data = ''.join(data)
            grab_sentences = sent_tokenize(temp_data, 'english')
            for x in range(0, len(grab_sentences)):
                if object_from_search in grab_sentences[x]:
                    important_sentence.append(grab_sentences[x])
                else:
                    important_sentence.append(grab_sentences[0])
            return important_sentence

        @staticmethod
        def createjsontraining(entry=''.join(searchOGL)):
            inputdata = {'entry': '{}'.format(entry),
                         'if_name': '{}'.format(['True' if len(wholeName) > 0 else nameStatus]),
                         'noun_type': '{}'.format(''.join(isNoun[0])),
                         'response': '{}'.format(important_sentence)
                         }
            with open(EAS_NEWDATA, 'a') as UND:
                json.dump(inputdata, UND)
            UND.close()


class Misc(object):

    @staticmethod
    def is_word_character(c):
        return 'a' <= c <= 'z' or 'A' <= c <= 'Z' or '0' <= c <= '9' or c == '_'

    @staticmethod
    def word_count(sentence):
        c = 0
        for i in range(1, len(sentence)):
            if not Misc.is_word_character(sentence[i]) and Misc.is_word_character(sentence[i - 1]):
                c += 1
        if Misc.is_word_character(sentence[-1]):
            c += 1
        if c != 250:
            c = 250
        return c

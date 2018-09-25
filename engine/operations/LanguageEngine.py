import json
import logging
import re
import string
import webbrowser
from os import system, path
from threading import Thread
from multiprocessing.pool import ThreadPool
import requests
from bs4 import BeautifulSoup
import spacy
import en_core_web_lg
from nltk import sent_tokenize
# krystal
from uni import MEMORY_NEWINFORMATION, EVENT_LOG

logging.basicConfig(filename=EVENT_LOG, format='%(asctime)s:%(levelname)s:%(name)s - %(message)s', level=logging.DEBUG)
log_events = logging.getLogger('Language Engine')

partOfSpeechTagging = []  # Noun, Pronoun, Proper noun, Number, etc.
partOfSpeechTaggingText = []  # the word
responseFromInformationSearch = []

entitiesTagging = []
entitiesTaggingText = []

# spacy configuration - 'xx' for all language detection (large models only)
defaultLanguage = 'en_core_web_lg'
nlp = spacy.load(defaultLanguage)  # declaration - nlp(u''.format([variable_containing_text]))
# nlp = en_core_web_lg.load()

"""
        - self.words : titled text (used to determine noun type in part-of-speech detection)

        Text: The original word text. - token.text
        Lemma: The base form of the word. - token.lemma_
        POS: The simple part-of-speech tag. - token.pos_
        Tag: The detailed part-of-speech tag. - token.tag_
        Dep: Syntactic dependency, i.e. the relation between tokens. token.dep_
        Shape: The word shape – capitalisation, punctuation, digits.
        is alpha: Is the token an alpha character?
        is stop: Is the token part of a stop list, i.e. the most common words of the language?
        
        - self.doc.ents : entities of text
        
        Text: The original entity text. ent.text
        Start: Index of start of entity in the Doc. ent.start_char
        End: Index of end of entity in the Doc. ent.end_char
        Label: Entity label, i.e. type. ent.label_
        
"""


class LanguageEngine:
    def __init__(self, words):
        if not isinstance(defaultLanguage, str):
            log_events.error('language must be two letter str value')
            return

        if not isinstance(words, str):
            log_events.error('words must be str value')
            return
        print('Language Engine Initiated')
        self.cleaned_words = re.sub(r'[?|$.,!]', r'', words)
        self.words = self.cleaned_words.title().encode()
        self.doc = nlp(self.words.decode('utf-8'))
        self.get_linguistics()

    def get_linguistics(self):
        print('Linguistics Running')
        for token in self.doc:
            if token.pos_ == 'PROPN':
                print(token.text, token.pos_, token.dep_)
                partOfSpeechTagging.append('PROPN')
                partOfSpeechTaggingText.append(self.removeWhitespace(token.text))
            if token.pos_ == 'NOUN':
                print(token.text, token.pos_, token.dep_)
                partOfSpeechTagging.append('NOUN')
                partOfSpeechTaggingText.append(token.text)
            if token.pos_ == 'VERB':
                print(token.text, token.pos_, token.dep_)
                partOfSpeechTagging.append('VERB')
                partOfSpeechTaggingText.append(token.text)
            if token.pos_ == 'NUM':
                print(token.text, token.pos_, token.dep_)
                partOfSpeechTagging.append('NUM')
                partOfSpeechTaggingText.append(token.text)
            if token.pos_ == 'SYM':
                print(token.text, token.pos_, token.dep_)
                partOfSpeechTagging.append('SYM')
                partOfSpeechTaggingText.append(token.text)
            if token.pos_ == 'ADP':
                print(token.text, token.pos_, token.dep_)
                partOfSpeechTagging.append('ADP')
                partOfSpeechTaggingText.append(token.text)
        self.get_entities()

    def get_entities(self):
        for ent in self.doc.ents:
            if ent.label_ == 'PERSON':
                print(ent.text, ent.label_)
                entitiesTagging.append('PERSON')
                entitiesTaggingText.append(ent.text)
            # print(ent.text, ent.start_char, ent.end_char, ent.label_)
        # sort(documentObject=dict(zip(partOfSpeechTaggingText, partOfSpeechTagging)))
        WorkerThread(documentObject=dict(zip(partOfSpeechTaggingText, partOfSpeechTagging)))

    def get_all_tokens(self):
        print('All Token Info')
        for num, token in enumerate(self.doc):
            print(num, token.text, token.pos_, token.dep_, '- head: ', token.head)

    def removeWhitespace(self, text):
        if ' ' in text:
            cleanedText = re.sub(r"\s+", '_', text)
            return cleanedText
        else:
            pass


class AssistantOperations:
    """

    search_parameter = the initiating question (i.e. 'who is.., where is..')
    search_object = the object to search following the search_parameter
    full_parameter = this is both search_parameter and search_object together

    """
    def __init__(self, searchPrefix, searchObject):
        self.searchParameters = searchPrefix
        self.searchObject = searchObject
        print('Assistant Operations Initiated')
        self.openAndSearchOperation()

    def openAndSearchOperation(self):
        if 'open' in self.searchParameters:
            upper = string.capwords(self.searchObject)
            results = 'Opening ' + upper
            system('open -a /Applications/{}.app'.format(upper))
            return results
        elif 'search' in self.searchParameters:
            nospace = re.sub(r"\s+", '+', self.searchObject)
            finalstringrequest = 'https://www.google.com/search?q=' + nospace + '&ie=UTF-8'
            webbrowser.open_new(finalstringrequest)
            results = 'Searching Google for ' + self.searchObject
            return results


class InformationFetcher:
    """
    This classed is used by Krystal to gather information from the web to to train later. This is how Krystal learns new
     information and when and how to use it. She will understand nouns from proper nouns, symbols from numbers,
     vice-versa, etc.

     This class is called when a user asks to search for something. Search features will be deprecated in the future to
     move Krystal away from a personal assistant and into a friend. (usually your friends don't make search requests for
     you)
     """
    def __init__(self, fetchObject, noun, getResponse=False, completeObject=None):
        """
        :param fetchObject: the object (word) that is going to be defined by search
        :param noun: determined by part of speech (will later be changed to 'entity type'
        :param getResponse: if we're looking to return as response to user - default: False
                although ambiguous by definition getResponse will only be called if krystal's trained data returns with
                False as a response.
        :param completeObject: if getResponse is true then this should contain the given sentence by user - default: None
        """
        self.objectToSearch = fetchObject
        self.nounType = noun
        self.data = None
        self.getResponse = getResponse
        self.completeObject = completeObject
        try:
            self.isName = dict(zip(entitiesTaggingText, entitiesTagging))
        except:
            pass
        print('Information Fetcher Initiated')
        self.searchBasedOnNounType()

    def searchBasedOnNounType(self):
        if self.nounType != 'PROPN':
            removedspace = re.sub(r"\s+", '+', self.objectToSearch)
            requestlink = 'https://www.google.com/search?q=' + removedspace + '&oq=' + \
                              removedspace + '&ie=UTF-8'
            page = requests.get(requestlink)
            tree = BeautifulSoup(page.text, 'html5lib')
            data = [page.text for page in tree.find_all("span", class_="st")]
            page.close()
            self.data = data
        else:
            removedspace = re.sub(r'\s+', '_', ''.format(self.objectToSearch))
            requestlink = 'https://en.wikipedia.org/wiki/' + removedspace
            page = requests.get(requestlink)
            tree = BeautifulSoup(page.text, 'html5lib')
            data = [page.text for page in tree.find_all("sup", class_="cite_ref-1")]
            page.close()
            self.data = data

        self.grab_sentence(self.data, self.objectToSearch)

    def grab_sentence(self, data, searchObject):
        temp_data = ''.join(data)
        grab_sentences = sent_tokenize(temp_data)
        response = []
        for sentences in range(len(grab_sentences)):
            if searchObject in grab_sentences[sentences]:
                response.append(grab_sentences[sentences])
            else:
                response.append(grab_sentences[0])
        self.processInformation(response)
        return response

    def processInformation(self, response):
        if self.isName:
            for word, isName in self.isName.items():
                if word == self.objectToSearch:
                    CommitToMemory([self.objectToSearch, self.nounType], True, response)
        else:
            CommitToMemory([self.objectToSearch, self.nounType], False, response)
        return response

    def getResponse(self):
        with open(MEMORY_NEWINFORMATION, 'r') as jsonFile:
            jsonObject = json.load(jsonFile)
            print(jsonObject)


def sort(documentObject):
    """
    :param documentObject: part of speech dictionary
    :return:
    """
    # pool = ThreadPool(processes=1)
    for word, posType in documentObject.items():
        fetcherThread = Thread(target=InformationFetcher, args=(word, posType))
        fetcherThread.daemon = False
        fetcherThread.start()
        InformationFetcher(word, posType)
        # fetcher = InformationFetcher(fetchObject=word, noun=posType)
        # async_result = pool.apply_async(func=fetcher.searchBasedOnNounType)
        # print('Response from thread: ', async_result.get())


class WorkerThread(Thread):
    def __init__(self, documentObject):
        super(WorkerThread, self).__init__()
        self.documentObject = documentObject

    def run(self):
        for word, posType in self.documentObject.items():
            InformationFetcher(fetchObject=word, noun=posType)


class CommitToMemory:
    # entryAndPOS (Dictionary): fetchedObject and part of speech
    # entities (Boolean): (currently) contains true or false to if entry (word) is a name or not
    # response (String): the results of the fetched Object; the Information
    # pos: part of speech

    def __init__(self, entryAndPOS, entities, response):
        print('Preparing Data...')
        self.entryAndPOS = entryAndPOS
        self.entities = entities
        self.response = response
        self.initialInputData = {
            "memory": [
                {
                    "entry": "{}".format(self.entryAndPOS[0] if self.entryAndPOS[0] else None),
                    "name": "{}".format(self.entities),
                    "pos": "{}".format(''.join(self.entryAndPOS[1] if self.entryAndPOS[1] else None)),
                    "responses": "{}".format(self.response if self.response else None)
                }
            ]
        }
        self.updatedInputData = \
            {
                "entry": "{}".format(self.entryAndPOS[0] if self.entryAndPOS[0] else None),
                "name": "{}".format(self.entities),
                "pos": "{}".format(''.join(self.entryAndPOS[1] if self.entryAndPOS[1] else None)),
                "responses": "{}".format(self.response if self.response else None)
            }
        print('Preparation Done.')
        self.write()

    def write(self):
        print('Committing To Memory...')
        try:
            if not path.exists(MEMORY_NEWINFORMATION):
                print('Initial Dump.')
                with open(MEMORY_NEWINFORMATION, mode='w', encoding='utf-8') as newJson:
                    json.dump(obj=self.initialInputData, fp=newJson, sort_keys=True, indent=4, separators=(',', ': '))
                newJson.close()
            else:
                print('Update Dump')
                with open(MEMORY_NEWINFORMATION, mode='r+', encoding='utf-8') as updateJson:
                    jsonObject = json.load(updateJson)
                    jsonObject.append(self.updatedInputData)
                    json.dump(obj=jsonObject, fp=updateJson)
                updateJson.close()
        except json.JSONDecodeError as je:
            raise je
        except ValueError as ve:
            raise ve
        except IOError as ioe:
            raise ioe
        except TypeError as te:
            raise te
        except KeyError as ke:
            raise ke
        finally:
            self.close()

    @staticmethod
    def close():
        partOfSpeechTagging.clear()
        partOfSpeechTaggingText.clear()
        entitiesTagging.clear()
        entitiesTaggingText.clear()
        print('Committed.')
        return


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
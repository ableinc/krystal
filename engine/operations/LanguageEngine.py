import json
import logging
import re
import string
import webbrowser
from os import system
from threading import Thread
import requests
from bs4 import BeautifulSoup
import spacy
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

# spacy configuration - 'x' for all language detection (currently unneeded & untested)
defaultLanguage = 'en'
nlp = spacy.load(defaultLanguage)  # declaration - nlp(u''.format([variable_containing_text]))

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
        if not isinstance(defaultLanguage, str) or len(defaultLanguage) > 2:
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
                partOfSpeechTaggingText.append(token.text)
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
        sort(dictObject=dict(zip(partOfSpeechTaggingText, partOfSpeechTagging)))

    def get_all_tokens(self):
        print('All Token Info')
        for num, token in enumerate(self.doc):
            print(num, token.text, token.pos_, token.dep_, '- head: ', token.head)


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

     This class is passed the following arguments:

    - fetchObject = the object (word) that is going to be defined by search
    - noun_type = discovered from the DetailClassifier class

     """
    def __init__(self, fetchObject, noun):
        self.objectToSearch = fetchObject
        self.nounType = noun
        self.data = None
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
            removedspace = re.sub(r'\s+', '_', self.objectToSearch)
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

    def processInformation(self, response):
        if self.isName:
            commitToMemory([self.objectToSearch, self.nounType], self.isName, response)
        else:
            commitToMemory([self.objectToSearch, self.nounType], {}, response)
        return response


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


def sort(dictObject):
    for word, entityType in dictObject.items():
        fetcherThread = Thread(target=InformationFetcher, args=(word, entityType))
        fetcherThread.daemon = False
        fetcherThread.start()


def commitToMemory(entryAndPOS, entities, response):
    # entryAndPOS : fetchedObject and part of speech
    # entities : (currently) contains true or false conditions to determine if given entry is or is not a name
    # response = the results of the fetched Object; the Information
    # pos: part of speech
    print('Committing To Memory...')
    initialInputData = {'memory': {
            'entry': '{}'.format(entryAndPOS[0] if entryAndPOS[0] else None),
            'is_name': '{}'.format(nameCypher(entities, entryAndPOS[0])),
            'pos': '{}'.format(''.join(entryAndPOS[1] if entryAndPOS[1] else None)),
            'responses': '{}'.format(response if response else None)
        }
    }

    updatedInputData = {
            'entry': '{}'.format(entryAndPOS[0] if entryAndPOS[0] else None),
            'is_name': '{}'.format(nameCypher(entities, entryAndPOS[0])),
            'pos': '{}'.format(''.join(entryAndPOS[1] if entryAndPOS[1] else None)),
            'responses': '{}'.format(response if response else None)
    }
    # r+ to read and write in parallel
    with open(MEMORY_NEWINFORMATION, 'r+') as newInfoJson:
        if len(newInfoJson.readline(0)) > 0:
            print('\t Updating')
            jsonObject = json.load(newInfoJson)
            jsonObject.update(updatedInputData)
            json.dump(obj=jsonObject, fp=newInfoJson, sort_keys=True, indent=4, separators=(',', ': '))
        else:
            print('\t Dumping')
            json.dump(obj=initialInputData, fp=newInfoJson, sort_keys=True, indent=4, separators=(',', ': '))

    newInfoJson.close()
    partOfSpeechTagging.clear()
    partOfSpeechTaggingText.clear()
    entitiesTagging.clear()
    entitiesTaggingText.clear()
    print('Committed.')
    return


def nameCypher(nameDict, entry):
    try:
        for text, isName in nameDict.items():
            if text == entry:
                return True
            else:
                return False
    except:
        return False

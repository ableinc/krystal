import logging
import re

import spacy

from engine.operations.AssistantEngine import WorkerThread
from root import EVENT_LOG

logging.basicConfig(filename=EVENT_LOG, format='%(asctime)s:%(levelname)s:%(name)s - %(message)s', level=logging.DEBUG)
log_events = logging.getLogger('Language Engine')

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
    def __init__(self, words: str):
        _sanitized_string = re.sub(r'[?|$.,!]', r'', words)
        self.words = _sanitized_string.title().encode()
        self.doc = nlp(self.words.decode('utf-8'))
        self.vocab_tagging = {}
        self.entity_tagging = {}
        #  begin operations automatically
        self.begin()

    def begin(self):
        self.get_linguistics()
        self.get_entities()
        self.combine_dicts()
        self.send_data()

    def get_linguistics(self):
        for token in self.doc:
            self.pos_to_dict(token)

    def get_entities(self):
        for ent in self.doc.ents:
            self.ent_to_dict(ent)

    def get_all_tokens(self):
        print('All Token Info')
        for num, token in enumerate(self.doc):
            print(num, token.text, token.pos_, token.dep_, '- head: ', token.head)

    def pos_to_dict(self, token, verbose: bool = True):
        if verbose:
            print(f'{str(token.pos_)}: {token.text}, {token.pos_}, {token.dep_}')
        new_dict = {str(token.text).replace(' ', ''): {'entity': '', 'dep': token.dep_, 'details': token.tag_,
                                                       'head': token.head, 'lemma': token.lemma_, 'pos': token.pos_,
                                                       'response': ''}}
        self.vocab_tagging.update(new_dict)

    def ent_to_dict(self, ent, verbose: bool = False):
        if verbose:
            print(f'{ent.label_}: {ent.text}')
        new_dict = {str(ent.text): {'label': ent.label_}}
        self.entity_tagging.update(new_dict)

    def combine_dicts(self):
        for word, properties in self.vocab_tagging.items():
            if self.entity_tagging.get(word, None) is not None:
                self.vocab_tagging[word]['entity'] = self.entity_tagging[word]['label']
            else:
                self.vocab_tagging[word]['entity'] = 'N/A'

    def send_data(self):
        WorkerThread(full_context_dict=self.vocab_tagging)
        self.clear()

    def clear(self):
        self.vocab_tagging.clear()
        self.entity_tagging.clear()

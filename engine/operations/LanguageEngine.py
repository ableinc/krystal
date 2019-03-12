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


class LanguageEngine:
    def __init__(self, words: str, request: str, known: str = None, self_start: bool = False):
        """
        Exam text through linguistic processing, store in an Object to be returned
        for memory write.

        Type Legend (Spacy):
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

        :param words: titled text (used to determine noun type in part-of-speech detection)
        :param request: the given phrase by user
        :param known: if information is already known to memory then pass value
        :param self_start: process, gather, compress and save data to memory automatically (threading)
        """
        _sanitized_string = re.sub(r'[?|$.,!]', r'', words)
        self.words = _sanitized_string.title().encode()
        self.request = request
        self.known = known
        self.doc = nlp(self.words.decode('utf-8'))
        self.vocab_tagging = {}
        self.entity_tagging = {}
        self.full_vocab_object = {}
        #  begin operations automatically
        if self_start:
            self.auto_flow()

    def auto_flow(self):
        self._get_linguistics()
        self._get_entities()
        self._combine_dicts()
        self.send_data()

    def controlled_flow(self):
        self._get_linguistics()
        self._get_entities()
        self._combine_dicts()
        return self.return_data()

    def _get_linguistics(self):
        for token in self.doc:
            self._pos_to_dict(token)

    def _get_entities(self):
        for ent in self.doc.ents:
            self._ent_to_dict(ent)

    def _get_all_tokens(self):
        print('All Token Info')
        for num, token in enumerate(self.doc):
            print(num, token.text, token.pos_, token.dep_, '- head: ', token.head)

    def _pos_to_dict(self, token, verbose: bool = False):
        if verbose:
            print(f'{token.text}, {token.pos_}, {token.dep_}')
        new_dict = {str(token.text).lower(): {'entity': '', 'dep': token.dep_, 'details': token.tag_,
                                              'head': token.head, 'lemma': token.lemma_, 'pos': token.pos_,
                                              'definition': ''}}
        self.vocab_tagging.update(new_dict)

    def _ent_to_dict(self, ent, verbose: bool = False):
        if verbose:
            print(f'{ent.label_}: {ent.text}')
        new_dict = {str(ent.text).lower(): {'label': ent.label_}}
        self.entity_tagging.update(new_dict)

    def _combine_dicts(self):
        for word, properties in self.vocab_tagging.items():
            if self.entity_tagging.get(word, None) is not None:
                self.vocab_tagging[word]['entity'] = self.entity_tagging[word]['label']
        if self.known is not None:
            self.full_vocab_object.update({self.request: self.vocab_tagging, 'response': self.known})
        else:
            self.full_vocab_object.update({self.request: self.vocab_tagging, 'response': ''})

    def send_data(self):
        WorkerThread(full_context_dict=self.full_vocab_object)
        self.clear()

    def return_data(self):
        return self.full_vocab_object

    def clear(self):
        self.vocab_tagging.clear()
        self.entity_tagging.clear()
        self.full_vocab_object.clear()

import re
import spacy

isNone = []
wholeName = []
nameStatus = False

__status__ = 'Unstable'


class LanguageEngine:
    def __init__(self, words, language='en'):
        if not isinstance(language, str) or len(language) > 2:
            raise TypeError('language must be two letter str value')

        if not isinstance(words, str):
            raise TypeError('words must be str value')
        self.cleaned_words = re.sub(r'[?|$.,!]', r'', words)
        self.words = self.cleaned_words.title().encode()
        self.nlp = spacy.load(language)
        self.doc = self.nlp(self.words.decode('utf-8'))
        self.temp = []
        self.cleaned_doc = None
        self.clean_sentence()

    def clean_sentence(self):
        for word in self.doc:
            if word.pos_ == 'PROPN':
                self.temp.append(word.text)
            else:
                self.temp.append(word.text.lower())
        self.cleaned_doc = self.nlp(u' '.join(self.temp))
        print('First Iter: ', self.cleaned_doc)
        del self.temp
        print('\n')

    def get_proper_nouns(self):
        print('Proper nouns')
        for num, token in enumerate(self.cleaned_doc):
            if token.pos_ == 'PROPN':
                print(num, token.text, token.dep_)
        print('\n')

    def get_entities(self):
        print('Entities')
        for ent in self.cleaned_doc.ents:
            print(ent.text, ent.start_char, ent.end_char, ent.label_)
        print('\n')

    def get_all_tokens(self):
        print('All Token Info')
        for num, token in enumerate(self.cleaned_doc):
            print(num, token.text, token.pos_, token.dep_, '- head: ', token.head)
        print('\n')

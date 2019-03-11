from engine.operations import LanguageEngine


def process(sentence):
    LanguageEngine.LanguageEngine(words=sentence)


if __name__ == '__main__':
    words = "i wonder could i ever meet barack obama. barack obama seems nice"
    process(sentence=words)

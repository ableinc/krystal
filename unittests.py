from engine.operations import LanguageEngine
from uni import MEMORY_NEWINFORMATION

m = open(MEMORY_NEWINFORMATION, 'w')
m.close()

LanguageEngine.LanguageEngine(words="i wonder could i ever meet barack obama, that would be really cool. "
                                    "barack obama seems nice")

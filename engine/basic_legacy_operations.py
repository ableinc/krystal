import re
import string
import webbrowser
from os import system


class BasicOperations(object):

    class LegacyOperations:
        def __call__(self, search_parameter, search_object):
            if search_parameter == 'open':
                upper = string.capwords(search_parameter)
                results = 'Opening ' + upper
                system('open -a /Applications/{}.app'.format(upper))
                return results
            else:
                nospace = re.sub(r"\s+", '+', search_object)
                finalstringrequest = 'https://www.google.com/search?q=' + nospace + '&ie=UTF-8'
                webbrowser.open_new(finalstringrequest)
                results = 'Searching Google for ' + search_object
                return results
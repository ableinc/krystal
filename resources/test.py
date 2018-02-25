import sys
from os import execl
from pathlib import Path

d = Path(__file__).resolve().parents[1]
print(d)

prefix = ['whats your', 'what is your']
attrib = ['age', 'name', 'eye color']

sample = 'whats your age?'
sample2 = 'can you tell me what is your name?'
sample3 = 'eye color, please?'

# BOOLS ARE COOL
FOUNDIT = True


def restart():
    execl(sys.executable, 'test', __file__, *sys.argv[1:])


num = input('Enter a number > ')
if num.isalnum():
    restart()

# print(helper.requestoptions[0:2])

# if findit(sample):
    # print('True')

# for gx in startrequests or defaultrequests or uniquerequests:
        #     if sentence.startswith(gx):
        #         paramlen = len(gx)
        #         AI.DetailClassifier(gx, ''.join(sentence[paramlen:]))
        #
        # for ux in uniquerequests:
        #     if ux in sentence:
        #         whole = sentence.index(gx) + len(gx)
        #         removed_whole = sentence[whole:]
        #         AI.DetailClassifier(gx, removed_whole)
        #
        #         AI.InformationHandler.search_engine(removed_whole)
        #         # searchExecution(gx, sentence[paramlen:])
        #         # sendinfo(gx, sentence[paramlen:])
        # for ox in uniquerequests:
        #     if ox in sentence:
        #         whole = sentence.index(ox) + len(ox)
        #         sub_whole = sentence[whole:]
        #         if not sub_whole.startswith('your'):
        #             AI.DetailClassifier(ox, sentence[sub_whole:])
        #             # searchExecution(ox, sub_whole)
        #             # sendinfo(ox, sub_whole)
        #         else:
        #             vocalfeedback(res)

# def searchExecution(param, option):
#     if param == 'open ':
#         upper = string.capwords(option)
#         openresults = 'Opening ' + upper
#         vocalfeedback(openresults)
#     elif param in helper.defaultrequests or helper.startrequests:
#         searchresults = 'Searching Google for ' + option
#         webbrowser.open_new(finalstringrequest)
#         vocalfeedback(searchresults)
#     elif param in helper.uniquerequests:
#         # combination = param + option
#         information = AI.DetailClassifier(param, option)
#         information.isanoun('detect')
#         resource = AI.InformationHandler()
#         output = ''.join(resource.search_engine())
#         vocalfeedback(output)
#     backhome()
#     return
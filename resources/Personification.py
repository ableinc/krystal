from os import system

""" THIS FILE IS INTENDED FOR THE PURPOSE OF HOLDING STRINGS (PHRASES) FOR KRYSTAL TO USE, IN A MANNER OF PERSONIFYING
    HER COMMUNICATION WITH USERS. THESE COMMANDS ARE NOT RECOMMENDED FOR ALTERING BUT DUE TO PERSONAL PREFERENCE AND
    ENCOURAGEMENT OF FURTHER LANGUAGE DEVELOPMENT, I AM NOT OPPOSED TO USER MODIFICATION TO THIS FILE. ENJOY AND HAVE
    MANNERS.
"""
# Politeness
Polite_Questions = ["would you like to try again"]
Polite_Statements = ["you look great", "sorry, I didn't recognize you"]
Polite_Greetings = ["hello"]

# Responses
# For Questions

# For Statements

# For Greetings
PG_Response = ["Hello!"]

# User Commands
User_Question = ["Who's that?"]

# Manner Holders
"""
    These hold all the manners, ahh... Wonderful
"""
# Polite Questions
PQ_TryAgain = str(Polite_Questions[0])
# Polite Statements
PS_LookGreat = str(Polite_Statements[0])
PS_SorryNotYou = str(Polite_Statements[1])


UQ_WhosThat = str(User_Question[0])


# DO NOT EDIT BELOW THIS LINE
def complimentcheck(sentence):
    for x in range(0, len(PG_Response)):
        if sentence in Polite_Greetings:
            print(PG_Response[x])
            system('say -v Ava {}'.format(PG_Response[x]))
        else:
            return 1

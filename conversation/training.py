import nltk
from nltk.stem.lancaster import LancasterStemmer
import numpy as np
TF_CPP_MIN_VLOG_LEVEL = 3
import tflearn
import tensorflow as tf
import random
import json
import pickle
import sys
from os.path import join
import time
import logging
from root import EVENT_LOG, NullDevice, ROOT
from engine.push.dailyupdates import DailyUpdates


logging.basicConfig(filename=EVENT_LOG, format='%(asctime)s:%(levelname)s:%(name)s - %(message)s', level=logging.INFO)
logger = logging.getLogger('ConversationTraining')


class EarlyStoppingCallback(tflearn.callbacks.Callback):
    def __init__(self, val_acc_thresh):
        """ Note: We are free to define our init function however we please. """
        self.val_acc_thresh = val_acc_thresh

    def on_epoch_end(self, training_state):
        """ """
        # Apparently this can happen.
        if training_state.val_acc is None: return
        if training_state.val_acc > self.val_acc_thresh:
            logger.info('Accuracy level met early. Stopping iteration.')
            raise StopIteration


early_stopping_cb = EarlyStoppingCallback(val_acc_thresh=0.95)


class Train:
    def __init__(self, personality_json: object = None, conversation_json: object = None, verbose=False):
        self.username = DailyUpdates().get_username()
        self.conversation_json = conversation_json
        self.personality_json = personality_json
        self.verbose = verbose
        self.stemmer = LancasterStemmer()
        self.words = []
        self.classes = []
        self.documents = []
        self.ignore_words = ['?', '!', '.', ',', '"', '$', '&', '*', '@', '(', ')']
        self.model_save_path = join(ROOT, f'conversation/conversation_model.ai')
        self.conv_save_path = join(ROOT, f'conversation/conversation.json')
        self.conv_data_save_path = join(ROOT, f'conversation/conversation_data.ai')
        self.intents = None
        self.preflight_check()

    def preflight_check(self):
        if self.personality_json is not None and self.conversation_json is not None:
            return False, 'Cannot train both models at once.'

        if self.personality_json is not None:
            self.loop_through_personality_json()
        elif self.conversation_json is not None:
            self.loop_through_conversation_json()
        else:
            return False, 'Personality or Conversation json is required for training.'

    def loop_through_personality_json(self):
        # open personality intent file
        intents = json.loads(self.personality_json, encoding='utf-8')
        self.intents = intents
        # loop through each sentence in our intents patterns
        for intent in intents['intents']:
            for pattern in intent['patterns']:
                # tokenize each word in the sentence
                w = nltk.word_tokenize(pattern)
                # add to our words list
                self.words.extend(w)
                # add to documents in our corpus
                self.documents.append((w, intent['tag']))
                # add to our classes list
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

    def loop_through_conversation_json(self):
        # open conversation intent file
        memory = json.loads(self.conversation_json, encoding='utf-8')
        self.intents = memory
        # loop through each sentence in our intents patterns
        for intent in memory['memory']:
            for pattern in intent['patterns']:
                # tokenize each word in the sentence
                w = nltk.word_tokenize(pattern)
                # add to our words list
                self.words.extend(w)
                # add to documents in our corpus
                self.documents.append((w, intent['tag']))
                # add to our classes list
                if intent['tag'] not in self.classes:
                    self.classes.append(intent['tag'])

    def start(self):
        start_time = time.time()
        if self.verbose:
            logger.info("Starting build for {}'s conversation model...".format(self.username.title()))

        # stem and lower each word and remove duplicates
        words = [self.stemmer.stem(w.lower()) for w in self.words if w not in self.ignore_words]
        words = sorted(list(set(words)))

        # remove duplicates
        classes = sorted(list(set(self.classes)))

        if self.verbose:
            logger.info(len(self.documents), "documents")
            logger.info(len(classes), "classes", classes)
            logger.info(len(words), "unique stemmed words", words)

        # create our training data
        training = []
        # create an empty array for our output
        output_empty = [0] * len(classes)

        # training set, bag of words for each sentence
        for doc in self.documents:
            # initialize our bag of words
            bag = []
            # list of tokenized words for the pattern
            pattern_words = doc[0]
            # stem each word
            pattern_words = [self.stemmer.stem(word.lower()) for word in pattern_words]
            # create our bag of words array
            for w in words:
                bag.append(1) if w in pattern_words else bag.append(0)

            # output is a '0' for each tag and '1' for current tag
            output_row = list(output_empty)
            output_row[classes.index(doc[1])] = 1

            training.append([bag, output_row])

        # shuffle our features and turn into np.array
        random.shuffle(training)
        training = np.array(training)
        # create train and test lists
        train_x = list(training[:, 0])
        train_y = list(training[:, 1])

        # reset underlying graph data
        tf.reset_default_graph()
        # Build neural network
        net = tflearn.input_data(shape=[None, len(train_x[0])])
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, 8)
        net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
        net = tflearn.regression(net)

        # Define model and setup tensorboard
        model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')

        # Start training (apply gradient descent algorithm)
        original_stdout = sys.stdout
        sys.stdout = NullDevice()
        model.fit(train_x, train_y, n_epoch=600, batch_size=8, show_metric=True, callbacks=early_stopping_cb)
        sys.stdout = original_stdout

        # save model
        model.save(self.model_save_path)

        if self.verbose:
            logger.info('Saving conversation model data...')
        with open(self.conv_save_path, 'w', encoding='utf-8') as conv_json:
            json.dump(self.intents, conv_json, sort_keys=True, indent=4)

        # save all of our data structures
        conversation_data = pickle.dumps({'words': words, 'classes': classes, 'train_x': train_x, 'train_y': train_y})
        with open(self.conv_data_save_path, 'wb') as conv_json:
            conv_json.write(conversation_data)

        if self.verbose:
            logger.info('Done.')
            logger.info("{}'s model has been saved.".format(self.username.title()))
            logger.info("{}'s data structure has been saved.".format(self.username.title()))
        end_time = time.time()
        if self.verbose:
            logger.info('Training completion time: {} seconds'.format(end_time - start_time))
            logger.info('Program complete. Terminating.')

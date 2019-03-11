#! /usr/bin/env python3
from os import system
from threading import Thread

from pyttsx3 import init


class VerbalFeedback(Thread):
    # Voice: Ava is not available by default, must be downloaded on Mac. Default
    # female voice is Samantha
    daemon = False
    engine = init()
    available_voices = ['com.apple.speech.synthesis.voice.samantha',
                        'com.apple.speech.synthesis.voice.alice',
                        'com.apple.speech.synthesis.voice.anna',
                        'com.apple.speech.synthesis.voice.ava.premium']
    phrase = None
    vocal_tone = None
    voice_choice = None
    speech_rate = None
    volume = None

    def set_variables(self, phrase, vocal_tone, speed, volume):
        self.speech_rate = speed
        self.vocal_tone = vocal_tone
        self.phrase = phrase
        self.voice_choice = None
        self.volume = volume
        # set speech attributes
        self.speech_attributes()

    # noinspection PyTypeChecker
    def get_available_voices(self, detailed=False):
        """
        :param detailed: get a detailed list of available voices (age, gender, etc.)
        :return: prints out the available text-to-speech voices on system
        """
        for voice in self.engine.getProperty('voices'):
            print(voice.id)

        if detailed is True:
            for voice in self.engine.getProperty('voices'):
                print(voice)

    # noinspection PyTypeChecker
    def speech_attributes(self):
        # set default voice
        self.engine.setProperty('voice', self.available_voices[1])

        if self.vocal_tone == 'natural':
            self.setup_voice(speech_rate=self.speech_rate if self.speech_rate is not None else 180, vocal_volume=0.55)
        elif self.vocal_tone == 'anger':
            pass
        elif self.vocal_tone == 'sad':
            pass
        elif self.vocal_tone == 'stern':
            pass
        elif self.vocal_tone == 'annoyed':
            pass
        elif self.vocal_tone == 'frantic':
            pass
        elif self.vocal_tone == 'excited':
            pass
        elif self.vocal_tone == 'misc':
            self.setup_voice(speech_rate=self.speech_rate, vocal_volume=self.volume)
        return

    # noinspection PyTypeChecker
    def setup_voice(self, voice_choice='samantha', speech_rate=None, vocal_volume=None):
        """

        :param voice_choice: if you prefer to change the voice actor (default: Ava)
        :param speech_rate: if you prefer to change the speech rate (default: 200)
        :param vocal_volume: if you prefer to change the speech volume (scale: 1.0)
        :return:
        """
        if voice_choice is not None:
            for x in self.available_voices:
                if voice_choice in x:
                    self.engine.setProperty('voice', x)
            self.voice_choice = voice_choice

        if speech_rate is not None:
            self.engine.setProperty('rate', speech_rate)

        try:
            if vocal_volume is not None:
                self.engine.setProperty('volume', vocal_volume)
        except:
            system('osascript -e "set volume output volume {}"'.format(str(int(vocal_volume * 100))))
        return

    def run(self):
        print(self.phrase)
        try:
            self.engine.say(self.phrase)
            self.engine.runAndWait()
        except:
            system(f'say -v {self.voice_choice} -r {self.speech_rate} {self.phrase}')


def verbal_feedback(phrase, vocal_tone='natural', vocal_speed=None, vocal_volume=None):
    """
    Send phrases to Krystal for speech and console logging. Based on vocal_tone you can determine
    how you would like krystal to respond; based on speed and volume
    :param phrase: the phrase to be spoken
    :param vocal_tone: the mood/tone/attitude in which the phrase will be spoken
    :param vocal_speed: speed at which voice should speak; int
    :param vocal_volume: volume at which to speak
    :return:
    """
    if not isinstance(phrase, str) or not isinstance(vocal_tone, str):
        raise AttributeError('phrase and attribute_settings must be String')

    if vocal_tone == 'misc' and vocal_speed is None and vocal_volume is None:
        raise NotImplementedError('if vocal tone is `misc` then speed and volume must be set')

    vf = VerbalFeedback()
    vf.set_variables(phrase=phrase, vocal_tone=vocal_tone, speed=vocal_speed, volume=vocal_volume)
    vf.start()

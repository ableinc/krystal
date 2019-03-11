import collections
import logging
import os
import os.path
import queue
import wave
from datetime import datetime

import deepspeech
import numpy as np
import pyaudio
import webrtcvad
from halo import Halo

logging.basicConfig(level=20)
LISTEN = False


def stop_listening():
    global LISTEN
    LISTEN = False


def start_listening():
    global LISTEN
    LISTEN = True


def handle_text(msg, verbose=True):
    if verbose:
        print(f'Speech is {"online" if LISTEN else "offline"}')
    print(f'Recognized: {msg}')


class Audio(object):
    """Streams raw audio from microphone. Data is received
    in a separate thread, and stored in a buffer, to be read from."""

    FORMAT = pyaudio.paInt16
    RATE = 16000
    CHANNELS = 1
    BLOCKS_PER_SECOND = 50
    BLOCK_SIZE = int(RATE / float(BLOCKS_PER_SECOND))

    def __init__(self, callback=None):
        def proxy_callback(in_data, frame_count, time_info, status):
            callback(in_data)
            return (None, pyaudio.paContinue)

        if callback is None: callback = lambda in_data: self.buffer_queue.put(in_data)
        self.buffer_queue = queue.Queue()
        self.sample_rate = self.RATE
        self.block_size = self.BLOCK_SIZE
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format=self.FORMAT,
                                   channels=self.CHANNELS,
                                   rate=self.sample_rate,
                                   input=True,
                                   frames_per_buffer=self.block_size,
                                   stream_callback=proxy_callback)
        self.stream.start_stream()

    def read(self):
        """Return a block of audio data, blocking if necessary."""
        return self.buffer_queue.get()

    def destroy(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    frame_duration_ms = property(lambda self: 1000 * self.block_size // self.sample_rate)

    def write_wav(self, filename, data):
        logging.info("write wav %s", filename)
        wf = wave.open(filename, 'wb')
        wf.setnchannels(self.CHANNELS)
        # wf.setsampwidth(self.pa.get_sample_size(FORMAT))
        assert self.FORMAT == pyaudio.paInt16
        wf.setsampwidth(2)
        wf.setframerate(self.sample_rate)
        wf.writeframes(data)
        wf.close()


class VADAudio(Audio):
    """Filter & segment audio with voice activity detection."""

    def __init__(self, aggressiveness=3):
        super().__init__()
        self.vad = webrtcvad.Vad(aggressiveness)

    def frame_generator(self):
        """Generator that yields all audio frames from microphone."""
        while True:
            yield self.read()

    def vad_collector(self, padding_ms=300, ratio=0.75, frames=None):
        """Generator that yields series of consecutive audio frames comprising each utterence, separated by yielding a single None.
            Determines voice activity by ratio of frames in padding_ms. Uses a buffer to include padding_ms prior to being triggered.
            Example: (frame, ..., frame, None, frame, ..., frame, None, ...)
                      |---utterence---|        |---utterence---|
        """
        if frames is None: frames = self.frame_generator()
        num_padding_frames = padding_ms // self.frame_duration_ms
        ring_buffer = collections.deque(maxlen=num_padding_frames)
        triggered = False

        for frame in frames:
            is_speech = self.vad.is_speech(frame, self.sample_rate)

            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if num_voiced > ratio * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        yield f
                    ring_buffer.clear()

            else:
                yield frame
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > ratio * ring_buffer.maxlen:
                    triggered = False
                    yield None
                    ring_buffer.clear()


def speech_recognizer():
    text = ''
    obj = {
        'vad_aggressiveness': 3,
        'nospinner': True,
        'model': os.path.abspath(os.curdir) + '/models/speech_recognition',
        'alphabet': 'alphabet.txt',
        'lm': 'lm.binary',
        'trie': 'trie',
        'n_features': 26,
        'n_context': 9,
        'lm_alpha': 0.75,
        'lm_beta': 1.85,
        'beam_width': 500,
        'savewav': False
    }
    configurations = RealDict(obj)

    # Load DeepSpeech models
    if os.path.isdir(configurations.model):
        model_dir = configurations.model
        configurations.model = os.path.join(model_dir, 'output_graph.rounded.pbmm')
        configurations.alphabet = os.path.join(model_dir, configurations.alphabet)
        configurations.lm = os.path.join(model_dir, configurations.lm)
        configurations.trie = os.path.join(model_dir, configurations.trie)

    print('Initializing models...')
    logging.info("ARGS.models: %s", configurations.model)
    logging.info("ARGS.alphabet: %s", configurations.alphabet)
    model = deepspeech.Model(configurations.model, configurations.n_features, configurations.n_context,
                             configurations.alphabet, configurations.beam_width)
    if configurations.lm and configurations.trie:
        logging.info("ARGS.lm: %s", configurations.lm)
        logging.info("ARGS.trie: %s", configurations.trie)
        model.enableDecoderWithLM(configurations.alphabet, configurations.lm, configurations.trie,
                                  configurations.lm_alpha, configurations.lm_beta)

    # Start audio with VAD
    vad_audio = VADAudio(aggressiveness=configurations.vad_aggressiveness)
    print("Speech Online")
    frames = vad_audio.vad_collector()

    # Stream from microphone to DeepSpeech using VAD
    spinner = None
    if not configurations.nospinner: spinner = Halo(spinner='line')
    stream_context = model.setupStream()
    wav_data = bytearray()
    for frame in frames:
        if frame is not None:
            if spinner: spinner.start()
            logging.debug("streaming frame")
            model.feedAudioContent(stream_context, np.frombuffer(frame, np.int16))
            if configurations.savewav: wav_data.extend(frame)
        else:
            if spinner: spinner.stop()
            logging.debug("end utterence")
            if configurations.savewav:
                vad_audio.write_wav(
                    os.path.join(configurations.savewav, datetime.now().strftime("savewav_%Y-%m-%d_%H-%M-%S_%f.wav")),
                    wav_data)
                wav_data = bytearray()
            text = model.finishStream(stream_context)
            if text is not None or text is not '':
                break
            else:
                stream_context = model.setupStream()
    Audio().destroy()
    return text


class RealDict(dict):
    def __init__(self, *args, **kwargs):
        super(RealDict, self).__init__(*args, **kwargs)
        self.__dict__ = self

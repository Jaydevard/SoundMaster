import threading
from queue import Queue
import librosa
import os
import sys


class Feature:
    def __init__(self, audio_thread=None, **kwargs):
        self.__audio_buffer = []
        self.audio_thread = audio_thread
        self.fft_analysis = kwargs.get('fft_analysis', False)
        self.fs = kwargs.get('fs', 44100)
        self.frame_rate = kwargs.get('frame_rate', 1024*2)
        self.is_live = kwargs.get('is_live', False)

    def update_buffer(self, buffer_input):
        self.__audio_buffer = buffer_input

    def zero_crossing_rate(self, hop_length=512):
        cross_rate = 0
        if len(self.__audio_buffer) == 0:
            return cross_rate
        cross_rate = librosa.feature.zero_crossing_rate(self.__audio_buffer,
                                                        frame_length=self.frame_rate,
                                                        hop_length=hop_length)
        print(cross_rate)
        return cross_rate

    def spectral_centroid(self, buffer_size=2048, hop_length=512):
        cent = librosa.feature.spectral_centroid(self.__audio_buffer,
                                                 sr=self.fs,
                                                 n_fft=buffer_size,
                                                 hop_length=hop_length)
        print(cent)
        return cent


class AudioThread(threading.Thread):
    def __init__(self, _method, flag):
        threading.Thread.__init__(self)
        self.queue = Queue()
        self.daemon = True
        self.method = _method
        self._isRunning = flag

    def run(self):
        while self._isRunning:
            val = self.queue.get()
            self.method(val)
        return

    def put(self, val):
        self.queue.put(val)


if __name__ == '__main__':
    pass





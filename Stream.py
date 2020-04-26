# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 00:14:30 2020

@author: Jaydev Madub
"""


import pyaudio
import numpy as np
import threading
import pyo
from audio_plotter import AudioPlotter


class StreamManager:
    
    def __init__(self, **kwargs):
        self.__port = pyaudio.PyAudio()
        self._BUFF_SIZE = 1024*2
        self._FORMAT = pyaudio.paFloat32
        self.__default_device = pyo.pa_get_default_input()
        self._NCHANNELS = StreamManager.get_num_channels(self.__default_device)
        self._RATE = 44100
        self.__DEVICE_INFO = ['index','name', 'hostApi']
        self._audio_devices = []
        self.get_available_devices()
        
    def open_stream(self, _input=True, _output=False, **kwargs):
        channels = kwargs.get('nchannels', self._NCHANNELS)
        buff_size = kwargs.get('buffer_size', self._BUFF_SIZE)
        _format = kwargs.get('format', self._FORMAT)
        rate = kwargs.get('rate', self._RATE)
        loopback = kwargs.get('loopback', False)
        stream = self.__port.open(format=_format,
                                  channels=channels,
                                  rate=rate,
                                  input=_input,
                                  output=_output,
                                  frames_per_buffer=buff_size,
                                  as_loopback=loopback)
        
        return stream

    def get_available_devices(self):
        """
        get the active IO devices from the PC environment
        """
        for i in range(0, self.__port.get_device_count()):
            device = []
            info = self.__port.get_device_info_by_index(i)
            device.append(info["index"])
            device.append(info["name"])
            device.append(self.__port.get_host_api_info_by_index(info["hostApi"])["name"])
            self._audio_devices.append(dict(zip(self.__DEVICE_INFO,device)))
    
    @staticmethod
    def get_num_channels(device_index):
        maxouts = pyo.pa_get_output_max_channels(device_index)
        maxins = pyo.pa_get_input_max_channels(device_index)
        if maxouts >= 2 and maxins >= 2:
            return 2
        else:
            return 1
        
    @staticmethod
    def output_devices():
        return pyo.pa_get_output_devices()
    
    @staticmethod
    def input_devices():
        return pyo.pa_get_input_devices()
    
    @staticmethod
    def list_active_devices():
        pyo.pa_list_devices()
        
    @staticmethod
    def devices_from_host(_input):
        print("getting it")
        return pyo.pa_get_default_devices_from_host(_input)
    

class Listener(StreamManager):

    def __init__(self, **kwargs):
        super(Listener, self).__init__(**kwargs)
        self.__active_stream = object
        self.__state = False
        self._default_device = pyo.pa_get_default_output()
        self.receiver_flag = True

    def start(self, **kwargs):
        device = kwargs.get('device', self._default_device)
        active_device_info = self._audio_devices[device]
        if active_device_info['hostApi'].find("WASAPI") == -1:
            if kwargs.get('loopback'):
                print("Loopback only available for wasapi")
                return
        try:
            self.__active_stream = self.open_stream(**kwargs)
        except (TypeError, ValueError) as e:
            raise e
        self.__state = True

    def receive_data(self, receiver_thread, flag):
        self.receiver_flag = flag

        def _read():
            while flag:
                buffer_data = self.__active_stream.read(self._BUFF_SIZE)
                decoded_data = np.frombuffer(buffer_data, dtype=np.float32)[::2]
                receiver_thread.put(decoded_data)
            return
        stream_thread = threading.Thread(target=_read)
        stream_thread.start()

    def stop_listening(self):
        self.__state = False
        self.receiver_flag = False
        

if __name__ == '__main__':
    listener = Listener()
    listener.start(loopback=True, device=5, nchannels=2)
    plotter = AudioPlotter(listener._BUFF_SIZE, listener._RATE, spectogram=True)
    receiver_thread, flag = plotter.com()
    listener.receive_data(receiver_thread, flag)
    plotter.start_plotting(10)

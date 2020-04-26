# -*- coding: utf-8 -*-
"""
Created on Mon Apr 13 23:54:04 2020

@author: Jaydev Madub
"""

import pyaudio 
import pyo
import scipy
import os
import pydub
from tkinter import filedialog




class SoundIO(pyo.Server):
    def __init__(self, **kwargs):
        
        pass
        
    def output_music(self, **kwargs):
        self._server = pyo.Server(**kwargs)
        
        
    
        
        
        

sound_io = SoundIO()
sound_io.output_music(duplex=0)
# boot the server
sound_io._server.boot()
# get the file
file = filedialog.askopenfilename()
file_path = os.path.abspath(file) 
try:
    pyo.SfPlayer(file_path, mul=0.3)
except TypeError:
    sound = pydub.AudioSegment.from_mp3(file_path)
    sound.export((os.path.dirname(file_path)+"/test.wav"), format="wav")
    file = filedialog.askopenfilename()
    file_path = os.path.abspath(file) 
    sf = pyo.SfPlayer(file_path, mul=0.3).out()
    sound_io._server.gui(locals())

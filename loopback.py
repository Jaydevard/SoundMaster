# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 15:30:51 2020

@author: Jaydev Madub
"""

import threading
import pyaudio
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from scipy.fftpack import fft

BUFF_DATA = []

    
# Code to run the figure spectogram
# fig = plt.figure()
# ax = fig.add_subplot(1, 1, 1)

# listener1 = Listener()
# listener1.active_devices()
# print(listener1._port.get_device_count())
# listener1._active_device_index = 5
# listener1.start_stream()
# listener1._stream_start = True
# listener1.receive_data()

# _t = np.arange(0, 8192)
# print(_t)
def animate(i):
    
    if len(BUFF_DATA) == 0:
        return
    fft_data = BUFF_DATA
    ax.clear()
    ax.set_ylim([-1, 1])
    ax.plot(_t, fft_data)


# ani = FuncAnimation(fig, animate, interval=7)
# plt.show()




    
    



    
    

        
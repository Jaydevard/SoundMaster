# -*- coding: utf-8 -*-
"""
Created on Thu Apr 16 16:04:29 2020

@author: Jaydev Madub
"""
from pyqtgraph.Qt import QtGui, QtCore
import numpy as np
import pyqtgraph as pg
import sys
from utils import AudioThread
from librosa.feature import melspectrogram
from librosa import power_to_db
from scipy.signal import stft
from PyQt5 import QtWidgets



class HistoSpec:
    def __init__(self, win, pos, fs, **kwargs):
        """
        :param win: PyQt window
        :param pos: tuple (row, col), if unspecified, then (0,0)
        :param kwargs: color: str, color of the histogram plot. eg. 'r'-red
                       window_length: int, window length for fft, unspecified = N/5
                       refresh_rate: int, refresh rate of graph, unspecified = 10 ms
                       N_length: int, number of data points for buffer, unspecified = len(buffer)

        """
        self.fs = fs
        self.data_points = []
        self.color = kwargs.get('color', 'r')
        self.N_length = kwargs.get('N_length', len(self.data_points))
        self.window_length = kwargs.get('window_length', self.N_length // 5)
        self.refresh_rate = kwargs.get('refresh_rate', 10)
        self.win = win
        self.pos = pos
        self.__x_data = []
        self.__y_data = []
        self.__histogram_width = 0.5
        self.__barGraphItem = object
        self.__barGraph = object
        self.color = pg.mkBrush([255, 255, 255, 255])
        pass

    def update_plot(self):
        self.remove_plot()
        self.calculate_stft()
        if len(self.__x_data) == 0:
            return
        self.__barGraphItem = pg.BarGraphItem(x=self.__x_data,
                                              height=self.__y_data,
                                              width=self.__histogram_width,
                                              brush=self.color)
        self.__barGraph = self.win.addItem(self.__barGraphItem)

    def remove_plot(self):
        self.win.clear()

    def set_data(self, x_data):
        self.__x_data = x_data

    def calculate_stft(self):
        self.__x_data, t, zxx = stft(self.__x_data, fs=self.fs, nperseg=len(self.__x_data), return_onesided=True)
        self.__y_data = np.average(np.abs(zxx), axis=1)*self.fs
        self.__histogram_width = int(self.__x_data[1])-2


class AudioPlotter:
    def __init__(self, buffer_size, rate, spectogram=False, mel=False):
        self.traces = dict()
        self.buffer = object
        self.buffer_size = buffer_size
        self.flag = True
        self.receiver_thread = AudioThread(self.update_buffer, self.flag)
        pg.setConfigOptions(antialias=True)
        self.enable_spectogram = spectogram
        self.enable_mel = mel
        self.RATE = rate
        self.refresh_rate = 10

        # QtGui.Application.setGraphicsSystem('raster')

        # Create Qt MainWindow
        self.__app = QtGui.QApplication([])
        self.__window = QtGui.QMainWindow()
        self.centralwidget = QtWidgets.QWidget(self.__window)
        self.centralwidget.setObjectName("centralwidget")

        # Create a frame for time-series and Spectogram plots
        self.plot_frame = QtWidgets.QFrame(self.__window)
        self.plot_frame.setGeometry(QtCore.QRect(9, -1, 771, 711))
        self.plot_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.plot_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.plot_frame.setObjectName("plotframe")

        # Create the PLotWidget
        self.plot_widget = pg.PlotWidget(self.plot_frame)
        self.plot_widget.setGeometry(QtCore.QRect(-5, 1, 781, 711))
        self.plot_widget.setObjectName('plotwidget')

        # Create the second frame for BPM, ZCR and SDC
        self.dynamics_frame = QtWidgets.QFrame(self.centralwidget)
        self.dynamics_frame.setGeometry(QtCore.QRect(779, -1, 401, 701))
        self.dynamics_frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.dynamics_frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.dynamics_frame.setObjectName("dynamicsframe")

        # LCD display for BPM
        self.bpm_display = QtWidgets.QLCDNumber(self.dynamics_frame)
        self.bpm_display.setGeometry(QtCore.QRect(779, -1, 401, 701))
        self.bpm_display.setObjectName('bpmdisplay')

        # LCD display for ZCR
        self.zcr_display = QtWidgets.QLCDNumber(self.dynamics_frame)
        self.zcr_display.setGeometry(QtCore.QRect(263, 102, 121, 51))
        self.zcr_display.setObjectName('zcrdisplay')

        # LCD display for SDC
        self.sdc_display = QtWidgets.QLCDNumber(self.dynamics_frame)
        self.sdc_display.setGeometry(QtCore.QRect(273, 182, 111, 51))
        self.sdc_display.setObjectName('SDCdisplay')

        # label for BPM
        self.bpm_label = QtWidgets.QLabel(self.dynamics_frame)
        self.bpm_label.setGeometry(QtCore.QRect(150, 20, 111, 41))
        self.bpm_label.setObjectName('bpmlabel')
        self.bpm_label.setText("BPM")

        # label for ZCR
        self.zcr_label = QtWidgets.QLabel(self.dynamics_frame)
        self.zcr_label.setGeometry(QtCore.QRect(130, 110, 111, 31))
        self.zcr_label.setObjectName('zcrlabel')
        self.bpm_label.setText("Zero Crossing Rate")

        # label for SDC
        self.sdc_label = QtWidgets.QLabel(self.dynamics_frame)
        self.sdc_label.setGeometry(QtCore.QRect(104, 200, 141, 20))
        self.sdc_label.setObjectName('sdclabel')
        self.sdc_label.setText("Spectral Density Centre")

        # List View for Audio Channels
        self.audio_channels_list_view = QtWidgets.QListView(self.dynamics_frame)
        self.audio_channels_list_view.setGeometry(QtCore.QRect(75, 321, 321, 361))
        self.audio_channels_list_view.setObjectName('audiochannelslistview')

        if self.enable_spectogram:
            self.waveform = pg.PlotItem(title='Waveform')
            self.plot_widget.addItem(self.waveform)
            self.__histogram_window = pg.PlotItem(title="Spectogram")
            self.plot_widget.addItem(self.__histogram_window)
            self.__histogram_window.setYRange(0, 200, padding=0)
            self.histogram_spectogram = HistoSpec(win=self.__histogram_window,
                                                  pos=(0, 0),
                                                  fs=self.RATE)
            if self.enable_mel:
                self.mel = self.plot_widget.addPlot(title='Mel', row=1, col=1, colspan=1)
        elif self.enable_mel:
            self.mel = self.plot_widget.addPlot(title='Mel', row=1, col=0, rowspan=1)
        else:
            self.waveform = self.plot_widget.addPlot(title='Waveform', row=0, col=0)

        # Arrange the x-axis for the plots
        self.x = np.arange(0, 2 * buffer_size, 2)

    def _start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            self.__window.show()
            QtGui.QApplication.instance().exec_()
    
    def set_data(self, name, dataset_x, dataset_y):
        if name in self.traces:
            self.traces[name].setData(dataset_x, dataset_y)

        elif name == 'waveform':
            self.traces[name] = self.waveform.plot(pen='c', width=3)
            self.waveform.setYRange(-0.1, 0.1, padding=0)
            self.waveform.setXRange(0, self.buffer_size, padding=0.05)
        elif name == 'spectrum':
            self.histogram_spectogram.set_data(dataset_x)
            self.histogram_spectogram.update_plot()
        elif name == 'melspectogram':
            return

    def compute_mel(self):
        # len buffer = 2048
        S = melspectrogram(y=self.buffer, sr=self.RATE*2, hop_length=len(self.buffer))
        S_dB = power_to_db(S, ref=np.max)
        S_dB = np.array(np.reshape(S_dB, newshape=-1))
        return S_dB

    def update(self):
        self.set_data(dataset_x=self.x, dataset_y=self.buffer, name='waveform')
        if self.enable_spectogram:
            self.set_data(dataset_x=self.buffer, dataset_y=self.x, name='spectrum')
        if self.enable_mel:
            mel_data = self.compute_mel()
            self.set_data(dataset_x=self.x, dataset_y=mel_data, name='mel')

    def update_buffer(self, buffer):
        self.buffer = buffer

    def com(self):
        return self.receiver_thread, self.flag

    def start_plotting(self, refresh_rate):
        self.receiver_thread.start()
        self.refresh_rate = refresh_rate
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start(refresh_rate)
        self._start()
        pass


if __name__ == '__main__':
    pass


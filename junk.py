import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtGui
from scipy.signal import stft

win = pg.plot()
bg1 = object


def histogram(window, n_data_points, y_values):
    global bg1
    histogram_width = n_data_points//n_data_points
    brush = 'r'
    window.setWindowTitle('check histogram')
    x_values = np.arange(n_data_points)
    bg1 = pg.BarGraphItem(x=x_values,
                          height=y_values,
                          width=histogram_width,
                          brush=brush)

    window.addItem(bg1)


if __name__ == '__main__':
    import sys

    def update():
        try:
            win.removeItem(bg1)
        except:
            pass
        n_data_points = 500
        y_values = np.random.rand(1, n_data_points).flatten()
        fs = 44100
        f, t, zxx = stft(y_values, fs, nperseg=len(y_values), return_onesided=True)
        t = t*44100
        abs = np.average(np.abs(zxx), axis=1)
        print(len(abs))
        histogram(window=win,
                  n_data_points=len(f),
                  y_values=f)
        pass
    timer = QtCore.QTimer()
    timer.timeout.connect(update)
    timer.start(2000)
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()


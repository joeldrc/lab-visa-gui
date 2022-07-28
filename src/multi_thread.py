#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Joel Daricou 07/2022

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

import traceback, sys
import time


class MeasureSignals(QObject):
    '''
    Defines the signals available from a running instr thread.

    Supported signals are:

    finished
        No data

    error
        tuple (exctype, value, traceback.format_exc() )

    result
        object data returned from processing, anything

    progress
        int indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Measure(QRunnable):
    '''
    Measure thread

    Inherits from QRunnable to handler instr thread setup, signals and wrap-up.

    :param callback: The function callback to run on this instr thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Measure, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = MeasureSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

        self.threadpool = QThreadPool()
        # max thread to 1, if busy wait
        self.threadpool.setMaxThreadCount(1)

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''
        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


if __name__ == "__main__": 

    class MainWindow(QMainWindow):
        def __init__(self, *args, **kwargs):
            super(MainWindow, self).__init__(*args, **kwargs)
            self.counter = 0

            layout = QVBoxLayout()
            self.l = QLabel("Start")
            b = QPushButton("DANGER!")
            b.pressed.connect(self.thread)
            layout.addWidget(self.l)
            layout.addWidget(b)
            w = QWidget()
            w.setLayout(layout)
            self.setCentralWidget(w)
            self.show()

            self.timer = QTimer()
            self.timer.setInterval(1000)
            self.timer.timeout.connect(self.recurring_timer)
            self.timer.start()

        def progress_fn(self, n):
            print("%d%% done" % n)

        def execute_this_fn(self, progress_callback):
            for n in range(0, 5):
                time.sleep(1)
                progress_callback.emit(n*100/4)
            return "Done."

        def print_output(self, s):
            print(s)

        def thread_complete(self):
            print("THREAD COMPLETE!")

        def thread(self):
            # Pass the function to execute
            instr = Measure(self.execute_this_fn) # Any other args, kwargs are passed to the run function
            instr.signals.result.connect(self.print_output)
            instr.signals.finished.connect(self.thread_complete)
            instr.signals.progress.connect(self.progress_fn)

            # Execute
            instr.threadpool.start(instr)

        def recurring_timer(self):
            self.counter +=1
            self.l.setText("Counter: %d" % self.counter)


    app = QApplication([])
    window = MainWindow()
    app.exec()
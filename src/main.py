# -*- coding: utf-8 -*-

import settings

from user_gui import *
from multi_thread import*

import time
from time import gmtime, strftime

import numpy as np
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


#==============================================================================#
def file_open(self):
    name = QtWidgets.QFileDialog.getOpenFileName(MainWindow, 'Open File')  # Returns a tuple
    #print(name)  # For debugging
    if len(name[0]) > 0:
        with open(name[0], 'r') as file:
            text = file.read()
            self.textEdit.setText(text)

def file_save(self):
    name = QtWidgets.QFileDialog.getSaveFileName(MainWindow, 'Save File')  # Returns a tuple
    #print(name)  # For debugging
    if len(name[0]) > 0:
        with open(name[0], 'w') as file:
            #text = self.textEdit.toPlainText()  # Plain text without formatting
            text = self.textEdit.toHtml()  # Rich text with formatting (font, color, etc.)
            file.write(text)

def file_quit(self):
    decision = QtWidgets.QMessageBox.question(MainWindow, 'Question',
                   'Sure to quit?',
                   QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No)
    if decision == QtWidgets.QMessageBox.Yes:
        sys.exit()

def edit_font(self):  # Applies on all text
    font = self.textEdit.font()  # Get the currently used font
    newfont, valid = QtWidgets.QFontDialog.getFont(font)
    if valid:
        self.textEdit.setFont(newfont)

def edit_color(self):  # Applies on selected text only
    color = self.textEdit.textColor()
    newcolor = QtWidgets.QColorDialog.getColor(color)
    if newcolor.isValid():
        self.textEdit.setTextColor(newcolor)

def enlarge_window(self):
    if self.checkBox.isChecked():
        MainWindow.setGeometry(100, 100, 600, 400)
        MainWindow.setWindowTitle("PyQT tuts!")
        """
        import os
        scriptDir = os.path.dirname(os.path.realpath(__file__))
        MainWindow.setWindowIcon(QtGui.QIcon(scriptDir + os.path.sep + 'images/icon.ico'))
        """
        from PyQt5.QtWidgets import QStyleFactory
        app.setStyle(QStyleFactory.create('Fusion'))
    else:
        MainWindow.setGeometry(100, 100, 400, 300)

#==============================================================================#
def check_input(self):
    self.actionOpen.triggered.connect(self.file_open)
    self.actionSave.triggered.connect(self.file_save)
    self.actionQuit.triggered.connect(self.file_quit)
    self.actionFont.triggered.connect(self.edit_font)
    self.actionColor.triggered.connect(self.edit_color)

    self.connectButton.clicked.connect(self.connect_instrument)

    self.checkBox.stateChanged.connect(self.enlarge_window)
    self.addTrace.clicked.connect(self.update_progressBar)
    self.removeTrace.clicked.connect(self.update_progressBar)

def connect_instrument(self):
    self.measure_thread = Measure_thread(self.instrumentAddress.text())

    self.instrument_timer = QtCore.QTimer()
    self.instrument_timer.timeout.connect(self.instrument_refresh)
    self.instrument_timer.start(1000)

    self.progressBar.setValue(0)


#==============================================================================#
def instrument_refresh(self):
    try:
        self.remoteConnectionLabel.setText(self.measure_thread.instrument_info)
        self.update_plot()
        self.progressBar.setValue(100)
    except Exception as e:
        print(e)

def update_time(self):
    self.timeLabel.setText(strftime("%d %b %Y %H:%M:%S", gmtime()))
    self.timer = QtCore.QTimer()
    self.timer.timeout.connect(self.update_time)
    self.timer.start(1000)

def update_progressBar(self, value=0):
    self.progressBar.setValue(value)

#==============================================================================#
def create_canvas(self):
    """
    static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
    self.plotTest.addWidget(static_canvas)
    MainWindow.addToolBar(NavigationToolbar(static_canvas, MainWindow))

    self._static_ax = static_canvas.figure.subplots()
    t = np.linspace(0, 10, 501)
    self._static_ax.plot(t, np.tan(t), ".")
    """

    dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
    self.plotTest.addWidget(dynamic_canvas)
    self.plotTest.addWidget(NavigationToolbar(dynamic_canvas, MainWindow))

    self._dynamic_ax = dynamic_canvas.figure.subplots()
    self._timer = dynamic_canvas.new_timer(
        100, [(self.update_canvas, (), {})])
    self._timer.start()

def update_canvas(self):
    self._dynamic_ax.clear()
    t = np.linspace(0, 10, 101)
    # Shift the sinusoid as a function of time.
    self._dynamic_ax.plot(t, np.sin(t + time.time()))
    self._dynamic_ax.figure.canvas.draw()


#==============================================================================#
plot_names = [[['S21 - delay', 'GHz', 'nS'],
               ['S21 - dB Mag', 'GHz', 'dB'],
               ['S11 - SWR', 'GHz', 'mU'],
               ['S11 - SWR', 'GHz', 'mU'],
               ['S11 - TDR', 'ns', 'mU']],

              [['S11 - TDR', 'x', 'y'],
               ['S11 - TDR', 'x', 'y']]]

figure_names = [['Flanges'],
                ['Pick-Up']]


def create_plot(self):
    number_of_plots = len(plot_names)

    self.plot = [[] for i in range(number_of_plots)]
    self.fig = [[] for i in range(number_of_plots)]
    self.canvas = [[] for i in range(number_of_plots)]
    self.toolbar = [[] for i in range(number_of_plots)]

    # initialize fig
    for i in range(number_of_plots):
        self.fig[i] =Figure(figsize=(12,7))

    # Figures
    for index in range(number_of_plots):
        subplot_number = len(plot_names[index])
        for i in range(subplot_number):
            # auto adapt plot number
            subplot_columns = (subplot_number // 3) + (subplot_number % 3)
            subplot_rows = subplot_number // 2
            subplot = self.fig[index].add_subplot(subplot_rows, subplot_columns, i + 1)
            self.plot[index].append(subplot)

    # auto adj
    for i in range(number_of_plots):
        self.fig[i].tight_layout()

    # Canvas & toolbar
    thisFigure = FigureCanvas(self.fig[0])
    self.plotTest_2.addWidget(thisFigure)
    self.plotTest_2.addWidget(NavigationToolbar(thisFigure, MainWindow))

    thisFigure = FigureCanvas(self.fig[1])
    self.plotTest_3.addWidget(thisFigure)
    self.plotTest_3.addWidget(NavigationToolbar(thisFigure, MainWindow))


def update_plot(self):
    # return wich test you have selected
    channel_number = len(self.measure_thread.measures)
    #selected_frame_number = self.measure_thread.test_number
    selected_frame_number = 1

    xValue = []
    yValue = []

    try:
        for i in range(channel_number):
            x, y = self.measure_thread.measures[i]
            xValue.append(x)
            yValue.append(y)
            # clean plot line
            self.plot[selected_frame_number][i].clear()
            # set data on plot
            self.plot[selected_frame_number][i].plot(xValue[i], yValue[i])
        """
        if self.plot_saveRef == True:
            self.xRef = xValue
            self.yRef = yValue
            self.plot_saveRef = False

        if self.plot_reference == True:
            for i in range(channel_number):
                self.plot[selected_frame_number][i].plot(self.xRef[i], self.yRef[i])
        """
    except Exception as e:
        print(e)

    # Set names on plot
    for i in range(len(plot_names[selected_frame_number])):
        self.plot[selected_frame_number][i].set_title(plot_names[selected_frame_number][i][0])
        self.plot[selected_frame_number][i].set_xlabel(plot_names[selected_frame_number][i][1])
        self.plot[selected_frame_number][i].set_ylabel(plot_names[selected_frame_number][i][2])
        #self.plot[selected_frame_number][i].grid()

    # autoadapt
    self.fig[selected_frame_number].tight_layout()
    # update plot
    #self.canvas[selected_frame_number].draw()

    # markers
    #Single_marker(self.others_frame, self.canvas[selected_frame_number], self.plot[selected_frame_number], xValue, yValue, len(plot_names[selected_frame_number]), self.plot_markers)


#==============================================================================#
Ui_MainWindow.check_input = check_input
Ui_MainWindow.file_open = file_open
Ui_MainWindow.file_save = file_save
Ui_MainWindow.file_quit = file_quit
Ui_MainWindow.edit_font = edit_font
Ui_MainWindow.edit_color = edit_color
Ui_MainWindow.enlarge_window = enlarge_window

Ui_MainWindow.connect_instrument = connect_instrument

Ui_MainWindow.instrument_refresh = instrument_refresh
Ui_MainWindow.update_time = update_time
Ui_MainWindow.update_progressBar = update_progressBar

Ui_MainWindow.create_canvas = create_canvas
Ui_MainWindow.update_canvas = update_canvas

Ui_MainWindow.create_plot = create_plot
Ui_MainWindow.update_plot = update_plot


#==============================================================================#
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    #MainWindow.setWindowTitle(settings.__logo__ + " - " + settings.__title__ + " - " + settings.__version__)
    #MainWindow.setWindowIcon(QtGui.QIcon('images/icon.ico'))
    ui.update_time()
    ui.check_input()
    ui.create_canvas()
    ui.create_plot()
    MainWindow.show()
    sys.exit(app.exec_())

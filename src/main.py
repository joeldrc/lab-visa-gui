# -*- coding: utf-8 -*-

import settings

from user_gui import *
from vna_scpi import *

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
    else:
        MainWindow.setGeometry(100, 100, 400, 300)

#==============================================================================#
def check_input(self):
    self.actionOpen.triggered.connect(self.file_open)
    self.actionSave.triggered.connect(self.file_save)
    self.actionQuit.triggered.connect(self.file_quit)
    self.actionFont.triggered.connect(self.edit_font)
    self.actionColor.triggered.connect(self.edit_color)
    self.checkBox.stateChanged.connect(self.enlarge_window)

    self.addTrace.clicked.connect(self.update_progressBar)
    self.removeTrace.clicked.connect(self.update_progressBar)

def update_time(self):
    self.timeLabel.setText(strftime("%d %b %Y %H:%M:%S", gmtime()))

    self.timer = QtCore.QTimer()
    self.timer.timeout.connect(self.update_time)
    self.timer.start(1000)

def update_progressBar(self):
    self.progressBar.setValue(100)

#==============================================================================#
def create_canvas(self):
    static_canvas = FigureCanvas(Figure(figsize=(5, 3)))
    self.plotTest.addWidget(static_canvas)
    MainWindow.addToolBar(NavigationToolbar(static_canvas, MainWindow))

    dynamic_canvas = FigureCanvas(Figure(figsize=(5, 3)))
    self.plotTest.addWidget(dynamic_canvas)
    MainWindow.addToolBar(QtCore.Qt.BottomToolBarArea, NavigationToolbar(dynamic_canvas, MainWindow))

    self._static_ax = static_canvas.figure.subplots()
    t = np.linspace(0, 10, 501)
    self._static_ax.plot(t, np.tan(t), ".")

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
Ui_MainWindow.check_input = check_input
Ui_MainWindow.file_open = file_open
Ui_MainWindow.file_save = file_save
Ui_MainWindow.file_quit = file_quit
Ui_MainWindow.edit_font = edit_font
Ui_MainWindow.edit_color = edit_color
Ui_MainWindow.enlarge_window = enlarge_window

Ui_MainWindow.update_time = update_time
Ui_MainWindow.update_progressBar = update_progressBar

Ui_MainWindow.create_canvas = create_canvas
Ui_MainWindow.update_canvas = update_canvas


#==============================================================================#
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    ui.update_time()
    ui.check_input()
    ui.create_canvas()
    MainWindow.show()
    sys.exit(app.exec_())

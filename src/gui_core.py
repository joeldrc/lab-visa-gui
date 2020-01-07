#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import settings
from user_gui import *
from vna_scpi import *

import os
#from openpyxl import *
import time
from time import gmtime, strftime
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets, is_pyqt5
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure


#==============================================================================#
def file_open(self):
    name, _ = QtWidgets.QFileDialog.getOpenFileName(MainWindow, 'Open File', "", "Text file (*.csv *.txt)")  # Returns a tuple

    try:
        if self.tabWidget.currentIndex() == 1:
            with open(name, 'r') as file:
                text = file.read()
                self.textEdit.setText(text)

        # Read file
        file = open(name, "r")
        test = []
        line_cnt = 0

        #read data
        for row in file:
            #start from the line number 3
            if line_cnt > 2:
                row = row.replace(";\n", '') #remove last column
                column = row.split(";")
                test.append(column)
            else:
                line_cnt += 1
        #print(test[0][:])
        file.close()

        #re-order data
        measures = []
        for j in range(len(test[0])):
            tmp = []
            for i in range(len(test)):
                try:
                    tmp.append(np.float_(test[i][j]))
                except:
                    pass
            measures.append(tmp)
        #print(measures[1])
        print(measures)

        self.measures_stored = []
        for i in range(1,len(measures)):
            self.measures_stored.append((measures[0], measures[i]))

        self.update_plot()

    except Exception as e:
        print(e)

def file_save(self):
    title = self.serialName.text() + self.serialNumber.text() + self.addDetails.text()
    name, _ = QtWidgets.QFileDialog.getSaveFileName(MainWindow, 'Save file', os.path.join(str(os.getenv('HOME')), title), "all traces file (*)")  # Returns a tuple

    if name != "":
        if self.tabWidget.currentIndex() == 1:
            if len(name) > 0:
                with open(name + '.txt', 'a') as file:
                    text = self.textEdit.toPlainText()  # Plain text without formatting
                    #text = self.textEdit.toHtml()  # Rich text with formatting (font, color, etc.)
                    file.write(text)
                    file.close()
        else:
            # Save all files received from vna
            print("All-parameters")

            try:
                # export png files
                file = open(name + '.png',"wb")
                file.write(self.vna_measure.picture)
                file.close()
                print('File saved')

                QtWidgets.QMessageBox.question(MainWindow, 'Info', 'Png files saved!', QtWidgets.QMessageBox.Ok)
            except Exception as e:
                print(e)

            try:
                # export csv file
                for i in range(len(self.vna_measure.all_traces)):
                    # export sp file
                    file = open(name + '_' + str(i) + '.csv',"wb")
                    file.write(self.vna_measure.all_traces[i])
                    file.close()
                    print('File saved ' + str(i))

                QtWidgets.QMessageBox.question(MainWindow, 'Info', 'Csv files saved!', QtWidgets.QMessageBox.Ok)
            except Exception as e:
                print(e)

            try:
                # export sp file
                for i in range(len(self.vna_measure.s_parameters)):
                    # export sp file
                    file = open(name + '_' + str(i) + '.s2p',"wb")
                    file.write(self.vna_measure.s_parameters[i])
                    file.close()
                    print('File saved ' + str(i))

                QtWidgets.QMessageBox.question(MainWindow, 'Info', 'Sp files saved!', QtWidgets.QMessageBox.Ok)
            except Exception as e:
                print(e)

            """
            # Save all traces in excell file
            try:
                xValue = []
                yValue = []
                measures = self.measures_stored

                self.wb = Workbook()
                self.sheet = self.wb.active

                for i in range(len(measures)):
                    x, y = measures[i]
                    xValue.append(x)
                    yValue.append(y)

                # Create sheet
                self.sheet.cell(row=1, column=1).value = "test"
                self.sheet.cell(row=1, column=2).value = "test 2"

                for i in range(0, len(xValue), 1):
                    self.sheet.cell(row=2, column= (i * 2) + 1).value = 'data: ' + str(i + 1)
                    self.sheet.cell(row=3, column= (i * 2) + 1).value = 'x'
                    self.sheet.cell(row=3, column= (i * 2) + 2).value = 'y'
                    for j in range(0, len(xValue[0]), 1):
                        self.sheet.cell(row=j + 4, column= (i * 2) + 1).value = xValue[i][j]
                        self.sheet.cell(row=j + 4, column= (i * 2) + 2).value = yValue[i][j]

                self.wb.save(name + '.xlsx')
                print('File saved')
            except Exception as e:
                print(e)
            """

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

def file_info(self):
    QtWidgets.QMessageBox.question(MainWindow, 'Info', settings.__author__ + '\n' + settings.__version__, QtWidgets.QMessageBox.Ok)


#==============================================================================#
def check_input(self):
    self.actionOpen.triggered.connect(self.file_open)
    self.actionSave.triggered.connect(self.file_save)
    self.actionQuit.triggered.connect(self.file_quit)
    self.actionFont.triggered.connect(self.edit_font)
    self.actionColor.triggered.connect(self.edit_color)
    self.actionAbout.triggered.connect(self.file_info)

    self.connectButton.clicked.connect(self.connect_instrument)
    self.startMeasure.clicked.connect(self.start_measure)

    self.saveReference.stateChanged.connect(self.save_reference)
    self.addTrace.clicked.connect(self.add_trace)
    self.removeTrace.clicked.connect(self.remove_trace)
    self.compareTrace.stateChanged.connect(self.save_reference)

    for i in range(len(settings.instrument_address)):
        #self.instrumentAddress.setItemText(i, settings.instrument_address[i])
        self.instrumentAddress.addItem(settings.instrument_address[i])

    for i in range(len(settings.test_name)):
        self.comboBox_test_type.addItem(settings.test_name[i])

def connect_instrument(self):
    self.vna_measure = Vna_measure(self.instrumentAddress.currentText())
    self.progressBar.setValue(0)
    self.instrument_refresh()

def start_measure(self):
    address = self.instrumentAddress.currentText()
    test_name = self.comboBox_test_type.currentText()
    file_name = strftime("%d%m%Y_%H%M%S", gmtime())
    directory_name = settings.directory_name

    self.vna_measure = Vna_measure(instrument_address = address, test_name = test_name, file_name = file_name, directory_name = directory_name)
    self.progressBar.setValue(0)

    counter = self.lcdNumber.value() + 1
    self.lcdNumber.display(counter)
    self.instrument_refresh()

def save_reference(self):
    if self.compareTrace.isChecked():
        print('compare trace')
        self.saveRef = True

    self.update_plot()

def add_trace(self):
    self.saveRef = True
    self.update_plot()

def remove_trace(self):
    self.delRef = True
    self.update_plot()

def newkeyPressEvent(self, e):
    if ((e.key() == QtCore.Qt.Key_Enter) or (e.key() == (QtCore.Qt.Key_Enter-1))):
        print ("User has pushed Enter", e.key())
        self.start_measure()


#==============================================================================#
def instrument_refresh(self):
    try:
        self.remoteConnectionLabel.setText(self.vna_measure.instrument_info)

        bar_value = self.progressBar.value()
        if bar_value < 100:
            bar_value += 2
            self.progressBar.setValue(bar_value)

        if self.vna_measure.data_ready == True:
            self.vna_measure.data_ready = False

            # copy array
            self.measures_stored = self.vna_measure.measures

            self.update_plot()
            self.progressBar.setValue(100)

            if self.autoSave.isChecked():
                self.file_save()

    except Exception as e:
        print(e)

    self.instrument_timer = QtCore.QTimer()
    self.instrument_timer.timeout.connect(self.instrument_refresh)
    self.instrument_timer.start(1000)

def update_time(self):
    self.timeLabel.setText(strftime("%d %b %Y %H:%M:%S", gmtime()))
    self.timer = QtCore.QTimer()
    self.timer.timeout.connect(self.update_time)
    self.timer.start(1000)


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

    self.demo_fig = Figure(figsize=(5, 3))

    dynamic_canvas = FigureCanvas(self.demo_fig)
    self.plotTest.addWidget(dynamic_canvas)
    self.plotTest.addWidget(NavigationToolbar(dynamic_canvas, MainWindow))

    self._dynamic_ax = dynamic_canvas.figure.subplots()

    self._timer = dynamic_canvas.new_timer(100, [(self.update_canvas, (), {})])
    self._timer.start()

def update_canvas(self):
    if self.tabWidget.currentIndex() == 2:
        self._dynamic_ax.clear()
        t = np.linspace(0, 10, 101)
        # Shift the sinusoid as a function of time.
        self._dynamic_ax.plot(t, np.sin(t + time.time()))
        self._dynamic_ax.figure.canvas.draw()

        # auto adj
        self.demo_fig.tight_layout()


#==============================================================================#
def create_plot(self):
    plt.style.use('seaborn-whitegrid')

    self.plot = []
    self.fig = []
    self.toolbar = []

    # initialize fig
    self.fig = Figure(figsize=(12,7))

    # Figures
    subplot_number = len(self.measures_stored)
    if subplot_number < 1:
        subplot_number = 1

    # auto adapt plot number
    if subplot_number > 3:
        subplot_rows = 2
        subplot_columns = 3
    else:
        subplot_rows = 1
        subplot_columns = subplot_number

    for i in range(subplot_number):
        subplot = self.fig.add_subplot(subplot_rows, subplot_columns, i + 1)
        self.plot.append(subplot)

    # auto adj
    self.fig.tight_layout()

    # Canvas & toolbar
    self.thisFigure = FigureCanvas(self.fig)
    self.plotTest_2.addWidget(self.thisFigure)

    self.thisToolbar = NavigationToolbar(self.thisFigure, MainWindow)
    self.plotTest_2.addWidget(self.thisToolbar)

def update_plot(self):
    try:
        # delete old fig
        self.plotTest_2.removeWidget(self.thisFigure)
        self.thisFigure.deleteLater()
        self.thisFigure = None

        # delete old toolbar
        self.plotTest_2.removeWidget(self.thisToolbar)
        self.thisToolbar.deleteLater()
        self.thisToolbar = None

        self.create_plot()

        # return wich test you have selected
        selected_frame_number = self.comboBox_test_type.currentIndex() - 1
        channel_number = len(self.measures_stored)

        xValue = []
        yValue = []

        for i in range(channel_number):
            x, y = self.measures_stored[i]
            xValue.append(x)
            yValue.append(y)
            # clean plot line
            self.plot[i].clear()

        if self.saveReference.isChecked():
            self.saveRef = True

        if self.delRef == True:
            if (len(self.xRef) > 0):
                del(self.xRef[-1])
                del(self.yRef[-1])
            self.delRef = False
        else:
            if self.saveRef == True:
                self.xRef.append(xValue)
                self.yRef.append(yValue)
                self.saveRef = False

            for i in range(channel_number):
                # set data on plot
                self.plot[i].plot(xValue[i], yValue[i])

        for j in range(len(self.xRef)):
            for i in range(channel_number):

                if (j == 0) and (self.compareTrace.isChecked()):
                    purcentage = self.purcentageReference.value()

                    import numpy as np
                    myarray = np.asarray(self.yRef[j][i])

                    purcentage = abs(myarray * purcentage / 100)
                    self.lower_bound = myarray - purcentage
                    self.upper_bound = myarray + purcentage

                    self.plot[i].plot(self.xRef[j][i], self.yRef[j][i], lw=2, color='black', ls='--')
                    self.plot[i].fill_between(self.xRef[j][i], self.lower_bound, self.upper_bound, facecolor='cyan', alpha=0.2)

                    # fill_between errors
                    self.plot[i].fill_between(xValue[i], self.yRef[j][i], yValue[i], where = yValue[i] > self.upper_bound, facecolor='red', alpha=0.5)
                    self.plot[i].fill_between(xValue[i], self.yRef[j][i], yValue[i], where = yValue[i] < self.lower_bound, facecolor='lime', alpha=0.5)
                else:
                    self.plot[i].plot(self.xRef[j][i], self.yRef[j][i])

        try:
            # Set names on plot
            if selected_frame_number < len(settings.plot_names):
                for i in range(len(settings.plot_names[selected_frame_number])):
                    self.plot[i].set_title(settings.plot_names[selected_frame_number][i][0])
                    self.plot[i].set_xlabel(settings.plot_names[selected_frame_number][i][1])
                    self.plot[i].set_ylabel(settings.plot_names[selected_frame_number][i][2])
                    #self.plot[i].grid()
        except Exception as e:
            print(e)

        # autoadapt
        self.fig.tight_layout()
        # update plot
        self.fig.canvas.draw()

    except Exception as e:
        print(e)


#==============================================================================#
Ui_MainWindow.check_input = check_input
Ui_MainWindow.file_open = file_open
Ui_MainWindow.file_save = file_save
Ui_MainWindow.file_quit = file_quit
Ui_MainWindow.edit_font = edit_font
Ui_MainWindow.edit_color = edit_color
Ui_MainWindow.file_info = file_info

Ui_MainWindow.connect_instrument = connect_instrument

Ui_MainWindow.start_measure = start_measure

Ui_MainWindow.save_reference = save_reference
Ui_MainWindow.add_trace = add_trace
Ui_MainWindow.remove_trace = remove_trace

Ui_MainWindow.save_s_parameters = file_save

Ui_MainWindow.instrument_refresh = instrument_refresh
Ui_MainWindow.update_time = update_time

Ui_MainWindow.create_canvas = create_canvas
Ui_MainWindow.update_canvas = update_canvas

Ui_MainWindow.create_plot = create_plot
Ui_MainWindow.update_plot = update_plot

Ui_MainWindow.newkeyPressEvent = newkeyPressEvent


#==============================================================================#
Ui_MainWindow.xRef = []
Ui_MainWindow.yRef = []
Ui_MainWindow.saveRef = False
Ui_MainWindow.delRef = False
Ui_MainWindow.measures_stored = []


#==============================================================================#
#if __name__ == "__main__":
import sys
app = QtWidgets.QApplication(sys.argv)
MainWindow = QtWidgets.QMainWindow()
ui = Ui_MainWindow()
ui.setupUi(MainWindow)
ui.update_time()
ui.check_input()
ui.create_canvas()
ui.create_plot()
MainWindow.keyPressEvent = ui.newkeyPressEvent
MainWindow.show()
sys.exit(app.exec_())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import settings

import time
from time import gmtime, strftime

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from user_gui import *
from visa_scpi import *


class GuiCore(Ui_MainWindow):
    xRef = []
    yRef = []
    delRef = False
    addRef = False
    measures_stored = []

    def __init__(self):
        super().__init__()

        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)
        self.update_time()
        self.check_input()
        self.create_plot()

        self.MainWindow.keyPressEvent = self.newkeyPressEvent
        self.MainWindow.show()


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
        self.compareTrace.stateChanged.connect(self.compare_trace)

        self.instrumentAddress.addItem('')
        try:
            config_file = open("config/instrument_address.txt", "r")
            content_list = config_file.readlines()

            for value in content_list:
                # remove '\n'
                value = value.strip()

                if (value[0] != '#'):
                    self.instrumentAddress.addItem(value)
        except Exception as e:
            print(e)

        self.comboBox_test_type.addItem('')
        try:
            config_file = open("config/measure_type.txt", "r")
            content_list = config_file.readlines()

            for value in content_list:
                # remove '\n'
                value = value.strip()

                if (value[0] != '#'):
                    self.comboBox_test_type.addItem(value)
        except Exception as e:
            print(e)

#------------------------------------------------------------------------------#

    def file_open(self):
        #name, _ = QtWidgets.QFileDialog.getOpenFileName(MainWindow, 'Open File', "", "Text file (*.csv *.txt)")  # Returns a tuple
        name, _ = QtWidgets.QFileDialog.getOpenFileNames(self.MainWindow, 'Open File', "", "Text file (*.csv *.txt)")  # Returns a tuple

        for index in range(len(name)):
            print(name[index])

            try:
                if self.tabWidget.currentIndex() == 3:
                    with open(name[index], 'r') as file:
                        text = file.read()
                        self.textEdit.setText(text)

                # Read file
                file = open(name[index], "r")
                test = []
                line_cnt = 0

                #read data
                for row in file:
                    #start from the line number 3
                    if line_cnt == 2:
                        row = row.replace(";\n", '') #remove last column
                        self.plot_titles = row.split(";")
                        print(self.plot_titles)
                        line_cnt += 1

                    elif line_cnt > 2:
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
                #print(measures)

                if (index == 0):
                    self.measures_stored = []

                for i in range(1,len(measures)):
                    self.measures_stored.append((measures[0], measures[i]))

                self.update_plot()

            except Exception as e:
                print(e)


    def file_save(self):
        title = self.serialName.text() + self.serialNumber.text() + self.addDetails.text()
        name, _ = QtWidgets.QFileDialog.getSaveFileName(self.MainWindow, 'Save file', os.path.join(str(os.getenv('HOME')), title), "all traces file (*)")  # Returns a tuple

        if name != "":
            if self.tabWidget.currentIndex() == 3:
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
                except Exception as e:
                    print(e)

                try:
                    # export sp file
                    for i in range(len(self.vna_measure.s_parameters)):
                        # export sp file
                        file = open(name + '_' + str(i) + '.s{}p'.format(settings.port_number),"wb")
                        file.write(self.vna_measure.s_parameters[i])
                        file.close()
                        print('File saved ' + str(i))
                except Exception as e:
                    print(e)

                QtWidgets.QMessageBox.question(self.MainWindow, 'Info', 'Files saved!', QtWidgets.QMessageBox.Ok)

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
        decision = QtWidgets.QMessageBox.question(self.MainWindow, 'Question',
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
        QtWidgets.QMessageBox.question(self.MainWindow, 'Info', settings.__author__ + '\n' + settings.__version__, QtWidgets.QMessageBox.Ok)

#------------------------------------------------------------------------------#

    def connect_instrument(self):
        self.vna_measure = Vna_measure(self.instrumentAddress.currentText())
        self.progressBar.setValue(0)
        self.instrument_refresh()


    def start_measure(self):
        address = self.instrumentAddress.currentText()
        test_name = self.comboBox_test_type.currentText()
        file_name = strftime("%d%m%Y_%H%M%S", gmtime())
        directory_name = settings.directory_name

        self.vna_measure = Vna_measure(instrument_address = address, test_name = test_name, file_name = file_name, directory_name = directory_name, port_number = settings.port_number)
        self.progressBar.setValue(0)

        counter = self.lcdNumber.value() + 1
        self.lcdNumber.display(counter)
        self.instrument_refresh()

    def compare_trace(self):
        self.addRef = True
        self.update_plot()

    def save_reference(self):
        self.addRef = True
        self.update_plot()

    def add_trace(self):
        self.addRef = True
        self.update_plot()

    def remove_trace(self):
        self.delRef = True
        self.update_plot()

    def newkeyPressEvent(self, e):
        if ((e.key() == QtCore.Qt.Key_Enter) or (e.key() == (QtCore.Qt.Key_Enter-1))):
            print ("User has pushed Enter", e.key())
            self.start_measure()

    #--------------------------------------------------------------------------#

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

                # selecting all the text in the box
                self.serialNumber.selectAll()

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

    #--------------------------------------------------------------------------#

    def create_plot(self):
        plt.style.use('seaborn-whitegrid')

        self.fig = []
        self.toolbar = []

        # initialize fig
        self.fig_0 = Figure(figsize=(12,7))
        self.fig_2 = Figure(figsize=(12,7))

        # add canvas
        self.figCanvas_0 = FigureCanvas(self.fig_0)
        self.figCanvas_2 = FigureCanvas(self.fig_2)

        self.plot_0.addWidget(self.figCanvas_0)
        self.plot_2.addWidget(self.figCanvas_2)

        # add toolbar
        self.navToolbar_0 = NavigationToolbar(self.figCanvas_0, self.MainWindow)
        self.navToolbar_2 = NavigationToolbar(self.figCanvas_2, self.MainWindow)

        self.plot_0.addWidget(self.navToolbar_0)
        self.plot_2.addWidget(self.navToolbar_2)

        # dynamic plot refresh
        self.plot_timer = QtCore.QTimer()
        self.plot_timer.timeout.connect(self.update_plot)

    #--------------------------------------------------------------------------#

    def update_plot(self):
        #self.values = values

        if (self.tabWidget.currentIndex() == 0):
            # clearing old figure
            self.fig_0.clear()

            xValue = []
            yValue = []
            xyVal = []

            # add plot 1
            subplots = len(self.measures_stored)
            if subplots < 1:
                subplots = 1

            if subplots > 8:
                rows = 4
                columns = 3
            elif subplots > 6:
                rows = 4
                columns = 2
            elif subplots > 3:
                rows = 2
                columns = 3
            else:
                rows = 1
                columns = subplots

            self.subplot = []
            for i in range(subplots):
                self.subplot.append(self.fig_0.add_subplot(rows, columns, i + 1))
                #self.subplot[i].clear()
                x, y = self.measures_stored[i]
                xValue.append(x)
                yValue.append(y)
                # plot
                self.subplot[i].plot(xValue[i], yValue[i])

            if self.delRef == True:
                self.delRef = False
                try:
                    del(self.xRef[-1])
                    del(self.yRef[-1])
                except:
                    pass
            elif self.addRef:
                    self.addRef = False
                    self.xRef.append(xValue)
                    self.yRef.append(yValue)

            for j in range(len(self.xRef)):
                for i in range(subplots):
                    if (j == 0) and (self.compareTrace.isChecked()):
                        purcentage = self.purcentageReference.value()

                        import numpy as np
                        myarray = np.asarray(self.yRef[j][i])

                        purcentage = abs(myarray * purcentage / 100)
                        self.lower_bound = myarray - purcentage
                        self.upper_bound = myarray + purcentage

                        self.subplot[i].plot(self.xRef[j][i], self.yRef[j][i], lw=2, color='black', ls='--')
                        self.subplot[i].fill_between(self.xRef[j][i], self.lower_bound, self.upper_bound, facecolor='cyan', alpha=0.2)

                        # fill_between errors
                        self.subplot[i].fill_between(xValue[i], self.yRef[j][i], yValue[i], where = yValue[i] > self.upper_bound, facecolor='red', alpha=0.5)
                        self.subplot[i].fill_between(xValue[i], self.yRef[j][i], yValue[i], where = yValue[i] < self.lower_bound, facecolor='lime', alpha=0.5)
                    else:
                        self.subplot[i].plot(self.xRef[j][i], self.yRef[j][i])

            """
            try:
                # Set names on plot
                selected_frame_number = 0
                for i in range(len(settings.plot_names[selected_frame_number])):
                    self.subplot[i].set_title(settings.plot_names[selected_frame_number][i][0])
                    self.subplot[i].set_xlabel(settings.plot_names[selected_frame_number][i][1])
                    self.subplot[i].set_ylabel(settings.plot_names[selected_frame_number][i][2])
                    #self.plot[i].grid()
            except Exception as e:
                print(e)
            """

        if (self.tabWidget.currentIndex() == 2):
            # clearing old figure
            self.fig_2.clear()

            self.demoValues_ax = self.figCanvas_2.figure.subplots()

            t = np.linspace(0, 10, 101)
            self.demoValues_ax.plot(t, np.sin(t + time.time()))

            self.plot_timer.start(100)
        else:
            self.plot_timer.stop()

        # auto adj
        self.fig_0.tight_layout()
        self.fig_2.tight_layout()

        self.fig_0.canvas.draw()
        self.fig_2.canvas.draw()

#------------------------------------------------------------------------------#

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = GuiCore()
    sys.exit(app.exec_())

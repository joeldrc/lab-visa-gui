#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Joel Daricou 03/2022

import os
import sys
import settings

import time
from time import gmtime, strftime

from PyQt5.QtCore import QRunnable, Qt, QThreadPool

import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from user_gui import *
from visa_scpi import *


class GuiCore(Ui_MainWindow):
    all_traces = {}
    all_traces['VNA'] = []
    all_traces['OSC'] = []
    all_traces['Demo'] = []

    mem_ref = False
    delRef = False
    addRef = False
    xRef = []
    yRef = []
    tab = ''

    def __init__(self):
        super().__init__()
        self.MainWindow = QtWidgets.QMainWindow()
        self.setupUi(self.MainWindow)
        self.set_timers()
        self.check_input()
        self.create_plot()
        self.MainWindow.keyPressEvent = self.newkeyPressEvent
        self.MainWindow.show()

    def set_timers(self):
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)

    def update_time(self):
        self.time.setText(strftime("%d %b %Y %H:%M:%S", gmtime()))
       
    def check_input(self):
        self.actionOpen.triggered.connect(self.file_open)
        self.actionSave.triggered.connect(self.file_save)
        self.actionQuit.triggered.connect(self.file_quit)
        self.actionFont.triggered.connect(self.edit_font)
        self.actionColor.triggered.connect(self.edit_color)
        self.actionAbout.triggered.connect(self.file_info)

        self.connect_btn.clicked.connect(self.measure)
        self.start_measure.clicked.connect(self.measure)      
        self.addTrace.clicked.connect(self.add_trace)
        self.removeTrace.clicked.connect(self.remove_trace)

        self.save_ref.stateChanged.connect(self.save_reference)
        self.comp_trace.stateChanged.connect(self.compare_trace)

        self.read_comboBox("config/instrument_address.txt", self.instrument_address)
        self.read_comboBox("config/measure_type.txt", self.comboBox_test_type)        
        
    def read_comboBox(self, path, comboBox):
        comboBox.addItem('_')
        try:
            config_file = open(path, "r")
            content_list = config_file.readlines()
            for value in content_list:
                # remove '\n'
                value = value.strip()
                if (value[0] != '#'):
                    comboBox.addItem(value)
        except Exception as e:
            print(e)

    def create_plot(self):
        plt.style.use('seaborn-whitegrid')

        # initialize fig
        self.fig_0 = Figure(figsize=(12,7))
        self.fig_1 = Figure(figsize=(12,7))
        self.fig_2 = Figure(figsize=(12,7))

        # add canvas
        self.figCanvas_0 = FigureCanvas(self.fig_0)
        self.figCanvas_1 = FigureCanvas(self.fig_1)
        self.figCanvas_2 = FigureCanvas(self.fig_2)

        # add widget
        self.vna_plot.addWidget(self.figCanvas_0)
        self.osc_plot.addWidget(self.figCanvas_1)
        self.demo_plot.addWidget(self.figCanvas_2)

        # add toolbar
        self.navToolbar_0 = NavigationToolbar(self.figCanvas_0, self.MainWindow)
        self.navToolbar_1 = NavigationToolbar(self.figCanvas_1, self.MainWindow)
        self.navToolbar_2 = NavigationToolbar(self.figCanvas_2, self.MainWindow)
        self.vna_plot.addWidget(self.navToolbar_0)
        self.osc_plot.addWidget(self.navToolbar_1)
        self.demo_plot.addWidget(self.navToolbar_2)

    def measure(self):
        self.measure_bar.setValue(0)
        counter = self.lcd_num.value() 
        self.tab = self.tabWidget.tabText(self.tabWidget.currentIndex())

        if (self.tab == "VNA"):       
            counter += 1
        elif (self.tab == "OSC"):
            pass       
        elif (self.tab == "Notes"):
            pass   
        elif (self.tab == "Demo"):
            pass     
        elif (self.tab == "VISA"):
            pass
        else:
            pass
        
        self.lcd_num.display(counter) 

        # multi thread
        pool = QThreadPool.globalInstance()   
        # max thread to 1, if busy wait
        pool.setMaxThreadCount(1)
        #print("Thread count: ", pool.maxThreadCount())
        self.instrument = VISA_Instrument()

        # class setup    
        self.instrument.type = self.tab
        self.instrument.address = self.instrument_address.currentText()
        self.instrument.test_name = self.serial_name.text() + self.serial_number.text()
        self.instrument.file_name = ''
        self.instrument.directory_name = ''

        # start thread
        pool.start(self.instrument)

        # timer refresher        
        self.timer_refsher = QtCore.QTimer()
        self.timer_refsher.timeout.connect(self.instrument_refresh)
        self.timer_refsher.start(500)

    def instrument_refresh(self):          
        self.remote_connection.setText(self.instrument.info)  

        bar_value = self.measure_bar.value()
        if (bar_value < 100):
            bar_value += 2
            self.measure_bar.setValue(bar_value)

        if (self.instrument.data_ready == True):
            self.instrument.data_ready = False

            self.update_plot(self.instrument.measures)
            self.measure_bar.setValue(100)

            if self.auto_save.isChecked():
                self.file_save()
        
        self.tab = self.tabWidget.tabText(self.tabWidget.currentIndex())
        if (self.tab == "Demo"):     
            self.measure()

#------------------------------------------------------------------------------#   
   
    def update_plot(self, measures = None): 
        self.subplot = []

        if (measures != None):
            self.all_traces[self.tab].append(measures)

        if (self.tab == "VNA"):
            # clear old figure
            self.fig_0.clear()

            # add plot
            num_traces = len(self.all_traces[self.tab][-1])
            if(num_traces > 0):
                if num_traces > 8:
                    rows = 4
                    columns = 3
                elif num_traces > 6:
                    rows = 4
                    columns = 2
                elif num_traces > 3:
                    rows = 2
                    columns = 3
                else:
                    rows = 1
                    columns = num_traces
                    
            # list with all the measurements
            meas = self.all_traces[self.tab]

            if self.delRef == True:
                self.delRef = False
                if (len(meas) > 1):
                    del(meas[-1])

            elif (self.save_ref.isChecked() or self.addRef):
                self.addRef = False
                if (len(meas) > 0):
                    meas.append(meas[-1])
            else:
                del(meas[:-1])

            for measure in meas:
                # list of traces in a measure
                traces = len(measure)

                for i in range(traces):
                    x, y = measure[i]
                    self.subplot.append(self.fig_0.add_subplot(rows, columns, i + 1))                 
                    
                    if (i == 0) and (self.comp_trace.isChecked()):
                        if (self.mem_ref == True):
                            self.mem_ref = False
                            self.xRef, self.yRef = measure[i]
                        
                        purcentage = self.purcentage_ref.value()
                        myarray = np.asarray(self.yRef)
                        lower_bound = myarray - purcentage
                        upper_bound = myarray + purcentage

                        self.subplot[i].plot(self.xRef, self.yRef, lw=2, color='black', ls='--')
                        self.subplot[i].fill_between(self.xRef, lower_bound, upper_bound, facecolor='lime', alpha=0.2)

                        # fill_between errors
                        self.subplot[i].fill_between(x, self.yRef, y, where = y > upper_bound, facecolor='red', alpha=0.6)
                        self.subplot[i].fill_between(x, self.yRef, y, where = y < lower_bound, facecolor='red', alpha=0.6)                       

                    self.subplot[i].plot(x, y)

            # auto adj
            self.fig_0.tight_layout()
            self.fig_0.canvas.draw()

        elif (self.tab == "Demo"):  
            # clearing old figure
            self.fig_2.clear()
            self.demoValues = self.figCanvas_2.figure.subplots()
            del(self.all_traces[self.tab][:-1])
            x, y = self.all_traces[self.tab][-1][0]
            self.demoValues.plot(x, y)
            self.fig_2.tight_layout()
            self.fig_2.canvas.draw()
        else:
            pass

    def compare_trace(self):
        self.addRef = True
        self.mem_ref = True
        self.update_plot()

    def save_reference(self):
        if(self.save_ref.isChecked()):
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
            self.measure()

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
   
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = GuiCore()
    sys.exit(app.exec_())

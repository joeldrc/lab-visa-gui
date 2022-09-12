#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Joel Daricou 07/2022

import os
import sys
import settings

from time import gmtime, strftime

from PyQt5.QtCore import QThreadPool

import matplotlib.pyplot as plt
from matplotlib.backends.qt_compat import QtCore, QtWidgets
from matplotlib.backends.backend_qt5agg import (FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure

from user_gui import *
from multi_thread import *
from visa_scpi import *


class GuiCore(Ui_MainWindow):
    all_traces = {}
    all_traces['plot'] = []

    all_files = {}
    all_files['instr_info'] = None
    all_files['form_data'] = []
    all_files['png_file'] = []
    all_files['csv_file'] = []
    all_files['snp_file'] = []

    mem_ref = False
    delRef = False
    addRef = False
    xRef = []
    yRef = []

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
        # timer refresher        
        self.timer_refsher = QtCore.QTimer()
        self.timer_refsher.timeout.connect(self.instrument_refresh)
        
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

    def check_tab(self):
        return self.tabWidget.tabText(self.tabWidget.currentIndex())      
        
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

        # add widget
        self.vna_plot.addWidget(self.figCanvas_0)

        # add toolbar
        self.navToolbar_0 = NavigationToolbar(self.figCanvas_0, self.MainWindow)
        self.vna_plot.addWidget(self.navToolbar_0)

    def launch_measure(self, tab = None):
        if (tab == None):
            tab = self.check_tab()
         
        counter = self.lcd_num.value() 
        if (tab == "Plot"):    
            counter += 1     
        elif (tab == "Notes"):
            pass 
        else:
            pass

        self.lcd_num.display(counter) 
        self.measure_bar.setValue(0)  
        self.timer_refsher.start(200)

        # Pass the function to execute
        instr = Measure(self.thread) # Any other args, kwargs are passed to the run function
        instr.signals.result.connect(self.print_output)
        instr.signals.finished.connect(self.thread_complete)
        # Execute
        instr.threadpool.start(instr)

        # set tab value
        self.tab = tab

    def thread(self, progress_callback):
        address = self.instrument_address.currentText()
        setup = self.comboBox_test_type.currentText()
        #test_name = self.serial_name.text() + self.serial_number.text()
        vna = Instrument_VISA(address, setup, calib = self.cal_file.isChecked())
        
        #disable_calibration
        self.cal_file.setChecked(False)
        
        return vna.run()

    def print_output(self, s):
        #debug
        #print(s)
        pass

    def thread_complete(self, result):
        print("Thread finished")

        self.all_files = result
        self.remote_connection.setText(self.all_files['instr_info'])
        self.update_plot(self.all_files['form_data'])

        # timer refresher
        self.timer_refsher.stop()
        self.measure_bar.setValue(100)

        # demo plot
        self.tab = self.check_tab()
        addr = self.instrument_address.currentText()
        if ((self.tab == "Plot") and (addr == "Demo")):
            self.auto_save.setChecked(False)
            time.sleep(0.1)             
            self.launch_measure()
        
        #save files
        elif self.auto_save.isChecked():
            self.file_save()

    def instrument_refresh(self):             
        bar_value = self.measure_bar.value()
        if (bar_value < 100):
            bar_value += 1
            self.measure_bar.setValue(bar_value)

    """
    def update_plot(self, measures = None):
        self.subplot = []
        tab = self.tab
        
        if(measures != None):
            self.all_traces[tab].append(measures)

        # select the type of plot
        if (tab == "VNA"):
            # clear old figure
            self.fig_0.clear()

            # list with all the measurements
            meas = self.all_traces[tab]

            # add plot
            if (len(meas) > 0):
                num_traces = len(meas[-1])
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
                    
            if self.delRef == True:
                self.delRef = False
                if (len(meas) > 0):
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
    """

    def update_plot(self, meas = None):  
        tab = self.check_tab()

        # clear old figure
        self.fig_0.clear()

        measures = self.all_traces['plot']
        #measures = [[[[0,],[0,]]]]

        if(meas != None):
            if (self.save_ref.isChecked()):
                measures.append([meas])
            else:
                measures = [[meas]]

        """
        measures = []
        if(meas != None):
            measures = [meas]
        else:
          #measures = [[[[0,],[0,]]]]
          pass
        """
        
        for measure in measures:
            # add plot
            if (len(measure) > 0):
                num_traces = len(measure[-1])
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
                        
                self.subplot = [0]*num_traces
                for i in range(num_traces):
                    self.subplot[i] = self.fig_0.add_subplot(rows, columns, i + 1)

            """
            if (tab == "VNA"): 
                if self.delRef == True:
                    self.delRef = False
                    del(measures[-1])

                elif (self.save_ref.isChecked() or self.addRef):
                    self.addRef = False
                    measures.append(measures[-1])
                else: 
                    measures = [measures[-1]]
            """

            # list of traces in a measure         
            for traces in measure: 
                # single trace in list of traces
                plt_num = 0
                for trace in traces:
                    #print(trace)
                    x, y = trace
                    self.subplot[plt_num].plot(x, y)
                    plt_num +=1
                    
        # auto adj
        self.fig_0.tight_layout()
        self.fig_0.canvas.draw()

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

    def measure(self):
        self.launch_measure()

    def newkeyPressEvent(self, e):
        if ((e.key() == QtCore.Qt.Key_Enter) or (e.key() == (QtCore.Qt.Key_Enter-1))):
            print ("User has pushed Enter", e.key())
            self.measure()

    def file_open(self):
        name, _ = QtWidgets.QFileDialog.getOpenFileNames(self.MainWindow, 'Open File', "", "Text file (*.csv *.txt)")  # Returns a tuple

        for index in range(len(name)):
            print(name[index])
            
            # read file
            file = open(name[index], "r")

            # read data
            values = []
            for row in file:
                row = row.replace("\n", '')
                values.append(row)
            file.close()

            #extract data
            begin = []
            end = []
            for i in range(len(values)):
                if values[i].find('BEGIN') == 0:
                    begin.append(i+2) #skip the first two rows
                elif values[i].find('END') == 0:
                    end.append(i-1) #skip the first row

            data = []
            for b, e in zip(begin, end):
                val_x = []
                val_y = []
                for row in values[b:e]:                
                    x, y = row.split(",")    
                    val_x.append(np.float_(x))
                    val_y.append(np.float_(y))
                    
                data.append([val_x, val_y])

            self.tab = self.check_tab()
            self.update_plot(data)

            """
            text = []
            line_cnt = 0
            # read data R&S
            for row in file:
                # start from the line number 3  
                if line_cnt == 2:
                    # remove last column
                    row = row.replace("\n", '')       
                    row = row.replace(";", ',')
                    plot_titles = row.split(",")
                    plot_titles.remove('')                     
                    line_cnt += 1
                elif line_cnt > 2:
                    # remove last column
                    row = row.replace("\n", '') 
                    row = row.replace(";", ',') 
                    column = row.split(",")
                    column.remove('') 
                    text.append(column)
                else:
                    line_cnt += 1   
            file.close()

            # convert to float excluding the first row
            data = []
            for j in range(len(text[0])):
                row = []
                for i in range(len(text)):
                    row.append(np.float_(text[i][j]))
                data.append(row)
            
            # re-order data
            measure = []
            for i in range(1,len(data)):
                measure.append([data[0], data[i]])
            
            self.tab = self.check_tab()
            self.update_plot(measure)
            """

    def file_save(self):
        title = self.serial_name.text() + self.serial_number.text()
        name, _ = QtWidgets.QFileDialog.getSaveFileName(self.MainWindow, 'Save file', os.path.join(str(os.getenv('HOME')), title), "all traces file (*)")  # Returns a tuple

        if name != "":
            if (self.tabWidget.tabText(self.tabWidget.currentIndex()) == 'Notes'):
                if len(name) > 0:
                    with open(name + '.txt', 'a') as file:
                        text = self.textEdit.toPlainText()  # Plain text without formatting
                        #text = self.textEdit.toHtml()  # Rich text with formatting (font, color, etc.)
                        file.write(text)
                        file.close()
                print('Notes saved')
            else:
                # Save all files received from vna
                print("Save files")

                if (self.png_file.isChecked()):
                    try:
                        # export png files
                        file = open(name + '.png',"wb")
                        file.write(self.all_files['png_file'])
                        file.close()
                        print('png file saved')
                    except Exception as e:
                        print(e, 'No png file')

                if (self.csv_file.isChecked()):
                    try:
                        # export csv file
                        """
                        cnt = 0
                        for csv_file in self.all_files['csv_file']:
                            #file = open(name + '_' + str(cnt) + '.csv',"wb")
                            file = open(name + '_' + str(cnt) + '.csv',"w")
                            file.write(csv_file)
                            file.close()
                            print('csv file saved ' + str(cnt))
                            cnt += 1
                        """
                        csv_file = self.all_files['csv_file']
                        csv_file = csv_file.replace("\n", '')         

                        file = open(name + '.csv',"w")
                        file.write(csv_file)
                        file.close()
                        print('csv file saved')
                    except Exception as e:
                        print(e, 'No csv file')

                if (self.snp_file.isChecked()):
                    try:                      
                        """
                        cnt = 0
                        # export sp file
                        for snp_file in self.all_files['snp_file']:
                            #file = open(name + '_' + str(cnt) + '.s{}p'.format(2),"wb")
                            file = open(name + '_' + str(cnt) + '.s{}p'.format(2),"w")
                            file.write(snp_file)
                            file.close()
                            print('File saved ' + str(cnt))
                            cnt += 1
                        """
                        snp_file = self.all_files['snp_file']
                        snp_file = snp_file.replace("\n", '')  

                        file = open(name + '.s{}p'.format(4),"w")
                        file.write(snp_file)
                        file.close()
                        print('File saved')
                    except Exception as e:
                        print(e, 'No snp file')
                
                if (self.cal_file.isChecked()):
                    print('No cal file')

                QtWidgets.QMessageBox.question(self.MainWindow, 'Info', 'Files saved!', QtWidgets.QMessageBox.Ok)

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

   
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    gui = GuiCore()
    sys.exit(app.exec_())

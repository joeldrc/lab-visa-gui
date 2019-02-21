#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from visa_scpi import *
import threading
from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
from openpyxl import *


class Measure_thread(threading.Thread):
    def __init__(self, address, start_test= False, test_number = 0):
        threading.Thread.__init__(self)

        self.file_name = ""
        self.time_value = ""
        self.start_test = start_test
        self.test_number = test_number
        self.measure_started = False
        self.data_ready = False

        try:
            self.vna = Vna_measure(address)
            self.instrument_info = self.vna.instrument_info()
        except Exception as e:
            print(e)
            self.instrument_info = "No connection", "\n "
            self.start_test = False

        # opening the existing excel file & create the sheet object
        self.wb = Workbook()
        self.sheet = self.wb.active

    # run all the time
    def run(self):
        try:
            if self.start_test:

                self.measure_started = True
                self.data_ready = False

                #measure vna
                if self.test_number == 0:
                    self.measures_0 = []
                    for i in range(0,5,1):
                        self.measures_0.append(self.vna.read_measure_1(i))

                elif self.test_number == 1:
                    self.measures_1 = []
                    for i in range(0,2,1):
                        self.measures_1.append(self.vna.read_measure_2(i))

                self.data_ready = True
                self.measure_started = False
        except Exception as e:
            print(e)

    def create_sheet(self):
        xValue = []
        yValue = []
        for i in range(0,5,1):
            x, y = self.measures_0[i]
            xValue.append(x)
            yValue.append(y)

        # - - - - - - - - - - - - - - - - - - - - -
        # Create sheet
        """
        # resize the width of columns in excel spreadsheet
        self.sheet.column_dimensions['A'].width = 30
        self.sheet.column_dimensions['B'].width = 30
        """

        self.sheet.cell(row=1, column=1).value = self.file_name

        self.sheet.cell(row=1, column=2).value = self.time_value

        self.sheet.cell(row=2, column=1).value = 'x'
        self.sheet.cell(row=2, column=2).value = 'y'

        self.sheet.cell(row=2, column=4).value = 'x'
        self.sheet.cell(row=2, column=5).value = 'y'

        self.sheet.cell(row=2, column=7).value = 'x'
        self.sheet.cell(row=2, column=8).value = 'y'

        self.sheet.cell(row=2, column=10).value = 'x'
        self.sheet.cell(row=2, column=11).value = 'y'

        self.sheet.cell(row=2, column=13).value = 'x'
        self.sheet.cell(row=2, column=14).value = 'y'

        for i in range(0, len(xValue[0]), 1):
            self.sheet.cell(row=i + 3, column=1).value = xValue[0][i]
            self.sheet.cell(row=i + 3, column=2).value = yValue[0][i]

            self.sheet.cell(row=i + 3, column=4).value = xValue[1][i]
            self.sheet.cell(row=i + 3, column=5).value = yValue[1][i]

            self.sheet.cell(row=i + 3, column=7).value = xValue[2][i]
            self.sheet.cell(row=i + 3, column=8).value = yValue[2][i]

            self.sheet.cell(row=i + 3, column=10).value = xValue[3][i]
            self.sheet.cell(row=i + 3, column=11).value = yValue[3][i]

            self.sheet.cell(row=i + 3, column=13).value = xValue[4][i]
            self.sheet.cell(row=i + 3, column=14).value = yValue[4][i]

        file_position = filedialog.asksaveasfilename(initialdir = "/",initialfile=self.file_name, title = "Select file",filetypes = (("Microsoft Excel Worksheet","*.xlsx"),("all files","*.*")), defaultextension = ' ')
        try:
            self.wb.save(file_position)
        except Exception as e:
            print(e)


class Progress_bar():
    # threaded progress bar for tkinter gui
    def __init__(self, parent, row, columnspan, sticky, padx, pady):
        self.maximum = 100
        self.interval = 10
        self.progressbar = ttk.Progressbar(parent, orient=tk.HORIZONTAL, mode="indeterminate", maximum=self.maximum)
        self.progressbar.grid(row= row, columnspan=columnspan, sticky=sticky, padx=padx, pady=pady)
        self.thread = threading.Thread()
        self.thread.__init__(target=self.progressbar.start(self.interval), args=())
        self.pb_clear()

    def pb_stop(self):
        if not self.thread.isAlive():
            VALUE = self.progressbar["value"]
            self.progressbar.stop()
            self.progressbar["value"] = VALUE

    def pb_start(self):
        if not self.thread.isAlive():
            VALUE = self.progressbar["value"]
            self.progressbar.configure(mode="indeterminate", maximum=self.maximum, value=VALUE)
            self.progressbar.start(self.interval)

    def pb_clear(self):
        if not self.thread.isAlive():
            self.progressbar.stop()
            self.progressbar.configure(mode="determinate", value=0)

    def pb_complete(self):
        if not self.thread.isAlive():
            self.progressbar.stop()
            self.progressbar.configure(mode="determinate", maximum=self.maximum, value=self.maximum)

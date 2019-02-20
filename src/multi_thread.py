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
    def __init__(self, address, start_test= False):
        threading.Thread.__init__(self)

        self.file_name = ""
        self.time_value = ""
        self.start_test = start_test
        self.measure_started = False
        self.data_ready = False

        try:
            self.vna = Vna_measure(address)
            self.instrument_info = self.vna.instrument_info()
        except:
            print("Visa error or wrong address")
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
                self.measure0 = self.vna.read_measure_1(0)
                self.measure1 = self.vna.read_measure_1(1)
                self.measure2 = self.vna.read_measure_1(2)
                self.measure3 = self.vna.read_measure_1(3)
                self.measure4 = self.vna.read_measure_1(4)

                self.data_ready = True
                self.measure_started = False
        except:
            print("No vna declared")

    def create_sheet(self):
        # masure vna
        xValue0, yValue0 = self.measure0
        xValue1, yValue1 = self.measure1
        xValue2, yValue2 = self.measure2
        xValue3, yValue3 = self.measure3
        xValue4, yValue4 = self.measure4

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

        for i in range(0, len(xValue0), 1):
            self.sheet.cell(row=i + 3, column=1).value = xValue0[i]
            self.sheet.cell(row=i + 3, column=2).value = yValue0[i]

            self.sheet.cell(row=i + 3, column=4).value = xValue1[i]
            self.sheet.cell(row=i + 3, column=5).value = yValue1[i]

            self.sheet.cell(row=i + 3, column=7).value = xValue2[i]
            self.sheet.cell(row=i + 3, column=8).value = yValue2[i]

            self.sheet.cell(row=i + 3, column=10).value = xValue3[i]
            self.sheet.cell(row=i + 3, column=11).value = yValue3[i]

            self.sheet.cell(row=i + 3, column=13).value = xValue4[i]
            self.sheet.cell(row=i + 3, column=14).value = yValue4[i]

        file_position = filedialog.asksaveasfilename(initialdir = "/",initialfile=self.file_name, title = "Select file",filetypes = (("Microsoft Excel Worksheet","*.xlsx"),("all files","*.*")), defaultextension = ' ')
        try:
            self.wb.save(file_position)
        except:
            print("Save operation error")


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

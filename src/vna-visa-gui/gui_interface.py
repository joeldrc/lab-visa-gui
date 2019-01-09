#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multi_thread import *

import time
from time import gmtime, strftime

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class User_gui(tk.Frame):

    def __init__(self, parent):
        self.window = parent
        #self.window.geometry('600x600')
        #self.window.configure(background='gray')

        self.window.protocol("WM_DELETE_WINDOW", self.close_program)

        self.plot_reference = False
        self.plot_saveRef = False
        self.save_data = False

        self.hostname_value = "TCPIP::CFO-MD-BQPVNA1::INSTR"

        self.window.title("TEST GUI - V.1.0")
        self.create_widgets()


    # when you close the program kill all the windows
    def close_program(self):
        self.window.destroy()
        exit()


    # when you press return
    def focus(self, event):
        self.start_test()


    # - - - - - - - - - - - - - - - - - - - - -
    # menuBar
    def show_info(self):
        messagebox.showinfo(title = 'About Me!', message = 'joel.daricou@cern.ch 2018')


    def save_file(self):
        #file_name = self.serial_name_field.get() + '_' + self.serial_number_field.get() + '_' + self.details_field.get()
        try:
            self.measure_thread.create_sheet()
        except:
            print("No data ready")

        return


    def open_file(self):
        #self.file_position = filedialog.askopenfile().name
        return


    def close_file(self):
        exit = messagebox.askyesno(title = 'Quit?', message = 'Are you sure?')
        if exit > 0:
            self.close_program()


    # - - - - - - - - - - - - - - - - - - - - -
    # autoupdate
    def update_screen(self):
        try:
            if self.measure_thread.measure_started:
                self.prog_bar.pb_start()
            else:
                self.create_plot()

            if self.measure_thread.data_ready:
                self.measure_thread.data_ready = False
                self.prog_bar.pb_complete()
                if self.save_data:
                    self.measure_thread.create_sheet()
        except:
            print(".")

        self.clock.config(text=strftime("%d %b %Y %H:%M:%S", gmtime()))
        self.clock.after(1000, self.update_screen)


    # - - - - - - - - - - - - - - - - - - - - -
    # user pannel
    def panel_led(self, color):
        self.circle_canvas.create_oval(10, 10, 40, 40, width=0, fill=color)


    def save_ref(self):
        # invert the value
        self.plot_reference = not self.plot_reference
        if self.plot_reference == True:
            self.save_ref.config(text='Remove Ref.')
            self.plot_saveRef = True
        else:
            self.save_ref.config(text='Set Ref.')


    def start_test(self):
        self.instrument_connection(start_test = True)
        self.measure_thread.file_name = self.serial_name_field.get() + '_' + self.serial_number_field.get() + '_' + self.details_field.get()
        self.measure_thread.time_value = strftime("%d %b %Y %H:%M:%S", gmtime())


    def instrument_connection(self, start_test = False):
        self.measure_thread = Measure_thread(self.hostname_field.get(), start_test)
        self.measure_thread.start()

        instrument_name, instrument_address = self.measure_thread.instrument_info
        self.str_instrument_info = instrument_name + "\n" + instrument_address
        self.labeled_frame_label.config(text=self.str_instrument_info)


    def save_sheet(self):
        try:
            self.save_data = self.var.get()
        except:
            print("No class declared")


    def set_axis_name(self):
        # set axis names
        self.plot0.set_title('S21 - delay')
        self.plot0.set_xlabel('freq')
        self.plot0.set_ylabel('dB')

        self.plot1.set_title('S21 - dB')
        self.plot1.set_xlabel('freq')
        self.plot1.set_ylabel('dB')

        self.plot2.set_title('S11 - SWR')
        self.plot2.set_xlabel('freq')
        self.plot2.set_ylabel('dB')

        self.plot3.set_title('S22 - SWR')
        self.plot3.set_xlabel('freq')
        self.plot3.set_ylabel('dB')

        self.plot4.set_title('S11 - TDR')
        self.plot4.set_xlabel('delay')
        self.plot4.set_ylabel('dB')


    def create_plot(self):
        # masure vna
        xValue0, yValue0 = self.measure_thread.measure0
        xValue1, yValue1 = self.measure_thread.measure1
        xValue2, yValue2 = self.measure_thread.measure2
        xValue3, yValue3 = self.measure_thread.measure3
        xValue4, yValue4 = self.measure_thread.measure4

        if self.plot_saveRef == True:
            # set reference data on plot
            self.xRef0, self.yRef0 = xValue0, yValue0
            self.xRef1, self.yRef1 = xValue1, yValue1
            self.xRef2, self.yRef2 = xValue2, yValue2
            self.xRef3, self.yRef3 = xValue3, yValue3
            self.xRef4, self.yRef4 = xValue4, yValue4
            self.plot_saveRef = False

        # clean plot line
        self.plot0.cla()
        self.plot1.cla()
        self.plot2.cla()
        self.plot3.cla()
        self.plot4.cla()

        # set axis names
        self.set_axis_name()

        # set data on plot
        self.plot0.plot(xValue0, yValue0)
        self.plot1.plot(xValue1, yValue1)
        self.plot2.plot(xValue2, yValue2)
        self.plot3.plot(xValue3, yValue3)
        self.plot4.plot(xValue4, yValue4)

        if self.plot_reference == True:
            self.plot0.plot(self.xRef0, self.yRef0)
            self.plot1.plot(self.xRef1, self.yRef1)
            self.plot2.plot(self.xRef2, self.yRef2)
            self.plot3.plot(self.xRef3, self.yRef3)
            self.plot4.plot(self.xRef4, self.yRef4)

        # update plot
        self.canvas.draw()


    def create_widgets(self):
        # - - - - - - - - - - - - - - - - - - - - -
        # menuBar
        myMenuBar = Menu (self.window)

        myFileMenu = Menu (myMenuBar , tearoff = 0)
        myFileMenu.add_command(label = "Exit", command = self.close_file)
        myFileMenu.add_command(label = "Open", command = self.open_file)
        myFileMenu.add_command(label = "Save as", command = self.save_file)
        myMenuBar.add_cascade(label = "File", menu = myFileMenu)

        myFileMenu = Menu (myMenuBar , tearoff = 0)
        myFileMenu.add_command(label = "Info", command = self.show_info)
        myMenuBar.add_cascade(label = "Help", menu = myFileMenu)

        self.window.config(menu = myMenuBar)

        # create some room around all the internal frames
        self.window['padx'] = 10
        self.window['pady'] = 10

        # - - - - - - - - - - - - - - - - - - - - -
        # title
        self.labeled_frame_label = ttk.Label(self.window, text=" \n ")
        self.labeled_frame_label.grid(row=0, column=0, sticky=W, padx=10, pady=5)

        # display button
        self.hostname_field = Entry(self.window, width=35)
        self.hostname_field.insert(30, self.hostname_value)
        self.hostname_field.grid(row=0, column=1, sticky = tk.W, padx=10, pady = 5)

        self.connect_device = Button(self.window, text='CONNECT', fg='Black', command= self.instrument_connection)
        self.connect_device.grid(row=0, column=1, sticky = tk.E, padx=10, pady = 5)

        # - - - - - - - - - - - - - - - - - - - - -
        # user data frame
        frame = ttk.LabelFrame(self.window, text="USER DATA", relief=tk.RIDGE)
        frame.grid(row=1, column=1, sticky = tk.E + tk.W + tk.N + tk.S, padx=10, pady=10)

        # display label
        name = Label(frame, text='Name (User):')
        name.grid(row=1, column=0, sticky = W)
        self.name_field = Entry(frame)
        self.name_field.grid(row=1, column=1, padx=5, pady = 5)

        serial_name = Label(frame, text='Serial name:')
        serial_name.grid(row=2, column=0, sticky = W)
        self.serial_name_field = Entry(frame)
        self.serial_name_field.grid(row=2, column=1, padx=5, pady = 5)

        serial_number = Label(frame, text='Serial num.:')
        serial_number.grid(row=3, column=0, sticky = W)
        self.serial_number_field = Entry(frame)
        self.serial_number_field.grid(row=3, column=1, padx=5, pady = 5)

        details = Label(frame, text='Add details:')
        details.grid(row=4, column=0, sticky = W)
        self.details_field = Entry(frame)
        self.details_field.grid(row=5, column=0, sticky = E + W, columnspan=2, padx=5, pady = 5)

        # display check button
        self.var = IntVar(value=1)
        self.check_save_file = Checkbutton(frame, text = "Save data after measure", variable=self.var, command= self.save_sheet)
        self.check_save_file.grid(row=10, column=0, padx=0, pady=5)

        # display button
        self.save_ref = Button(frame, text='Save ref.', fg='Black', command= self.save_ref)
        self.save_ref.grid(row=11, column=0, columnspan=2, sticky = W, padx=20, pady = 5)

        submit = Button(frame, text='START MEASURE', fg='Black', command= self.start_test)
        submit.grid(row=11, column=1, columnspan=2, sticky = E, padx=20, pady = 5)

        # create loading bar
        self.prog_bar = Progress_bar(frame, row=30, columnspan=2, sticky = tk.E + tk.W + tk.N + tk.S, padx=5, pady=10)

        # display time
        self.clock = Label(frame)
        self.clock.grid(row=31, column=0, sticky = tk.W + tk.N + tk.S, padx=5, pady=5)

        # - - - - - - - - - - - - - - - - - - - - -
        # plot setup
        plt.style.use('bmh')

        self.fig = Figure()
        self.fig = plt.gcf()
        DPI = self.fig.get_dpi()
        self.fig.set_size_inches(1280.0/float(DPI), 720.0/float(DPI))

        # subplot
        self.plot0 = self.fig.add_subplot(231)
        self.plot1 = self.fig.add_subplot(232)
        self.plot2 = self.fig.add_subplot(233)
        self.plot3 = self.fig.add_subplot(234)
        self.plot4 = self.fig.add_subplot(235)

        # set axis names
        self.set_axis_name()

        # autoadapt
        plt.tight_layout()

        # draw
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.window)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=1, column=0, sticky=tk.E + tk.W + tk.N + tk.S, padx=10, pady=10)

        # - - - - - - - - - - - - - - - - - - - - -
        # event
        self.update_screen()

        # whenever the enter key is pressed then call the focus1 function
        self.window.bind('<Return>', self.focus)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from multi_thread import *
import time
from time import gmtime, strftime
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
    # auto-update
    def update_screen(self):
        try:
            if self.measure_thread.measure_started:
                self.prog_bar.pb_start()

            if self.measure_thread.data_ready:
                self.create_plot()

                self.measure_thread.data_ready = False
                self.prog_bar.pb_complete()

                if self.save_data:
                    self.measure_thread.create_sheet()
        except:
            pass

        self.clock.config(text=strftime("%d %b %Y %H:%M:%S", gmtime()))
        self.clock.after(1000, self.update_screen)

    # - - - - - - - - - - - - - - - - - - - - -
    # user pannel

    def save_ref(self):
        self.plot_reference = self.var1.get()
        if self.plot_reference == True:
            self.plot_saveRef = True

        try:
            self.create_plot()
        except:
            pass

    def start_test(self):
        self.instrument_connection(start_test = True)
        self.measure_thread.file_name = self.serial_name_field.get() + '_' + self.serial_number_field.get() + '_' + self.details_field.get()
        self.measure_thread.time_value = strftime("%d %b %Y %H:%M:%S", gmtime())

    def instrument_connection(self, start_test = False):
        self.measure_thread = Measure_thread(self.hostname_field.get(), start_test)
        self.measure_thread.start()

        instrument_name = self.measure_thread.instrument_info
        self.labeled_frame_label.config(text=instrument_name)

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
        menuBar = Menu (self.window)

        fileMenu = Menu (menuBar , tearoff = 0)
        fileMenu.add_command(label = "Exit", command = self.close_file)
        fileMenu.add_command(label = "Open", command = self.open_file)
        fileMenu.add_command(label = "Save as", command = self.save_file)
        menuBar.add_cascade(label = "File", menu = fileMenu)

        fileMenu = Menu (menuBar , tearoff = 0)
        fileMenu.add_command(label = "Info", command = self.show_info)
        menuBar.add_cascade(label = "Help", menu = fileMenu)

        self.window.config(menu = menuBar)

        # create some room around all the internal frames
        self.window['padx'] = 10
        self.window['pady'] = 10

        # - - - - - - - - - - - - - - - - - - - - -
        frame1 = ttk.Frame(self.window)
        frame1.grid(row=0, column=0, sticky = tk.E + tk.W + tk.N)

        frame2 = ttk.Frame(self.window)
        frame2.grid(row=0, column=1, sticky = tk.E + tk.W + tk.N)

        # display button
        frame_button = ttk.LabelFrame(frame2, text="REMOTE CONNECTION")
        frame_button.grid(row=0, column=0, sticky = tk.E + tk.W + tk.N + tk.S, padx=10, pady=10)

        self.hostname_field = Entry(frame_button, width=35)
        self.hostname_field.insert(30, self.hostname_value)
        self.hostname_field.grid(row=0, column=0, sticky=W, padx=5, pady=5)

        self.connect_device = Button(frame_button, text='CONNECT', fg='Black', command= self.instrument_connection)
        self.connect_device.grid(row=0, column=1, sticky=E, padx=5, pady=5)

        self.labeled_frame_label = ttk.Label(frame_button, text=" \n ")
        self.labeled_frame_label.grid(row=1, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        # - - - - - - - - - - - - - - - - - - - - -
        # user data frame_user
        frame_user = ttk.LabelFrame(frame2, text="USER DATA", relief=tk.RIDGE)
        frame_user.grid(row=2, column=0, sticky = tk.E + tk.W + tk.N + tk.S, padx=10, pady=10)

        # display label
        name = Label(frame_user, text='Name (User):')
        name.grid(row=1, column=0, sticky = W)
        self.name_field = Entry(frame_user)
        self.name_field.grid(row=1, column=1, sticky = E, pady=5)

        serial_name = Label(frame_user, text='Serial name:')
        serial_name.grid(row=2, column=0, sticky = W)
        self.serial_name_field = Entry(frame_user)
        self.serial_name_field.grid(row=2, column=1, sticky = E, pady=5)

        serial_number = Label(frame_user, text='Serial num.:')
        serial_number.grid(row=3, column=0, sticky = W)
        self.serial_number_field = Entry(frame_user)
        self.serial_number_field.grid(row=3, column=1, sticky = E, pady=5)

        details = Label(frame_user, text='Add details:')
        details.grid(row=4, column=0, sticky = W)
        self.details_field = Entry(frame_user)
        self.details_field.grid(row=4, column=1, sticky = E, pady=5)

        # display check button
        self.var = IntVar(value= self.save_data)
        self.check_save_file = Checkbutton(frame_user, text = "Save data after measure", variable=self.var, command= self.save_sheet)
        self.check_save_file.grid(row=10, column=0, sticky=W, padx=0, pady=5)

        self.var1 = IntVar(value= self.plot_reference)
        self.check_save_ref = Checkbutton(frame_user, text = "Save reference", variable=self.var1, command= self.save_ref)
        self.check_save_ref.grid(row=11, column=0, sticky=W, padx=0, pady=5)

        # display button
        submit = Button(frame_user, text='START MEASURE', fg='Black', command= self.start_test)
        submit.grid(row=11, column=1, sticky = E, padx=20, pady = 5)

        # create loading bar
        self.prog_bar = Progress_bar(frame_user, row=30, columnspan=2, sticky = E + W + N + S, padx=5, pady=10)

        # display time
        self.clock = Label(frame_user)
        self.clock.grid(row=31, column=0, sticky = tk.W + tk.N + tk.S, padx=5, pady=5)

        # - - - - - - - - - - - - - - - - - - - - -
        # details_frame
        details_frame = ttk.LabelFrame(frame2, text="DETAILS")
        details_frame.grid(row=3, column=0, sticky = tk.E + tk.W + tk.N + tk.S, padx=10, pady=10)

        details_label = ttk.Label(details_frame, text="Add functions...")
        details_label.grid(row=1, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        # - - - - - - - - - - - - - - - - - - - - -
        # Notebook
        note = ttk.Notebook(frame1)
        note.pack()

        self.tab1 = ttk.Frame(note)
        self.tab2 = ttk.Frame(note)

        note.add(self.tab1, text = "Flanges")
        note.add(self.tab2, text = "Pick-Up")

        # - - - - - - - - - - - - - - - - - - - - -
        # plot setup
        #plt.style.use('bmh')

        #Figure 1
        fig1 = Figure(figsize=(14,7))

        #fig1.suptitle('Sampled signal')

        self.plot0 = fig1.add_subplot(2,3,1)
        self.plot0.set_title("Channel X")
        self.plot0.set_xlabel('g')
        self.plot0.set_ylabel('g')
        self.plot0.grid()

        self.plot1 = fig1.add_subplot(2,3,2)
        self.plot1.set_title("Channel Y")
        self.plot1.set_xlabel('ms')
        self.plot1.set_ylabel('g')
        self.plot1.grid()

        self.plot2 = fig1.add_subplot(2,3,3)
        self.plot2.set_title("Channel Y")
        self.plot2.set_xlabel('ms')
        self.plot2.set_ylabel('g')
        self.plot2.grid()

        self.plot3 = fig1.add_subplot(2,3,4)
        self.plot3.set_title("Channel Y")
        self.plot3.set_xlabel('ms')
        self.plot3.set_ylabel('g')
        self.plot3.grid()

        self.plot4 = fig1.add_subplot(2,3,5)
        self.plot4.set_title("Channel Y")
        self.plot4.set_xlabel('ms')
        self.plot4.set_ylabel('g')
        self.plot4.grid()

        #add comment
        self.set_axis_name()

        #Figure 2
        fig2 = Figure()

        #fig2.suptitle('Data received')

        ax_21 = fig2.add_subplot(1,2,1)
        #ax_21.hold(False)
        ax_21.set_title("Channel X")
        ax_21.set_ylabel('g')
        ax_21.grid()

        ax_22 = fig2.add_subplot(1,2,2)
        #ax_21.hold(False)
        ax_22.set_title("Channel X")
        ax_22.set_ylabel('g')
        ax_22.grid()

        # autoadapt
        fig1.tight_layout()
        fig2.tight_layout()

        # Canvas1
        self.canvas1 = FigureCanvasTkAgg(fig1, master=self.tab1)
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar1 = NavigationToolbar2Tk(self.canvas1, self.tab1)
        self.toolbar1.update()
        self.canvas1._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Canvas2
        self.canvas2 = FigureCanvasTkAgg(fig2, master=self.tab2)
        self.canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar2 = NavigationToolbar2Tk(self.canvas2, self.tab2)
        self.toolbar2.update()
        self.canvas2._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # - - - - - - - - - - - - - - - - - - - - -
        # event
        self.update_screen()

        # whenever the enter key is pressed then call the focus1 function
        self.window.bind('<Return>', self.focus)

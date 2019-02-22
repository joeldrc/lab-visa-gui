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
        except Exception as e:
            print(e)

        try:
            if self.measure_thread.data_ready:
                self.create_plot()

                self.measure_thread.data_ready = False
                self.prog_bar.pb_complete()

                try:
                    if self.save_data:
                        self.measure_thread.create_sheet()
                except Exception as e:
                    print(e)
                    messagebox.showerror(title = 'Error', message = e)

        except Exception as e:
            print(e)

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
        except Exception as e:
            print(e)

    def start_test(self):
        #check wich frame you have selected (return int)
        selected_frame_number = self.note.index("current")
        #print(selected_frame_number)
        self.instrument_connection(start_test = True, frame_number = selected_frame_number)
        self.measure_thread.file_name = self.serial_name_field.get() + '_' + self.serial_number_field.get() + '_' + self.details_field.get()
        self.measure_thread.time_value = strftime("%d %b %Y %H:%M:%S", gmtime())

    def instrument_connection(self, start_test = False, frame_number = 0):
        self.measure_thread = Measure_thread(self.hostname_field.get(), start_test, frame_number)
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
        #Fig 1
        self.plot[0].set_title('S21 - delay')
        self.plot[0].set_xlabel('freq')
        self.plot[0].set_ylabel('dB')
        self.plot[1].set_title('S21 - dB')
        self.plot[1].set_xlabel('freq')
        self.plot[1].set_ylabel('dB')
        self.plot[2].set_title('S11 - SWR')
        self.plot[2].set_xlabel('freq')
        self.plot[2].set_ylabel('dB')
        self.plot[3].set_title('S22 - SWR')
        self.plot[3].set_xlabel('freq')
        self.plot[3].set_ylabel('dB')
        self.plot[4].set_title('S11 - TDR')
        self.plot[4].set_xlabel('delay')
        self.plot[4].set_ylabel('dB')

        #Fig 2
        self.plot[5].set_title('S11 - TDR')
        self.plot[5].set_xlabel('delay')
        self.plot[5].set_ylabel('dB')
        self.plot[6].set_title('S11 - TDR')
        self.plot[6].set_xlabel('delay')
        self.plot[6].set_ylabel('dB')

        #set grid on
        for i in range(0,7,1):
            self.plot[i].grid()

    def create_plot(self):
        selected_frame_number = self.note.index("current")
        xValue = []
        yValue = []

        if selected_frame_number == 0:
            for i in range(0,5,1):
                x, y = self.measure_thread.measures_0[i]
                xValue.append(x)
                yValue.append(y)

            if self.plot_saveRef == True:
                self.xRef = xValue
                self.yRef = yValue
                self.plot_saveRef = False

            for i in range(0,5,1):
                # clean plot line
                self.plot[i].cla()
                # set data on plot
                self.plot[i].plot(xValue[i], yValue[i])

            if self.plot_reference == True:
                for i in range(0,5,1):
                    self.plot[i].plot(self.xRef[i], self.yRef[i])

            # set axis names
            self.set_axis_name()
            # autoadapt
            self.fig1.tight_layout()
            # update plot
            self.canvas1.draw()

        elif selected_frame_number == 1:
            for i in range(0,2,1):
                x, y = self.measure_thread.measures_1[i]
                xValue.append(x)
                yValue.append(y)

            if self.plot_saveRef == True:
                self.xRef = xValue
                self.yRef = yValue
                self.plot_saveRef = False

            for i in range(0,2,1):
                # clean plot line
                self.plot[i + 5].cla()
                # set data on plot
                self.plot[i + 5].plot(xValue[i], yValue[i])

            if self.plot_reference == True:
                for i in range(0,2,1):
                    self.plot[i + 5].plot(self.xRef[i], self.yRef[i])

            # set axis names
            self.set_axis_name()
            # autoadapt
            self.fig2.tight_layout()
            # update plot
            self.canvas2.draw()

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
        self.window['padx'] = 5
        self.window['pady'] = 5

        # - - - - - - - - - - - - - - - - - - - - -
        frame1 = ttk.Frame(self.window)
        frame1.grid(row=0, column=0, sticky = tk.E + tk.W + tk.N)

        frame2 = ttk.Frame(self.window)
        frame2.grid(row=0, column=1, sticky = tk.E + tk.W + tk.N)

        # display button
        frame_button = ttk.LabelFrame(frame2, text="REMOTE CONNECTION")
        frame_button.grid(row=0, column=0, sticky = tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

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
        frame_user.grid(row=2, column=0, sticky = tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

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
        details_frame.grid(row=3, column=0, sticky = tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        details_label = ttk.Label(details_frame, text="Add functions...")
        details_label.grid(row=1, column=0, columnspan=2, sticky=W, padx=5, pady=5)

        # - - - - - - - - - - - - - - - - - - - - -
        # Notebook
        self.note = ttk.Notebook(frame1)
        self.note.pack(padx=5, pady=5)

        self.tab1 = ttk.Frame(self.note)
        self.tab2 = ttk.Frame(self.note)

        self.note.add(self.tab1, text = "Flanges")
        self.note.add(self.tab2, text = "Pick-Up")

        # - - - - - - - - - - - - - - - - - - - - -
        # plot setup
        #plt.style.use('bmh')
        self.plot = []

        #Figure 1
        self.fig1 = Figure(figsize=(12,7))
        #self.fig1.suptitle('Sampled signal')
        for i in range(0,5,1):
            subplot = self.fig1.add_subplot(2,3,i + 1)
            self.plot.append(subplot)

        #Figure 2
        self.fig2 = Figure()
        #self.fig2.suptitle('Data received')
        for i in range(0,2,1):
            subplot = self.fig2.add_subplot(1,2,i + 1)
            self.plot.append(subplot)

        #set all axis names
        self.set_axis_name()
        # autoadapt
        self.fig1.tight_layout()
        self.fig2.tight_layout()

        # Canvas1
        self.canvas1 = FigureCanvasTkAgg(self.fig1, master=self.tab1)
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar1 = NavigationToolbar2Tk(self.canvas1, self.tab1)
        self.toolbar1.update()
        self.canvas1._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # Canvas2
        self.canvas2 = FigureCanvasTkAgg(self.fig2, master=self.tab2)
        self.canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)
        self.toolbar2 = NavigationToolbar2Tk(self.canvas2, self.tab2)
        self.toolbar2.update()
        self.canvas2._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # - - - - - - - - - - - - - - - - - - - - -
        # event
        self.update_screen()

        # whenever the enter key is pressed then call the focus1 function
        self.window.bind('<Return>', self.focus)

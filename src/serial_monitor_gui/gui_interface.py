#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import matplotlib
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)

# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure

from scipy import fftpack, arange, signal
import numpy as np

import sys

from tkinter import *
import tkinter as tk
from tkinter import filedialog
from tkinter import messagebox
from tkinter.scrolledtext import ScrolledText
from tkinter import ttk

import time

from serial_functions import*


class User_gui(tk.Frame):

    def __init__(self, parent):

        #Variables
        self.f_saved = True       #Sampled data saved
        self.data_to_read = 16384     # Amount of samples to read.

        self.sample_rate = 5000       # Sampling frequency (SPS).
        self.g_scale = (3.3 / 1024) * (1000/300)  #(Vref / ADC resolution) * 1/(300 mv/g)
        self.max_freq = 1500          # Maximum signal frequency, X and Y axis (accelerometer).
        self.max_freq_z = 500         # Maximum signal frequency, Z axis (accelerometer).

        self.g_channel_1 = []           #channel_1
        self.g_channel_2 = []           #channel_2
        self.g_channel_3 = []           #channel_3

        self.t_timeout = 8            #Timeout time in seconds.

        # Parameters
        self.window = parent
        self.frames()

        self.window.protocol("WM_DELETE_WINDOW", self.close_file)
        self.window.title("TEST GUI - V.1.0")


    def close_file(self):
        if (self.f_saved==False):
            if messagebox.askokcancel("Quit", "Sampled data not saved. Do you wanto to quit?"):
                self.window.destroy()
        else:
            self.window.destroy()


    def show_info(self):
        messagebox.showinfo(title = 'About Me!', message = 'joel.daricou@cern.ch 2018')


    def frames(self):
        frame1 = ttk.LabelFrame(self.window, text="USER DATA", relief=tk.RIDGE)
        frame2 = ttk.Frame(self.window)

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

        # Notebook
        note = ttk.Notebook(frame2)
        self.tab1 = ttk.Frame(note)
        self.tab2 = ttk.Frame(note)

        note.add(self.tab1, text = "Frequency")
        note.add(self.tab2, text = "Time")

        # Positioning
        frame1.grid(row=0, column=2, padx=10, pady=10, sticky = tk.E + tk.W + tk.N + tk.S)
        frame2.grid(row=0, column=1, padx=5, pady=5, sticky = tk.E + tk.W + tk.N + tk.S)

        button_scan = tk.Button(frame1, text="Scan serial ports", command=self.scan_ports)
        button_read = tk.Button(frame1, text="Read serial data", command=self.read_serial)

        label1 = tk.Label(frame1, text="Select Serial Port:")
        self.sel_port = ttk.Combobox(frame1, textvariable='', state="readonly")
        ports_names = scan_serial()
        self.sel_port['values'] = ports_names
        if (ports_names != []):
            self.sel_port.current(0)

        self.text_message = ScrolledText(frame1, height=10, width=20)

        # Grid
        label1.grid(row=0, column=0, padx=5, pady=5)
        self.sel_port.grid(row=1, column=0, padx=5, pady=5)
        button_scan.grid(row=2, column=0, padx=5, pady=5)
        button_read.grid(row=3, column=0, padx=5, pady=5)
        self.text_message.grid(row=4, column=0, padx=5, pady=5)

        #note.grid(row = 0, column=0)
        note.pack(side='top', fill='both', padx=5, pady=5)

        #Figure 1
        fig1 = Figure(figsize=(10,9))
        fig1.suptitle('Sampled signal - Acceleration')
        ax_11 = fig1.add_subplot(3,1,1)
        #ax_11.hold(False)
        ax_11.set_title("Channel X")
        ax_11.set_ylabel('g')
        ax_11.grid()                       #Shows grid.

        ax_12 = fig1.add_subplot(3,1,2)
        #ax_12.hold(False)
        ax_12.set_title("Channel Y")
        #ax_12.set_xlabel('ms')
        ax_12.set_ylabel('g')
        ax_12.grid()                       #Shows grid.

        ax_12 = fig1.add_subplot(3,1,3)
        #ax_12.hold(False)
        ax_12.set_title("Channel Z")
        ax_12.set_xlabel('ms')
        ax_12.set_ylabel('g')
        ax_12.grid()                       #Shows grid.

        #Figure 2
        fig2 = Figure(figsize=(10,9))
        fig2.suptitle('Data received')

        ax_21 = fig2.add_subplot(1,1,1)
        #ax_21.hold(False)
        ax_21.set_title("Channel X")
        ax_21.set_ylabel('g')
        ax_21.set_xlim(right=self.max_freq)
        ax_21.grid()

        # Canvas
        self.canvas2 = FigureCanvasTkAgg(fig1, master=self.tab2)
        self.canvas2.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar2 = NavigationToolbar2Tk(self.canvas2, self.tab2)
        self.toolbar2.update()
        self.canvas2._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.canvas1 = FigureCanvasTkAgg(fig2, master=self.tab1)
        self.canvas1.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        self.toolbar1 = NavigationToolbar2Tk(self.canvas1, self.tab1)
        self.toolbar1.update()
        self.canvas1._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)


    def read_serial(self):
        port = self.sel_port.get()
        print(port)
        message_string = "Port: {0} \n".format(port)
        self.show_message(self.text_message, message_string)

        serial_state = False
        try:
            serial_avr = serial.Serial(port=port, baudrate=500000,
                           bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                           stopbits=serial.STOPBITS_ONE, timeout=0)

            time.sleep(2)            # waiting the initialization...
            print("Initializing")
            message_string = "Initializing... \n"
            self.show_message(self.text_message, message_string)

            if (serial_avr.isOpen() == True):
                serial_state = True
            else:
                serial_state = False
        except:
            messagebox.showerror( "Result", "Can't open serial port: ")

        if (serial_state == True):
            channel_1 = []
            channel_2 = []
            channel_3 = []
            buffer = []
            pack = []
            values = []
            serial_avr.flushInput()
            serial_avr.flushOutput()

            values_decod = []

            received_data_counter = 0;         #Received samples counter.

            print("Sending INI")
            message_string = "Sending INI \n"
            self.show_message(self.text_message, message_string)

            serial_avr.write(b'INI')         #Start data sampling command.
            #serial_avr.write(chr(0x22))    #CRC 'INI'. Not used.
            serial_avr.write(b"\x7E")     #End of packet.

            timeout_state = False
            t0 = time.time()       #Start loop time stamp.
            while ((received_data_counter < self.data_to_read) and (timeout_state == False)):
                if serial_avr.inWaiting():
                    val_read = serial_avr.read(serial_avr.inWaiting())
                    buffer += val_read
                    values = []
                if len(buffer) > 15:
                    try:
                        i = buffer.index(0x7E)
                    except (ValueError):
                        i = -1
                    #print("Buffer: {0}".format(buffer))
                    if i >= 0:
                        pack = buffer[:i]
                        buffer =  buffer[i+1:]
                        #print("pack: {0}".format(pack))
                        values=[i for i in pack]
                        pack = ''

                        x = 0
                        while x < len(values):
                            if values[x] == 0x7D:
                                values_decod.append(values[x+1] ^ 0x20)
                                x = x + 1
                            else:
                                values_decod.append(values[x])
                            x = x + 1

                        channel1 = (values_decod[0] * 256) + values_decod[1]
                        channel2 = (values_decod[2] * 256) + values_decod[3]
                        channel3 = (values_decod[4] * 256) + values_decod[5]

                        channel_1.append(channel1)
                        channel_2.append(channel2)
                        channel_3.append(channel3)

                        #print("channel 1: %s    channel2: %s  " % (channel1, channel2))

                        values = []
                        values_decod = []

                        received_data_counter += 1 ;
                        #print("received_data_counter =  %s" %received_data_counter)

                #Check if self.t_timeout seconds have elapsed since time stamp t0
                if ((time.time() - t0) > self.t_timeout):
                    timeout_state = True
                    #print("Serial port timeout")

            if (timeout_state == False):
                print("Sending PAR")
                self.text_message.config(state=tk.NORMAL)        #Enable to modify
                self.text_message.insert(tk.END, "Sending PAR \n")
                self.text_message.config(state=tk.DISABLED)      #Disable - Read only
                self.window.update_idletasks()        #Needed to make message visible

                serial_avr.write(b'PAR')          #Stop data sampling.
                serial_avr.write(b"\x7E")         #End of packet.

                serial_avr.close()                #Close serial port.

                print("Amount of samples channel 1: %s" %len(channel_1))
                print("Amount of samples channel 2: %s" %len(channel_2))
                print("Amount of samples channel 3: %s" %len(channel_3))
                message_string = "Amount of samples channel 1: {0} \n".format(len(channel_1))
                message_string += "Amount of samples channel 2: {0} \n".format(len(channel_2))
                message_string += "Amount of samples channel 3: {0} \n".format(len(channel_3))
                self.show_message(self.text_message, message_string)

                #Keep a copy of the original values
                self.g_channel_1 = channel_1[:]            #Copy list by value not by reference
                self.g_channel_2 = channel_2[:]
                self.g_channel_3 = channel_3[:]

                self.f_saved = False                #Sampled data not saved

                self.window_var.set(1)        #Option rectangular window
                self.plot(self.tab1, self.tab2, channel_1, channel_2, channel_3, win_var=1)
            else:
                serial_avr.write(b'PAR')          #Stop data sampling.
                serial_avr.write(b"\x7E")         #End of packet.
                serial_avr.close()                #Close serial port.
                print("Serial port timeout")
                message_string = ("Serial port timeout \n")
                self.show_message(self.text_message, message_string)


    def show_message(self, text_message, message_string):
        """Shows messages on a scrollable textbox"""
        text_message.config(state=tk.NORMAL)        #Enable to modify
        text_message.insert(tk.END, message_string)
        text_message.config(state=tk.DISABLED)      #Disable - Read only
        text_message.see("end")        #Show the "end" of text
        self.window.update_idletasks()        #Needed to make message visible


    def scan_ports(self):
        ports_names = []
        ports_names = scan_serial()
        self.sel_port['values'] = ports_names
        if (ports_names != []):
            self.sel_port.current(0)


    def plot(self, tab1, tab2, channel_1, channel_2, channel_3, win_var=1):
        num_datos = len(channel_1)
        X = range(0, num_datos, 1)

        # Scale the signal in g's
        for indice in X:
            channel_1[indice] *= self.g_scale
            channel_2[indice] *= self.g_scale
            channel_3[indice] *= self.g_scale

        # Calculates medium value for each channel.
        vdc_channel_1 = 0
        vdc_channel_2 = 0
        vdc_channel_3 = 0
        for indice in X:
            vdc_channel_1 += channel_1[indice]
            vdc_channel_2 += channel_2[indice]
            vdc_channel_3 += channel_3[indice]
        vdc_channel_1 = vdc_channel_1 / num_datos
        vdc_channel_2 = vdc_channel_2 / num_datos
        vdc_channel_3 = vdc_channel_3 / num_datos
        #print("Vdc Channel 1: {0}, Vdc Channel 2: {1}".format(vdc_channel_1, vdc_channel_2))

        # Substract DC offset
        for indice in X:
            channel_1[indice] -= vdc_channel_1
            channel_2[indice] -= vdc_channel_2
            channel_3[indice] -= vdc_channel_3

        #----------------- Plotting ----------
        X1 = np.linspace(0, num_datos/5, num=num_datos)     # X axis, 5000 sps, 1/5 ms.

        # Figure 1. Sampled signals.
        #Channel X
        ax_11, ax_12, ax_13 = self.canvas2.figure.get_axes()
        ax_11.clear()
        ax_11.plot(X1,channel_1)
        ax_11.set_title("Channel X")
        ax_11.set_ylabel('g')
        ax_11.grid()                       #Shows grid.

        #Channel Y
        ax_12.clear()
        ax_12.plot(X1,channel_2)
        ax_12.set_title("Channel Y")
        #ax_12.set_xlabel('ms')
        ax_12.set_ylabel('g')
        ax_12.grid()                       #Shows grid.

        #Channel Z
        ax_13.clear()
        ax_13.plot(X1,channel_3)
        ax_13.set_title("Channel Z")
        ax_13.set_xlabel('ms')
        ax_13.set_ylabel('g')
        ax_13.grid()                       #Shows grid.

        # Figure 2. FFT from signals.
        #Channel X
        channel_fft = []
        channel_fft = channel_1

        N = len(channel_fft)         # length of the signal

        #Window function
        if(win_var == 2):
            w = signal.hann(N, sym=False)      #Hann (Hanning) window
        elif(win_var == 3):
            w = signal.flattop(N, sym=False)   #Flattop window
        else:
            w = 1                              #Rectangular window

        T = 1.0 / self.sample_rate
        y = channel_fft
        yf = fftpack.fft(y*w)*(2/N)
        yf = yf[:int(N/2)]
        xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

        ax_21, ax_22, ax_23 = self.canvas1.figure.get_axes()
        ax_21.clear()
        #ax_21.plot(xf, 2.0/N * np.abs(yf[:N/2]))
        ax_21.plot(xf, np.abs(yf))
        ax_21.grid()
        ax_21.set_title("Channel X")
        ax_21.set_ylabel('g')
        ax_21.set_xlim(right=self.max_freq)

        #Channel Y
        channel_fft = []
        channel_fft = channel_2

        N = len(channel_fft)              # length of the signal
        T = 1.0 / self.sample_rate
        y = channel_fft
        yf = fftpack.fft(y*w)*(2/N)
        yf = yf[:int(N/2)]
        xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

        ax_22.clear()
        #ax_22.plot(xf, 2.0/N * np.abs(yf[:N/2]))
        ax_22.plot(xf, np.abs(yf))
        ax_22.grid()
        ax_22.set_title("Channel Y")
        #ax_22.set_xlabel('Hz')
        ax_22.set_xlim(right=self.max_freq)
        ax_22.set_ylabel('g')

        #Channel Z
        channel_fft = []
        channel_fft = channel_3

        N = len(channel_fft)              # length of the signal
        T = 1.0 / self.sample_rate
        y = channel_fft
        yf = fftpack.fft(y*w)*(2/N)
        yf = yf[:int(N/2)]
        xf = np.linspace(0.0, 1.0/(2.0*T), N/2)

        ax_23.clear()
        #ax_23.plot(xf, 2.0/N * np.abs(yf[:N/2]))
        ax_23.plot(xf, np.abs(yf))
        ax_23.grid()
        ax_23.set_title("Channel Z")
        ax_23.set_xlabel('Hz')
        #ax_23.set_xlim(right=self.max_freq)
        ax_23.set_xlim(right=self.max_freq_z)
        ax_23.set_ylabel('g')

        self.canvas1.draw()
        self.canvas2.draw()


    def win_sel(self):
        """Window selection. Every time a window is selected,
        the FFT spectrum is calculated, applying the selected window function"""
        channel_1 = self.g_channel_1[:]            #Copy list by value not by reference
        channel_2 = self.g_channel_2[:]
        channel_3 = self.g_channel_3[:]
        win_var = self.window_var.get()
        if(len(channel_1) != 0):            #Apply only if data available
            self.plot(self.tab1, self.tab2, channel_1, channel_2, channel_3, win_var)


    def open_file(self):
        """Opens dialog to select a file, reads data from file and plots the data"""
        ftypes = [('Text files', '*.txt'), ('All files', '*')]
        dlg = filedialog.Open(self.window, filetypes = ftypes)
        fl = dlg.show()
        if fl != '':
            # Open file for reading
            arch = open(fl, "r")
            data_arch = arch.read()
            # Searches for every channel, delimited by L1, L2 and L3 tags.
            channel_1 = extract_int_tag(data_arch, 'L1')
            channel_2 = extract_int_tag(data_arch, 'L2')
            channel_3 = extract_int_tag(data_arch, 'L3')

            print("Amount of samples in channel 1: %s" %len(channel_1))
            print("Amount of samples on channel 2: %s" %len(channel_2))
            print("Amount of samples on channel 3: %s" %len(channel_3))
            message_string = "Amount of samples channel 1: {0} \n".format(len(channel_1))
            message_string += "Amount of samples channel 2: {0} \n".format(len(channel_2))
            message_string += "Amount of samples channel 3: {0} \n".format(len(channel_3))
            self.show_message(self.text_message, message_string)

            #Keep a copy of the original values
            self.g_channel_1 = channel_1[:]            #Copy list by value not by reference
            self.g_channel_2 = channel_2[:]
            self.g_channel_3 = channel_3[:]

            self.window_var.set(1)        #Option rectangular window
            self.plot(self.tab1, self.tab2, channel_1, channel_2, channel_3, win_var=1)


    def save_file(self):
        ftypes = [('Text files', '*.txt'), ('All files', '*')]
        dlg = filedialog.SaveAs(self.window, filetypes = ftypes)
        fl = dlg.show()
        if fl != '':
            if (len(self.g_channel_1) > 0):
                grabar(self.g_channel_1, self.g_channel_2, self.g_channel_3, fl)
                self.f_saved = True               #Sampled data saved
            else:
                print("No samled data to save")
                message_string = "No samled data to save\n"
                self.show_message(self.text_message, message_string)

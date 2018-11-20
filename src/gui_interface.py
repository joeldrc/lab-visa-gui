from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import colorchooser

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

from openpyxl import *

#global variables
file_position = ' '

# opening the existing excel file
wb = Workbook()
# create the sheet object
sheet = wb.active

class Frame_examples_program():

	
    def __init__(self):
        self.window = tk.Tk()
        #self.window.geometry('600x600') 
        self.window.title("BUTTON TEST")
        self.create_widgets()


    def create_buttons(self, parent, a, b, c):
        button1 = ttk.Button(parent, text="do task " + a)
        button1.grid(row=1, column=1)
        button2 = ttk.Button(parent, text="do task " + b)
        button2.grid(row=2, column=1)
        button3 = ttk.Button(parent, text="do task " + c)
        button3.grid(row=3, column=1)

        return (button1, button2, button3)
	
	
    def show_info(self):
        messagebox.showinfo(title = 'About Me!', message = 'joel.daricou@cern.ch 2018')
        return


    def new_file(self):
        global file_position
        file_position = filedialog.asksaveasfilename(initialdir = "/",title = "Select file",filetypes = (("Microsoft Excel Worksheet","*.xlsx"),("all files","*.*")), defaultextension = ' ')
        wb.save(file_position)


    def open_file(self):
        global file_position
        file_position = filedialog.askopenfile().name
        

    def close_file(self):
        exit = messagebox.askyesno(title = 'Quit?', message = 'Are you sure?')
        if exit > 0:
            self.window.destroy()
            return


    def create_widgets(self):
        # Create some room around all the internal frames
        self.window['padx'] = 5
        self.window['pady'] = 5


        # - - - - - - - - - - - - - - - - - - - - -
        # MenuBar
        myMenuBar = Menu (self.window)

        myFileMenu = Menu (myMenuBar , tearoff = 0)
        myFileMenu.add_command(label = "Exit", command = self.close_file)
        myFileMenu.add_command(label = "Open", command = self.open_file)
        myFileMenu.add_command(label = "Save as", command = self.new_file)
        myMenuBar.add_cascade(label = "File", menu = myFileMenu)

        myFileMenu = Menu (myMenuBar , tearoff = 0)
        myFileMenu.add_command(label = "Info", command = self.show_info)
        myMenuBar.add_cascade(label = "Help", menu = myFileMenu)

        self.window.config(menu = myMenuBar)
        
       
        # - - - - - - - - - - - - - - - - - - - - -
        # Title
        labeled_frame_label = ttk.Label(self.window, text="TEST")
        labeled_frame_label.grid(row=0, column=0, sticky=W)


        # - - - - - - - - - - - - - - - - - - - - -
        # User data
        frame = ttk.LabelFrame(self.window, text="USER DATA", relief=tk.RIDGE)
        frame.grid(row=1, column=0, sticky = tk.E + tk.W + tk.N + tk.S, padx=0, pady=20)
       
        name = Label(frame, text='Name:')
        name.grid(row=0, column=0, sticky = W)
        name_field = Entry(frame)
        name_field.grid(row=0, column=1, padx=0, pady = 5)

        serial_name = Label(frame, text='S. Name:')
        serial_name.grid(row=1, column=0, sticky = W)
        serial_name_field = Entry(frame)
        serial_name_field.grid(row=1, column=1, padx=0, pady = 5)

        serial_number = Label(frame, text='Ser. Num.:')
        serial_number.grid(row=2, column=0, sticky = W)
        serial_number_field = Entry(frame)
        serial_number_field.grid(row=2, column=1, padx=0, pady = 5)

        details = Label(frame, text='Details:')
        details.grid(row=3, column=0, sticky = W)
        details_field = Entry(frame)
        details_field.grid(row=4, column=0, sticky = E + W, columnspan=2)
        
        submit = Button(frame, text='Submit', fg='Black')
        submit.grid(row=10, column=0, columnspan=2, padx=0, pady = 5)


        # - - - - - - - - - - - - - - - - - - - - -
        # Title
        notebook_label = ttk.Label(self.window, text="Notebook")
        notebook_label.grid(row=2, column=0, sticky=tk.W, pady=3)


        # - - - - - - - - - - - - - - - - - - - - -
        # Setup

        frame2 = ttk.Notebook(self.window)
        frame2.grid(row=3, column=0, sticky=tk.E + tk.W + tk.N + tk.S, padx=0, pady=0)

        tab1 = tk.Frame(frame2)
        tab2 = tk.Frame(frame2)


        frame2.add(tab1, text="TEST", compound=tk.TOP)
        frame2.add(tab2, text="SETUP", compound=tk.TOP)
        

        self.create_buttons(tab1, "J", "K", "L")
        self.create_buttons(tab2, "M", "N", "O")
        

        # - - - - - - - - - - - - - - - - - - - - -
        # Plot
        plt.style.use('bmh')
        
        fig = Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(2 * np.pi * t))

        canvas = FigureCanvasTkAgg(fig, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, sticky=tk.W, pady=3)


        # - - - - - - - - - - - - - - - - - - - - -
        # Plot 2       
        fig = Figure(figsize=(5, 4), dpi=100)
        t = np.arange(0, 3, .01)
        fig.add_subplot(111).plot(t, 2 * np.sin(4 * np.pi * t))

        canvas1 = FigureCanvasTkAgg(fig, master=self.window)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=3, column=1, sticky=tk.W, pady=3)
        
      

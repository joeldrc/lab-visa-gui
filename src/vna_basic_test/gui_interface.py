import time

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog
from tkinter import colorchooser

from visa_scpi import vna_measure

from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.backend_bases import key_press_handler
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import numpy as np

from openpyxl import *


# variables
file_position = ' '

        
class Frame_examples_program():
	
    def __init__(self):
        self.window = tk.Tk()
        #self.window.geometry('600x600') 
        self.window.title("BUTTON TEST")
        self.create_widgets()

        # opening the existing excel file
        self.wb = Workbook()
        # create the sheet object
        self.sheet = self.wb.active
        

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


    def save_file(self):
        global file_position      
        file_name = self.name_field.get() + self.serial_name_field.get() + self.serial_number_field.get() + self.details_field.get()   
        file_position = filedialog.asksaveasfilename(initialdir = "/",initialfile=file_name, title = "Select file",filetypes = (("Microsoft Excel Worksheet","*.xlsx"),("all files","*.*")), defaultextension = ' ')
        self.wb.save(file_position)


    def open_file(self):
        global file_position
        file_position = filedialog.askopenfile().name
        

    def close_file(self):
        exit = messagebox.askyesno(title = 'Quit?', message = 'Are you sure?')
        if exit > 0:
            self.window.destroy()
            return
        

    def create_plot(self):
        self.display_info.config(text='START TEST')
        
        # masure vna
        xValue0, yValue0 = vna_measure(0)
        xValue1, yValue1 = vna_measure(1)
        xValue2, yValue2 = vna_measure(2)
        xValue3, yValue3 = vna_measure(3)
        xValue4, yValue4 = vna_measure(4)
      
        # - - - - - - - - - - - - - - - - - - - - -
        # Plot setup
        plt.style.use('bmh')

        # - - - - - - - - - - - - - - - - - - - - -
        # Plot 0        
        fig0 = Figure()
        
        fig0.add_subplot(111).plot(xValue0, yValue0)

        canvas = FigureCanvasTkAgg(fig0, master=self.window)
        canvas.draw()
        canvas.get_tk_widget().grid(row=1, column=1, sticky=tk.W, pady=3)
                                          
        # - - - - - - - - - - - - - - - - - - - - -
        # Plot 1       
        fig1 = Figure()
                      
        fig1.add_subplot(111).plot(xValue1, yValue1)

        canvas1 = FigureCanvasTkAgg(fig1, master=self.window)
        canvas1.draw()
        canvas1.get_tk_widget().grid(row=3, column=1, sticky=tk.W, pady=3)

        # - - - - - - - - - - - - - - - - - - - - -
        # Plot 2       
        fig2 = Figure()
                       
        fig2.add_subplot(111).plot(xValue2, yValue2)

        canvas2 = FigureCanvasTkAgg(fig2, master=self.window)
        canvas2.draw()
        canvas2.get_tk_widget().grid(row=1, column=2, sticky=tk.W, pady=3)

        # - - - - - - - - - - - - - - - - - - - - -
        # Plot 3       
        fig3 = Figure()
                       
        fig3.add_subplot(111).plot(xValue3, yValue3)

        canvas3 = FigureCanvasTkAgg(fig3, master=self.window)
        canvas3.draw()
        canvas3.get_tk_widget().grid(row=3, column=2, sticky=tk.W, pady=3)

        # - - - - - - - - - - - - - - - - - - - - -
        # Plot 4       
        fig4 = Figure()
                      
        fig4.add_subplot(111).plot(xValue4, yValue4)

        canvas4 = FigureCanvasTkAgg(fig4, master=self.window)
        canvas4.draw()
        canvas4.get_tk_widget().grid(row=1, column=3, sticky=tk.W, pady=3)

        # - - - - - - - - - - - - - - - - - - - - -
        # Create sheet
        """
        # resize the width of columns in excel spreadsheet
        self.sheet.column_dimensions['A'].width = 30
        self.sheet.column_dimensions['B'].width = 30
        """

        # write given data to an excel spreadsheet at particular location
        file_name = self.name_field.get() + self.serial_name_field.get() + self.serial_number_field.get() + self.details_field.get()
        self.sheet.cell(row=1, column=1).value = file_name

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
            
        self.display_info.config(text='TEST DONE')
        self.save_file()

            
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
        myFileMenu.add_command(label = "Save as", command = self.save_file)
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
        self.name_field = Entry(frame)
        self.name_field.grid(row=0, column=1, padx=0, pady = 5)

        serial_name = Label(frame, text='S. Name:')
        serial_name.grid(row=1, column=0, sticky = W)
        self.serial_name_field = Entry(frame)
        self.serial_name_field.grid(row=1, column=1, padx=0, pady = 5)

        serial_number = Label(frame, text='Ser. Num.:')
        serial_number.grid(row=2, column=0, sticky = W)
        self.serial_number_field = Entry(frame)
        self.serial_number_field.grid(row=2, column=1, padx=0, pady = 5)

        details = Label(frame, text='Details:')
        details.grid(row=3, column=0, sticky = W)
        self.details_field = Entry(frame)
        self.details_field.grid(row=4, column=0, sticky = E + W, columnspan=2)
        
        submit = Button(frame, text='Submit', fg='Black', command= self.create_plot)
        submit.grid(row=10, column=0, columnspan=2, padx=0, pady = 5)

        self.display_info = ttk.Label(frame, text= ' ')
        self.display_info.grid(row=11, column=0, sticky = tk.E + tk.W + tk.N + tk.S, padx=0, pady=20)

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
        #self.create_plot()
        
      

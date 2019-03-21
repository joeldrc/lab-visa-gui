#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import settings
from multi_thread import *

import threading

from tkinter import *
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

import time
from time import gmtime, strftime

from tkinter import filedialog
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


# plot list
plot_names = [[['S21 - delay', 'GHz', 'dB'],
               ['S21 - dB', 'GHz', 'dB'],
               ['S11 - SWR', 'GHz', 'mU'],
               ['S11 - SWR', 'GHz', 'mU'],
               ['S11 - TDR', 'ns', 'mU']],

              [['S11 - TDR', 'x', 'y'],
               ['S11 - TDR', 'x', 'y']]]

figure_names = [['Flanges'],
                ['Pick-Up']]

LARGE_FONT= ("Verdana", 12)


def screenTransp(root, transparency = True):
    root.overrideredirect(transparency)
    root.lift()
    root.wm_attributes("-topmost", transparency)
    root.wm_attributes("-disabled", transparency)
    root.wm_attributes("-transparentcolor", "blue")

def screenAdj(root):
    # Window in center of screen
    root.update_idletasks()
    width = root.winfo_width()
    frm_width = root.winfo_rootx() - root.winfo_x()
    win_width = width + 2 * frm_width
    height = root.winfo_height()
    titlebar_height = root.winfo_rooty() - root.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = root.winfo_screenwidth() // 2 - win_width // 2
    y = root.winfo_screenheight() // 2 - win_height // 2
    root.geometry('{}x{}+{}+{}'.format(width, height, x, y))
    root.deiconify()

def zoomPage(root):
    root.state('zoomed')

def progressBar(root):
    maximum = 100
    interval = 20
    progressbar = ttk.Progressbar(root, orient=tk.HORIZONTAL, mode="indeterminate", maximum=maximum)
    #progressbar.configure(mode="determinate", maximum=100, value=0)
    progressbar.configure(mode="indeterminate", maximum=100, value=0)
    progressbar.start(interval)
    progressbar.pack(fill=BOTH)

def destroyApp(root):
    root.destroy()
    exit()

def messageboxError(root, title, txt):
    messagebox.showerror(title, txt)
    print(title + ': ' + txt)


class Main(tk.Tk, threading.Thread):

    def __init__(self, *args, **kwargs):
        threading.Thread.__init__(self, *args, **kwargs)

        tk.Tk.__init__(self, *args, **kwargs)

        tk.Tk.iconbitmap(self, default='./images/icon.ico')
        tk.Tk.wm_title(self, "Sea of BTC Client")

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand = True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        #test
        self.test_container = container

        self.frames = {}
        for F in (LoadingPage, PageOne):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        #start thread
        self.start()

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

    def run(self):
        #display loader
        self.show_frame(LoadingPage)
        #test
        screenTransp(self, True)
        screenAdj(self)

        import time
        i = 0
        while i < 5:
            i += 1
            print(i)
            self.frames[LoadingPage].loading.config(text=str(i))
            time.sleep(1)

        #test     
        user_gui = User_gui(self.test_container, self)
        user_gui.grid(row=0, column=0, sticky="nsew")

        zoomPage(self)
        screenTransp(self, False)
    
        #self.show_frame(PageOne)


class LoadingPage(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.image = tk.PhotoImage(file='./images/startup.png')
        self.image_2 = tk.PhotoImage(file='./images/startup_2.png')

        label = tk.Label(self, bg='blue', image=self.image)
        label.pack()

        #progressBar(self)

        self.loading = tk.Label(self, bg='blue', justify=CENTER, compound=CENTER, text='Loading...', fg = "black", padx=0, pady=0, image=self.image_2)
        self.loading.pack()


class PageOne(tk.Frame):

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        label = ttk.Label(self, text="Page One!!!", font=LARGE_FONT)
        label.pack(pady=10,padx=10)

        button = ttk.Button(self, text="Back to Home", command=lambda: controller.show_frame(PageTwo))
        button.pack()


########################################################################
class Single_marker():
    def __init__(self, parent, canvas, plot, x, y, loop, marker_status = True):
        measure_pointer = 20

        # clean all the previous labels
        for widget in parent.winfo_children():
            widget.destroy()

        # create new label
        if marker_status == True:
            for i in range(loop):
                x_label_sci = str("%.6g" % x[i][measure_pointer])
                y_label_sci = str("%.6g" % y[i][measure_pointer])
                marker_x = plot[i].get_xlabel() + ' = ' + x_label_sci
                marker_y = plot[i].get_ylabel() + ' = ' + y_label_sci

                plot_label = marker_x + " / " + marker_y
                plot[i].plot(x[i][measure_pointer], y[i][measure_pointer], marker="o", ms=4, label = plot_label)
                legend = plot[i].legend(loc='upper left', ncol=2, mode="expand", shadow=True, fancybox=True)
                canvas.draw()

                plot_number = label_x = Label(parent, text=str(i))
                plot_number.grid(column = 0, row = i + 1, sticky=W)

                label_x = Label(parent, text=marker_x)
                label_x.grid(column = 1, row = i + 1, sticky=W)

                label_y = Label(parent, text=marker_y)
                label_y.grid(column = 2, row = i + 1, sticky=W)
        else:
            label = Label(parent, text= "")
            label.grid(column = 0, row = 1, sticky=W)


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

    def __init__(self, parent, controller):

        tk.Frame.__init__(self, parent)

        self.plot_reference = False
        self.plot_saveRef = False
        self.save_data = False
        self.plot_markers = False
        self.hostname_value = "TCPIP::CFO-MD-BQPVNA1::INSTR"

        self.create_widgets(controller)

    # when you close the program kill all the windows
    def close_program(self):
        self.destroy()
        exit()

    # when you press return
    def focus(self, event):
        self.start_test()

    # - - - - - - - - - - - - - - - - - - - - -
    # menuBar
    def show_info(self):
        info_txt = settings.__author__ + '\n' + "Version: " + settings.__version__
        messagebox.showinfo(title = 'About Me!', message = info_txt)

    def save_file(self):
        try:
            self.measure_thread.create_sheet()
        except:
            messagebox.showerror("Warning", "No data to save!")

    def open_file(self):
        #self.file_position = filedialog.askopenfile().name
        return None

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
                self.update_plot()

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
    def start_test(self):
        #check wich frame you have selected (return int)
        selected_frame_number = self.note.index("current")
        #print(selected_frame_number)
        self.instrument_connection(start_test = True, frame_number = selected_frame_number)
        self.measure_thread.file_name = self.serial_name_field.get() + '_' + self.serial_number_field.get() + '_' + self.details_field.get()
        self.measure_thread.time_value = strftime("%d %b %Y %H:%M:%S", gmtime())

    def instrument_connection(self, start_test = False, frame_number = 0):
        self.measure_thread = Measure_thread(self.hostname_field.get(), start_test, frame_number, len(plot_names[frame_number]))
        self.measure_thread.start()

        instrument_name = self.measure_thread.instrument_info
        self.labeled_frame_label.config(text = instrument_name)

    def checkbox(self, type):
        if type == 1:
            try:
                self.save_data = self.var.get()
            except:
                print("No class declared")
        elif type == 2:
            self.plot_reference = self.var1.get()
            if self.plot_reference == True:
                self.plot_saveRef = True
            try:
                self.update_plot()
            except Exception as e:
                print(e)
        elif type == 3:
            try:
                self.plot_markers = self.var2.get()
                self.update_plot()
            except Exception as e:
                print(e)

    def update_plot(self):
        # return wich test you have selected
        channel_number = len(self.measure_thread.measures)
        selected_frame_number = self.measure_thread.test_number

        xValue = []
        yValue = []

        try:
            for i in range(channel_number):
                x, y = self.measure_thread.measures[i]
                xValue.append(x)
                yValue.append(y)
                # clean plot line
                self.plot[selected_frame_number][i].cla()
                # set data on plot
                self.plot[selected_frame_number][i].plot(xValue[i], yValue[i])

            if self.plot_saveRef == True:
                self.xRef = xValue
                self.yRef = yValue
                self.plot_saveRef = False

            if self.plot_reference == True:
                for i in range(channel_number):
                    self.plot[selected_frame_number][i].plot(self.xRef[i], self.yRef[i])
        except Exception as e:
            print(e)

        # Set names on plot
        for i in range(len(plot_names[selected_frame_number])):
            self.plot[selected_frame_number][i].set_title(plot_names[selected_frame_number][i][0])
            self.plot[selected_frame_number][i].set_xlabel(plot_names[selected_frame_number][i][1])
            self.plot[selected_frame_number][i].set_ylabel(plot_names[selected_frame_number][i][2])
            #self.plot[selected_frame_number][i].grid()

        # autoadapt
        self.fig[selected_frame_number].tight_layout()
        # update plot
        self.canvas[selected_frame_number].draw()

        # markers
        Single_marker(self.others_frame, self.canvas[selected_frame_number], self.plot[selected_frame_number], xValue, yValue, len(plot_names[selected_frame_number]), self.plot_markers)

    def create_widgets(self, parent):
        # menuBar
        menuBar = tk.Menu(parent)

        fileMenu = Menu (menuBar , tearoff = 0)
        fileMenu.add_command(label = "New")
        fileMenu.add_command(label = "Open", command = self.open_file)
        fileMenu.add_command(label = "Save as", command = self.save_file)
        fileMenu.add_separator()
        fileMenu.add_command(label = "Exit", command = self.close_file)
        menuBar.add_cascade(label = "File", menu = fileMenu)

        fileMenu = Menu (menuBar , tearoff = 0)
        fileMenu.add_command(label = "Info", command = self.show_info)
        menuBar.add_cascade(label = "Help", menu = fileMenu)

        parent.config(menu = menuBar)

        # create some room around all the internal frames
        parent['padx'] = 5
        parent['pady'] = 5

        # - - - - - - - - - - - - - - - - - - - - -
        frame1 = ttk.Frame(self)
        frame1.grid(row=0, column=0, sticky = tk.E + tk.W + tk.N)

        frame2 = ttk.Frame(self)
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

        # create loading bar
        self.prog_bar = Progress_bar(frame_user, row=10, columnspan=2, sticky = E + W + N + S, padx=5, pady=10)

        # display check button
        self.var = IntVar(value= self.save_data)
        self.check_save_file = Checkbutton(frame_user, text = "Save data after measure", variable=self.var, command= lambda: self.checkbox(1))
        self.check_save_file.grid(row=20, column=0, sticky=W, padx=0, pady=5)

        # display button
        submit = Button(frame_user, text='START MEASURE', fg='Black', command= self.start_test)
        submit.grid(row=20, column=1, sticky = E, padx=20, pady = 5)

        # display time
        self.clock = Label(frame_user)
        self.clock.grid(row=30, column=0, sticky = tk.W + tk.N + tk.S, padx=5, pady=5)

        # - - - - - - - - - - - - - - - - - - - - -
        # details_frame
        details_frame = ttk.LabelFrame(frame2, text="PLOT OPTIONS")
        details_frame.grid(row=3, column=0, sticky = tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        self.var1 = IntVar(value= self.plot_reference)
        self.check_save_ref = Checkbutton(details_frame, text = "Save reference", variable=self.var1, command= lambda: self.checkbox(2))
        self.check_save_ref.grid(row=1, column=0, sticky=W, padx=0, pady=5)

        self.var2 = IntVar(value= self.plot_markers)
        self.markers_status = Checkbutton(details_frame, text = "Markers", variable=self.var2, command= lambda: self.checkbox(3))
        self.markers_status.grid(row=2, column=0, sticky=W, padx=0, pady=5)

        # others_frame
        self.others_frame = ttk.LabelFrame(frame2, text="OTHERS")
        self.others_frame.grid(row=4, column=0, sticky = tk.E + tk.W + tk.N + tk.S, padx=5, pady=5)

        # - - - - - - - - - - - - - - - - - - - - -
        # Notebook
        self.note = ttk.Notebook(frame1)
        self.note.pack(padx=5, pady=5)

        number_of_plots = len(plot_names)

        # initialize tab
        self.tab = [[] for i in range(number_of_plots)]
        for i in range(number_of_plots):
            self.tab[i] = ttk.Frame(self.note)
            self.note.add(self.tab[i], text = figure_names[i])

        # - - - - - - - - - - - - - - - - - - - - -
        # plot setup
        plt.style.use('seaborn-whitegrid')

        self.plot = [[] for i in range(number_of_plots)]
        self.fig = [[] for i in range(number_of_plots)]
        self.canvas = [[] for i in range(number_of_plots)]
        self.toolbar = [[] for i in range(number_of_plots)]

        # initialize fig
        for i in range(number_of_plots):
            self.fig[i] =Figure(figsize=(12,7))

        # Figures
        for index in range(number_of_plots):
            subplot_number = len(plot_names[index])
            for i in range(subplot_number):
                # auto adapt plot number
                subplot_columns = (subplot_number // 3) + (subplot_number % 3)
                subplot_rows = subplot_number // 2
                subplot = self.fig[index].add_subplot(subplot_rows, subplot_columns, i + 1)
                self.plot[index].append(subplot)

        # auto adj
        for i in range(number_of_plots):
            self.fig[i].tight_layout()

        # Canvas & # toolbar
        for i in range(number_of_plots):
            self.canvas[i] = FigureCanvasTkAgg(self.fig[i], master=self.tab[i])
            self.canvas[i].get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

            self.toolbar[i] = NavigationToolbar2Tk(self.canvas[i], self.tab[i])
            self.toolbar[i].update()
            self.canvas[i]._tkcanvas.pack(side=tk.TOP, fill=tk.BOTH, expand=1)

        # - - - - - - - - - - - - - - - - - - - - -
        # event
        self.update_screen()

        # whenever the enter key is pressed then call the focus1 function
        self.bind('<Return>', self.focus)


if __name__ == '__main__':
    main = Main()
    #main.geometry("1280x720")
    main.mainloop()

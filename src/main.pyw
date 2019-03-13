#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import settings
from auto_install import*

import threading
from tkinter import *
import tkinter as tk


class Main(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

        self.root = tk.Tk()
        #self.root.attributes("-fullscreen", False)
        self.root.title(settings.__logo__ + " - " + settings.__title__ + " - " + settings.__version__)
        #self.root.iconify()
        self.root.withdraw()

        try:
            self.root.iconbitmap('./data/icon.ico')
        except:
            print("No icon file")

        # start run()
        self.start()

        self.root.mainloop()

    def start_gui(self, parent):
        from gui_interface import User_gui
        parent.deiconify()
        User_gui(parent)

    def run(self):
        Auto_install(Toplevel(self.root))
        self.start_gui(self.root)



if __name__ == '__main__':
    # multi thread main
    Main()

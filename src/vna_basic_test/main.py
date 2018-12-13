#!/usr/bin/env python
# -*- coding: utf-8 -*-
#*******************************************************************************
# title          : main.py
# author         : Joel Daricou <joel.daricou@cern.ch>
# date           : 12/2018
# version        : 1.0
# usage          : main.py
# notes          :
# python_version : 3.7  
#*******************************************************************************

import tkinter as tk
from tkinter import ttk

from gui_interface import User_gui


root = tk.Tk()
try:
    root.iconbitmap('icon.ico')
except:
    print("No icon file")
program = User_gui(root)
root.mainloop()

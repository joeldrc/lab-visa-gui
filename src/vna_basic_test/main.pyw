#!/usr/bin/env python
# -*- coding: utf-8 -*-

import tkinter as tk
from tkinter import ttk

from gui_interface import User_gui


root = tk.Tk()
#root.attributes("-fullscreen", False)
try:
    root.iconbitmap('./data/icon.ico')
except:
    print("No icon file")
program = User_gui(root)
root.mainloop()

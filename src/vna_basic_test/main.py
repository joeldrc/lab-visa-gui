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

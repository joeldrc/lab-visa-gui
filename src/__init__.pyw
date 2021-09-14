#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import platform
python_version, system_version = platform.architecture()
import tkinter
from PIL import Image, ImageTk, ImageSequence

import threading

class App():
    def __init__(self, parent):

        self.parent = parent
        self.canvas = tkinter.Canvas(parent, width=400, height=400)
        self.canvas.pack()

        self.sequence = [ImageTk.PhotoImage(img)for img in ImageSequence.Iterator(Image.open(r'images\loading.gif'))]
        self.image = self.canvas.create_image(200,200, image=self.sequence[0])

        self.parent.overrideredirect(True)
        self.parent.eval('tk::PlaceWindow . center')

        self.animate(1)

    def animate(self, counter):
        self.canvas.itemconfig(self.image, image=self.sequence[counter])
        self.parent.after(20, lambda: self.animate((counter+1) % len(self.sequence)))


import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def installPakages():
    install("numpy")
    install("visa")
    install("pyvisa")
    install("PyQt5")
    install("matplotlib")
    root.destroy()


root = tkinter.Tk()
app = App(root)
thread = threading.Thread(target=installPakages)
thread.start()
root.mainloop()

if (python_version == '64bit'):
    print(python_version)
    import gui_core
else:
    print('Error, the code cannot be executed in this %s python version.' % python_version)
    print('Please install the 64bit python version.')

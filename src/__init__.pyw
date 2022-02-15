#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import subprocess
import sys

import settings
import platform
python_version, system_version = platform.architecture()
import tkinter
from PIL import Image, ImageTk, ImageSequence

import threading
import time


class App():
    def __init__(self, parent):

        self.parent = parent
        self.parent.configure(bg='White')

        self.canvas = tkinter.Canvas(parent, width=300, height=200, bd=-2)
        self.canvas.pack()

        self.labelIntro = tkinter.Label(self.parent, text = settings.__title__, bg='White', font='Calibri 20 bold')
        self.labelIntro.pack()

        self.details = settings.__author__ + ' - ' + settings.__version__
        self.label = tkinter.Label(self.parent, text = self.details, bg='White')
        self.label.pack()

        self.sequence = [ImageTk.PhotoImage(img)for img in ImageSequence.Iterator(Image.open(r'images\loading.gif'))]
        self.image = self.canvas.create_image(150,100, image=self.sequence[0])

        self.parent.overrideredirect(True)
        self.parent.eval('tk::PlaceWindow . center')

        self.animate(1)


    def animate(self, counter):
        self.canvas.itemconfig(self.image, image=self.sequence[counter])
        self.parent.after(10, lambda: self.animate((counter+1) % len(self.sequence)))


def bootApp():
    if (python_version == '64bit'):
        print(python_version)
        import gui_core
    else:
        print('Error, the code cannot be executed in this %s python version.' % python_version)
        print('Please install the 64bit python version.')


def main():
    time.sleep(4)
    
    mainThread = threading.Thread(target=bootApp)
    mainThread.start()

    cnt = 0
    while((settings.SYS_READY == False) or (cnt >= 30)):
        time.sleep(1)
    root.destroy()


root = tkinter.Tk()
app = App(root)
thread = threading.Thread(target=main)
thread.start()

root.mainloop()

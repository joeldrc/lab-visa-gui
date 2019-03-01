#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import settings
from tkinter import *
import tkinter as tk
import threading
import subprocess
import sys
print(sys.executable)


class Install_and_run(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent

    def pip_install(self, package):
        import importlib
        try:
            importlib.import_module(package)
        except ImportError:
            from pip._internal import main
            main(['install', package])
            print('Installed: ' + package)
        """
        try:
            subprocess.call(["pip", "install", package, "--user"], shell=True)  #!Security! Better if shell=False
            print('\n Installed: ' + package)
        except:
            print("Error")
        """

    def start_loader(self):
        from loading_window import Loading_window
        self.loader_app = Toplevel(self.parent)
        Loading_window(self.loader_app)

    def destroy_loader(self):
        self.loader_app.destroy()

    def start_gui(self):
        from gui_interface import User_gui
        self.parent.deiconify()
        self.main_app = User_gui(self.parent)

    def run(self):
        #Run loading app
        self.start_loader()

        #pip_install all the packages
        self.pip_install('matplotlib')
        self.pip_install('openpyxl')
        self.pip_install('pyvisa')
        self.pip_install('pyvisa-py')
        self.pip_install('numpy')

        #Run Main App
        self.start_gui()

        self.destroy_loader()


def main():
    root = tk.Tk()
    #root.attributes("-fullscreen", False)
    root.title(settings.__logo__ + " - " + settings.__title__ + " - " + settings.__version__)
    #root.iconify()
    root.withdraw()

    try:
        root.iconbitmap('./data/icon.ico')
    except:
        print("No icon file")

    #Install all librairies and run program
    lib_installer = Install_and_run(root)
    lib_installer.start()

    root.mainloop()


if __name__ == '__main__':
    main()

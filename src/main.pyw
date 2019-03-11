#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import settings
from tkinter import *
import tkinter as tk
import threading
import subprocess
import sys
print(sys.executable)


class AnimatedGif(object):
    """ Animated GIF Image Container. """
    def __init__(self, image_file_path):
        # Read in all the frames of a multi-frame gif image.
        self._frames = []
        frame_num = 0  # Number of next frame to read.
        while True:
            try:
                frame = PhotoImage(file=image_file_path,
                                   format="gif -index {}".format(frame_num))
            except TclError:
                break
            self._frames.append(frame)
            frame_num += 1

    def __len__(self):
        return len(self._frames)

    def __getitem__(self, frame_num):
        return self._frames[frame_num]


class Loading_window():
    def __init__(self, master):
        self.master = master
        self.master.title(settings.__logo__ + " - Installing libraries...")
        self.master.geometry('360x125')

        # Window in center of screen
        self.master.update_idletasks()
        width = self.master.winfo_width()
        frm_width = self.master.winfo_rootx() - self.master.winfo_x()
        win_width = width + 2 * frm_width
        height = self.master.winfo_height()
        titlebar_height = self.master.winfo_rooty() - self.master.winfo_y()
        win_height = height + titlebar_height + frm_width
        x = self.master.winfo_screenwidth() // 2 - win_width // 2
        y = self.master.winfo_screenheight() // 2 - win_height // 2
        self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        self.master.deiconify()

        try:
            self.master.iconbitmap('./data/icon.ico')
        except:
            print("No icon file")

        self.frame = Frame(self.master)

        try:
            self.ani_img = AnimatedGif("data/loading_bar.gif")
            # Display first frame initially.
            self.animation = Label(self.frame, height = 100, image=self.ani_img[0])
            self.animation.pack()
            self.enable_animation()
        except:
            print("No gif file")

        self.frame.pack()

        # display text
        self.startLog = Text(self.frame, takefocus=0)
        self.startLog.pack()

    def update_label_image(self, label, ani_img, ms_delay, frame_num):
        label.configure(image=self.ani_img[frame_num])
        frame_num = (frame_num+1) % len(self.ani_img)
        self.frame.after(ms_delay, self.update_label_image, label,
                         self.ani_img, ms_delay, frame_num)

    def enable_animation(self):
        ms_delay = 1000 // len(self.ani_img)    # Show all frames in 1000 ms.
        self.frame.after(ms_delay, self.update_label_image, self.animation,
                         self.ani_img, ms_delay, 0)


class Install_and_run(threading.Thread):
    def __init__(self, parent):
        threading.Thread.__init__(self)
        self.parent = parent

    def pip_install(self, package):
        import importlib

        try:
            importlib.import_module(package)
            txt = str('Loading pakages: ' + package)
        except ImportError:
            from pip._internal import main
            main(['install', package])
            print('Installed: ' + package)
            txt = str('Installing pakages: ' + package)

        self.loadingWindow.startLog.insert(0.0, txt + "\n")

        """
        try:
            subprocess.call(["pip", "install", package, "--user"], shell=True)  #!Security! Better if shell=False
            print('\n Installed: ' + package)
        except:
            print("Error")
        """

    def start_loader(self):
        self.loader_app = Toplevel(self.parent)
        self.loadingWindow = Loading_window(self.loader_app)
        self.loadingWindow.startLog.insert(0.0, "Start running..." + "\n")

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

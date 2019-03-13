#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import settings

import threading
import os, glob, importlib

from tkinter import *
import tkinter as tk


class Auto_install(threading.Thread):
    def __init__(self, master):
        threading.Thread.__init__(self)
        self.master = master

        self.edit_loader()
    
        # start to check modules    
        self.check_modules()

    def edit_loader(self):     
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
        
    def pip_install(self, package):
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

    def check_modules(self):
        start = False
        while (start == False):
            try:
                # check modules inside the folder
                modules = {}
                for path in glob.glob('./[!_]*.py'):
                    name, ext = os.path.splitext(os.path.basename(path))
                    modules[name] = importlib.import_module(name, path)

                for i in modules:
                    print(modules[i])
                    
                start = True
                
            except ImportError as moduleError:
                # cut "No module named" and print the module name
                missed_module = str(moduleError).split("'")[1]

                # run autoinstaller           
                pip_install(missed_module)
                
            except Exception as e:
                print(e)
                
                # continue to modify
                start = True

        # destroy loading window
        self.master.destroy()


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

    

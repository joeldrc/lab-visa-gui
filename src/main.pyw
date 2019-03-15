#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import settings
from auto_install import*


def main():
    #run auto installer
    installer = Auto_install()
    #installer.mainloop()

    # start gui
    from gui_interface import User_gui
    gui = User_gui()
    #gui.mainloop()


if __name__ == '__main__':
    main()

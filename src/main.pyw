#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import settings
from auto_install import*


def main():
    #run auto installer
    Auto_install()

    # start gui
    from gui_interface import User_gui
    User_gui()


if __name__ == '__main__':
    main()

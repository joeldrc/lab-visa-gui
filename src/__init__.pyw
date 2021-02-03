#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import platform
python_version, system_version = platform.architecture()

if (python_version == '64bit'):
    print(python_version)
    from gui_core import *
else:
    print('Error, the code cannot be executed in this %s python version.' % python_version)
    print('Please install the 64bit python version.')

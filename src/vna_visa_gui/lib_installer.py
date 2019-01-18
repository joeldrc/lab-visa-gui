#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
print(sys.executable)

import subprocess

def pip_install(package):
    print('\n Installing: ' + package)
    subprocess.call(["pip", "install", package, "--user"], shell=True)  #!Security! Better if shell=False

#pip_install all the packages
pip_install('matplotlib')
pip_install('openpyxl')
pip_install('pyvisa')
pip_install('pyvisa-py')
pip_install('numpy')

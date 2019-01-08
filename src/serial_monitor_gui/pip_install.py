#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
print(sys.executable)

import subprocess
def pip_install(package):    
    subprocess.call(["pip", "install", package, "--user"])

#pip_install all the packages
pip_install('matplotlib')
pip_install('serial')
pip_install('pyserial')
pip_install('openpyxl')
pip_install('pyvisa')
pip_install('pyvisa-py')
pip_install('numpy')

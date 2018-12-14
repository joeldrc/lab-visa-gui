#!/bin/bash

pip install pyvisa --user
pip install PyVISA-py --user
pip install matplotlib --user
pip install openpyxl --user

"%~dp0RUN_script.lnk"

exit 0
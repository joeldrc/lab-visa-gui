#!/bin/bash

pip install serial --user
pip install pyserial --user
pip install matplotlib --user
pip install openpyxl --user

"%~dp0RUN_script.lnk"

exit 0
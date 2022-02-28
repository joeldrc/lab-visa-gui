#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import platform
python_version, system_version = platform.architecture()

from loading import*
from gui_core import*


def check_version():
    if (python_version == '64bit'):
        print(python_version)
        return True
    else:
        print('Error, the code cannot be executed in this %s python version.'
        % python_version)
        print('Please install the 64bit python version.')
        return False


if __name__ == "__main__":
    check_version()

    app = QtWidgets.QApplication(sys.argv)
    loading = LoadingGui()
    sys.exit(app.exec_())

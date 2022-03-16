#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Joel Daricou 03/2022

import sys
from loading import *
from gui_core import *

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # create the main GUI
    gui = GuiCore()
    
    # create the loading page
    loading = LoadingGui()
    sys.exit(app.exec_())

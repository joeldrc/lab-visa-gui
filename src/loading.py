#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt

class LoadingGui:
    def __init__(self):
        self.MainWindow = QtWidgets.QMainWindow()
        self.MainWindow.setWindowTitle('Loading')

        # Create window
        self.MainWindow.resize(600, 600)
        self.MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.centralwidget = QtWidgets.QWidget(self.MainWindow)

        # Label Create
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.MainWindow.setCentralWidget(self.centralwidget)

        # Loading the GIF
        self.movie = QMovie("images/loading.gif")
        self.label.setMovie(self.movie)
        self.startAnimation()

        # Show the window
        self.MainWindow.show()

    # Start Animation
    def startAnimation(self):
        self.movie.start()

        # auto close app
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.stopAnimation)
        self.timer.start(5000)

    # Stop Animation(According to need)
    def stopAnimation(self):
        self.movie.stop()
        self.MainWindow.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    loading = LoadingGui()
    sys.exit(app.exec_())

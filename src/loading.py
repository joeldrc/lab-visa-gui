#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt

class LoadingGui:
    def __init__(self):
        self.MainWindow = QtWidgets.QMainWindow()

        # Create window
        self.MainWindow.resize(300, 300)
        self.MainWindow.setWindowTitle('Loading')
        self.MainWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.MainWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        centralwidget = QtWidgets.QWidget(self.MainWindow)

        # Label Create
        label1 = QLabel(centralwidget)
        label2 = QLabel(self.MainWindow)
        label2.setText("Loading...")
        font = label2.font()
        font.setPointSize(30)
        label2.setFont(font)
        label2.adjustSize()
        label2.move(70, 0)

        self.MainWindow.setCentralWidget(centralwidget)

        # Loading the GIF
        self.movie = QMovie("images/loading.gif")
        label1.setMovie(self.movie)
        self.startAnimation()

        # Show the window
        self.MainWindow.move(QDesktopWidget().availableGeometry().center() - self.MainWindow.frameGeometry().center())
        self.MainWindow.show()

    # Start Animation
    def startAnimation(self):
        self.movie.start()

        # auto close app
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.stopAnimation)
        self.timer.start(5000)

    # Stop Animation
    def stopAnimation(self):
        self.movie.stop()
        self.MainWindow.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    loading = LoadingGui()
    sys.exit(app.exec_())

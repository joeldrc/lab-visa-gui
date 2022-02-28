import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt
  
  
class Loading(object): 
    def main(self, FrontWindow):
        self.FrontWindow = FrontWindow
        FrontWindow.resize(600, 600)
        FrontWindow.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        FrontWindow.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.centralwidget = QtWidgets.QWidget(FrontWindow)
  
        # Label Create
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        FrontWindow.setCentralWidget(self.centralwidget)
  
        # Loading the GIF
        self.movie = QMovie("images/loading.gif")
        self.label.setMovie(self.movie) 
        self.startAnimation()
  
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
        self.FrontWindow.close()
  

if __name__ == "__main__":  
    app = QtWidgets.QApplication(sys.argv)
    window = QtWidgets.QMainWindow()
    loading = Loading()
    loading.main(window)
    window.show()
    sys.exit(app.exec_())

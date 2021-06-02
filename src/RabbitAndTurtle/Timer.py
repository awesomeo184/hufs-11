# importing libraries
import os

from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import sys
from config import setup

PATH = setup.UI_PATH
start_form = uic.loadUiType(os.path.join(PATH, "StartWindow.ui"))[0]


class Window(QMainWindow, start_form):

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.btn_start.clicked.connect(self.popUp)

    def popUp(self):
        box = QMessageBox()
        box.setWindowTitle("eye dry warning")
        box.setText("안구 건조 위험")
        box.resize(300, 200)
        box.show()
        box.exec_()


if __name__ == "__main__":

    # create pyqt5 app
    App = QApplication(sys.argv)
    # create the instance of our Window
    window = Window()
    window.show()
    App.exec_()


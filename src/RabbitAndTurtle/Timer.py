# importing libraries
import os
import sys

import cv2
from PyQt5.QtWidgets import *
from PyQt5 import QtCore, QtGui, uic
from PyQt5.QtGui import *
from PyQt5.QtCore import *

from config import setup
from EyeTracker import EyeTracker
from signals import DriedEye, ImageThread

PATH = setup.UI_PATH
start_form = uic.loadUiType(os.path.join(PATH, "StartWindow.ui"))[0]
exec_form = uic.loadUiType(os.path.join(PATH, "ExecWindow.ui"))[0]
status_form = uic.loadUiType(os.path.join(PATH, "StatusWindow.ui"))[0]


class StartWindow(QMainWindow, start_form):
    def __init__(self):
        super(StartWindow, self).__init__()
        self.setupUi(self)

        self.btn_start.clicked.connect(self.goto_exec_window)

    def goto_exec_window(self):
        execWindow = ExecWindow()
        widgets.addWidget(execWindow)
        widgets.setCurrentWidget(execWindow)


class ExecWindow(QMainWindow, exec_form):

    def __init__(self):
        super(ExecWindow, self).__init__()
        self.setupUi(self)

        # * utility
        self.eye_warning_signal = DriedEye()
        self.eyeTracker = EyeTracker()
        self.thread = ImageThread(self.eyeTracker, self.eye_warning_signal)

        # * click signal
        self.btn_status.clicked.connect(self.goto_status_window)

        # * custom signal
        self.eye_warning_signal.dried.connect(self.show_eye_warning_message)
        self.thread.stream.connect(self.set_image)

        self.thread.start()

    def goto_status_window(self):
        statusWindow = StatusWindow(0, 0, self.eyeTracker.get_warning_count())
        widgets.addWidget(statusWindow)
        widgets.setCurrentWidget(statusWindow)

    @pyqtSlot(int)
    def show_eye_warning_message(self, warning_count):
        print("Warning count = ", warning_count)
        box = QMessageBox()
        box.setWindowTitle("eye dry warning")
        box.setText("안구 건조 위험")
        box.resize(300, 200)
        box.exec_()

    @pyqtSlot(QImage)
    def set_image(self, image):
        self.label_webcam.setPixmap(QPixmap.fromImage(image))


class StatusWindow(QMainWindow, status_form):
    def __init__(self, exec_time, turtle_neck_warning_count, eye_dried_warning_count):
        super(StatusWindow, self).__init__()
        self.setupUi(self)
        self.exec_time = exec_time
        self.turtle_neck_warning_count = turtle_neck_warning_count
        self.eye_dried_warning_count = eye_dried_warning_count


if __name__ == "__main__":
    App = QApplication(sys.argv)

    widgets = QStackedWidget()
    startWindow = StartWindow()

    widgets.addWidget(startWindow)

    widgets.setMinimumWidth(800)
    widgets.setMinimumHeight(600)
    widgets.show()
    App.exec_()

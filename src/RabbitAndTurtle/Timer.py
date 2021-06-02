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

    class DriedEye(QObject):
        dried = pyqtSignal(int)

        def __init__(self):
            super().__init__()

        def warn(self, warning_count):
            self.dried.emit(warning_count)

    class ImageThread(QThread):
        def __init__(self, eyeTracker, eye_warning_signal):
            super().__init__()
            self.eyeTracker = eyeTracker
            self.eye_warning_signal = eye_warning_signal

        stream = pyqtSignal(QImage)

        def run(self):
            cap = cv2.VideoCapture(0)
            count = self.eyeTracker.get_warning_count()
            while True:
                ret, frame = cap.read()
                if ret:
                    frame = self.eyeTracker.is_blinked(frame)

                    # * warning count가 1 증가하면 시그널 보냄
                    if self.eyeTracker.get_warning_count() > count:
                        self.eye_warning_signal.warn(self.eyeTracker.get_warning_count())
                        count = self.eyeTracker.get_warning_count()

                    rgbImage = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    h, w, ch = rgbImage.shape
                    bytesPerLine = ch * w
                    convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                    p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                    self.stream.emit(p)

    def __init__(self):
        super(ExecWindow, self).__init__()
        self.setupUi(self)

        # * utility
        self.eye_warning_signal = self.DriedEye()
        self.eyeTracker = EyeTracker()
        self.thread = self.ImageThread(self.eyeTracker, self.eye_warning_signal)

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

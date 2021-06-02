import cv2
from PyQt5.QtCore import QObject, pyqtSignal, Qt, QThread
from PyQt5.QtGui import QImage


class DriedEye(QObject):
    dried = pyqtSignal(int)

    def __init__(self):
        super().__init__()

    def warn(self, warning_count):
        self.dried.emit(warning_count)


class ImageThread(QThread):
    def __init__(self, eyeTracker, eye_warning_signal):
        super().__init__()
        self.is_interrupted = False
        self.eyeTracker = eyeTracker
        self.eye_warning_signal = eye_warning_signal

    stream = pyqtSignal(QImage)

    def run(self):
        cap = cv2.VideoCapture(0)
        count = self.eyeTracker.get_warning_count()
        while not self.is_interrupted:
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

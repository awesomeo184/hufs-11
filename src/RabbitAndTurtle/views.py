import os
import sys
import time

import cv2

from PyQt5.QtCore import QThread, pyqtSignal, Qt, pyqtSlot
from PyQt5.QtGui import QImage, QPixmap

from config import setup
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *

from src.RabbitAndTurtle.EyeTracker import EyeTracker
from src.RabbitAndTurtle.NeckTracker import NeckTracker

PATH = setup.UI_PATH

start_form = uic.loadUiType(os.path.join(PATH, "StartWindow.ui"))[0]
exec_form = uic.loadUiType(os.path.join(PATH, "ExecWindow.ui"))[0]
setting_form = uic.loadUiType(os.path.join(PATH, "SettingWindow.ui"))[0]
status_form = uic.loadUiType(os.path.join(PATH, "StatusWindow.ui"))[0]
alarm_form = uic.loadUiType(os.path.join(PATH, "AlarmWindow.ui"))[0]

eyeTracker = None

# TODO: 예외 처리, 팝업창, 모듈 연결, 디자인

class StartWindow(QMainWindow, start_form):
    '''
    시작창

    오브젝트 목록
    - 타이틀: label_title
    - 시작버튼: btn_start
    - 설정버튼: btn_setting
    '''

    def __init__(self):
        super(StartWindow, self).__init__()
        self.setupUi(self)
        self.setting_window = SettingWindow()

        self.btn_start.clicked.connect(self.activate_exec_window)
        self.btn_setting.clicked.connect(self.setting_window.show)
        self.show()

    def activate_exec_window(self):
        self.hide()
        self.exec_window = ExecWindow(self)
        self.exec_window.show()



class ImageThread(QThread):
    def __init__(self, dried_eye_signal):
        super().__init__()
        self.is_interrupted = False
        self.dried_eye_signal = dried_eye_signal

    changePixmap = pyqtSignal(QImage)

    def run(self):
        global eyeTracker
        cap = cv2.VideoCapture(0)
        eyeTracker = EyeTracker()
        neckTracker = NeckTracker()

        count = eyeTracker.dried_count

        while not self.is_interrupted:
            ret, frame = cap.read()

            if ret:
                rgbImage = eyeTracker.is_blinked(frame)
                neckTracker.is_good_posture(rgbImage)

                if count != eyeTracker.dried_count:
                    self.dried_eye_signal.dry()
                    count = eyeTracker.dried_count

                h, w, ch = rgbImage.shape
                bytesPerLine = ch * w
                convertToQtFormat = QImage(rgbImage.data, w, h, bytesPerLine, QImage.Format_RGB888)
                p = convertToQtFormat.scaled(640, 480, Qt.KeepAspectRatio)
                self.changePixmap.emit(p)


class ExecWindow(QMainWindow, exec_form):
    '''
    실행창

    오브젝트 목록
    - 카메라 온/오프 버튼: btn_camera
    - 웹캠 화면: widget_webcam
    - 종료 버튼(통계 창으로 이동): btn_status
    - 설정 버튼: btn_setting
    '''

    @pyqtSlot(QImage)
    def __init__(self, parent):
        super(ExecWindow, self).__init__(parent)
        self.setupUi(self)
        self.setting_window = parent.setting_window
        self.dried_eye_signal = DriedEye()

        self.btn_status.clicked.connect(self.terminate)
        self.btn_setting.clicked.connect(self.setting_window.show)
        self.dried_eye_signal.dried.connect(self.show_eye_dried_pop_up_message)

        self.thread = ImageThread(self.dried_eye_signal)
        self.thread.changePixmap.connect(self.setImage)
        self.thread.start()

        self.count = 0
        self.flag = True

        # setting text to the label
        self.label_time.setText(str(self.count))

        # creating a timer object
        timer = QTimer(self)

        # adding action to timer
        timer.timeout.connect(self.showTime)

        # update the timer every tenth second
        timer.start(100)

    def show_eye_dried_pop_up_message(self):
        box = QMessageBox()
        box.setWindowTitle("eye dry warning")
        box.setText("안구 건조 위험")
        box.resize(300, 200)
        box.exec_()


    def showTime(self):
        # checking if flag is true
        if self.flag:
            # incrementing the counter
            self.count += 1

        # getting text from count
        strftime = time.strftime('%H:%M:%S', time.gmtime(self.count))
        text = str(strftime)

        # showing text
        self.label_time.setText(text)

    def setImage(self, image):
        self.label_webcam.setPixmap(QPixmap.fromImage(image))

    def terminate(self):
        self.thread.is_interrupted = True
        self.hide()
        self.status_window = StatusWindow(self)
        self.status_window.show()


# 안구건조 시그널
class DriedEye(QObject):

    dried = pyqtSignal()

    def __init__(self):
        super().__init__()

    def dry(self):
        self.dried.emit()

class SettingWindow(QMainWindow, setting_form):
    '''
    오브젝트 목록
    - 거북목 알림 : check_box_turtle_neck
    - 안구 건조 알림: check_box_eye_track
    - 소리 알림: check_box_sound
    - 방해 금지 모드: check_box_no_disturb
    - 완료 버튼: btn_save
    '''

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.check_box_turtle_neck.setChecked(True)
        self.check_box_eye_track.setChecked(True)
        self.check_box_sound.setChecked(True)

        self.btn_save.clicked.connect(self.save_states)

    def save_states(self):
        # TODO: 설정에 맞춰 기능 활성화
        if self.check_box_turtle_neck.isChecked():
            pass
        if self.check_box_eye_track.isChecked():
            pass
        if self.check_box_sound.isChecked():
            pass
        if self.check_box_no_disturb.isChecked():
            pass
        self.close()


class StatusWindow(QMainWindow, status_form):
    '''
    오브젝트 목록
    - 사용시간 : label_time_count
    - 거북목 경고 횟수: label_turtle_count
    - 눈 깜빡임 경고 횟수: label_eye_count
    - 확인 버튼: btn_exit
    '''

    def __init__(self, parent):
        super(StatusWindow, self).__init__(parent)
        self.setupUi(self)
        self.get_status()
        self.btn_exit.clicked.connect(self.exit)

    def get_status(self):
        # TODO: 통계 모듈 연결
        self.label_time_count.setText("08:11:11")
        self.label_turtle_count.setText("14")
        self.label_eye_count.setText("5")

    def exit(self):
        self.close()


class AlarmWindow(QMainWindow, alarm_form):
    '''
    오브젝트 목록
    - 눈 깜빡임 횟수: label_blink_count
    - 확인 버튼: btn_exit
    '''

    def __init__(self, parent):
        super(AlarmWindow, self).__init__(parent)
        self.setupUi(self)
        self.get_status()
        self.btn_exit.clicked.connect(self.exit)

    def get_status(self):
        # TODO: 깜빡임 횟수 연결
        self.label_blink_count("8")

    def exit(self):
        self.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = StartWindow()
    app.exec_()

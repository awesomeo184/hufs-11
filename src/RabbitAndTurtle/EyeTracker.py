import os
import threading

import cv2, dlib
import numpy as np
from imutils import face_utils
from keras.models import load_model
from config import setup


class EyeTracker:
    def __init__(self):

        self.__IMG_SIZE = (34, 26)
        self.__COUNT = 0
        self.__STATUS = True
        self.__detector = dlib.get_frontal_face_detector()
        self.__predictor = dlib.shape_predictor(os.path.join(setup.MODEL_PATH, 'shape_predictor_68_face_landmarks.dat'))
        self.__model = load_model(os.path.join(setup.MODEL_PATH, 'eye_blink_detector_model.h5'))
        self.__model.summary()

        self.dried_count = 0
        self.__MINUTE_COUNT = 0
        self.__start_timer()


    def __start_timer(self):
        timer = threading.Timer(6, self.__start_timer)
        if not self.__MINUTE_COUNT == 0:
            if self.__is_eye_dried():
                # popup warning message
                self.dried_count += 1
            self.__COUNT = 0
        self.__MINUTE_COUNT += 1
        timer.start()

    def is_blinked(self, img_ori):
        faces, gray, img = self.__get_frontal_faces(img_ori)

        for face in faces:
            shapes = self.__predictor(gray, face)
            shapes = face_utils.shape_to_np(shapes)
            eye_img_l, eye_rect_l = self.__preprocess_left_eye_img(gray, shapes)
            eye_img_r, eye_rect_r = self.__preprocess_right_eye_img(gray, shapes)
            eye_input_l, eye_input_r = self.__reshape_eye_img(eye_img_l, eye_img_r)

            pred_l, pred_r = self.__get_prediction(eye_input_l, eye_input_r)

            if (pred_r <= 0.1 or pred_l <= 0.1) and self.__STATUS:
                self.__COUNT += 1
                self.__STATUS = False

            if pred_r > 0.1 and pred_l > 0.1:
                self.__STATUS = True

            # visualize, only in dev mode
            self.__put_text(eye_rect_l, eye_rect_r, img, pred_l, pred_r)

        return img

    def __put_text(self, eye_rect_l, eye_rect_r, img, pred_l, pred_r):
        state_l = 'opened' if pred_l > 0.1 else 'closed'
        state_r = 'opened' if pred_r > 0.1 else 'closed'
        cv2.rectangle(img, pt1=tuple(eye_rect_l[0:2]), pt2=tuple(eye_rect_l[2:4]), color=(255, 0, 0), thickness=2)
        cv2.rectangle(img, pt1=tuple(eye_rect_r[0:2]), pt2=tuple(eye_rect_r[2:4]), color=(0, 255, 0), thickness=2)
        cv2.putText(img, state_l, (tuple(eye_rect_l[0:2])), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
        cv2.putText(img, state_r, tuple(eye_rect_r[0:2]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(img, "Blink Count = " + str(self.__COUNT), (70, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    def __reshape_eye_img(self, eye_img_l, eye_img_r):
        eye_input_l = eye_img_l.copy().reshape((1, self.__IMG_SIZE[1], self.__IMG_SIZE[0], 1)).astype(np.float32) / 255.
        eye_input_r = eye_img_r.copy().reshape((1, self.__IMG_SIZE[1], self.__IMG_SIZE[0], 1)).astype(np.float32) / 255.
        return eye_input_l, eye_input_r

    def __preprocess_right_eye_img(self, gray, shapes):
        eye_img_r, eye_rect_r = self.__crop_eye(gray, eye_points=shapes[42:48])
        eye_img_r = cv2.resize(eye_img_r, dsize=self.__IMG_SIZE)
        eye_img_r = cv2.flip(eye_img_r, flipCode=1)
        return eye_img_r, eye_rect_r

    def __preprocess_left_eye_img(self, gray, shapes):
        eye_img_l, eye_rect_l = self.__crop_eye(gray, eye_points=shapes[36:42])
        eye_img_l = cv2.resize(eye_img_l, dsize=self.__IMG_SIZE)
        return eye_img_l, eye_rect_l

    def __get_prediction(self, eye_input_l, eye_input_r):
        pred_l = self.__model.predict(eye_input_l)
        pred_r = self.__model.predict(eye_input_r)
        return pred_l, pred_r

    def __get_frontal_faces(self, img_ori):
        img_ori = cv2.resize(img_ori, dsize=(0, 0), fx=0.5, fy=0.5)
        img = img_ori.copy()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = self.__detector(gray)
        return faces, gray, img

    def __crop_eye(self, gray, eye_points):
        x1, y1 = np.amin(eye_points, axis=0)
        x2, y2 = np.amax(eye_points, axis=0)
        cx, cy = (x1 + x2) / 2, (y1 + y2) / 2

        w = (x2 - x1) * 1.2
        h = w * self.__IMG_SIZE[1] / self.__IMG_SIZE[0]

        margin_x, margin_y = w / 2, h / 2

        min_x, min_y = int(cx - margin_x), int(cy - margin_y)
        max_x, max_y = int(cx + margin_x), int(cy + margin_y)

        eye_rect = np.rint([min_x, min_y, max_x, max_y]).astype(np.int)

        eye_img = gray[eye_rect[1]:eye_rect[3], eye_rect[0]:eye_rect[2]]

        return eye_img, eye_rect

    def __is_eye_dried(self):
        return self.__COUNT < 10


import argparse
import logging
import time

import cv2

from tf_pose.forward_head_detector import ForwardHeadDetector



logger = logging.getLogger('TfPoseEstimator-WebCam')
logger.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

fps_time = 0

if __name__ == '__main__':
    # logger.debug('cam read+')
    cam = cv2.VideoCapture(0)
    ret_val, image = cam.read()
    # logger.info('cam image=%dx%d' % (image.shape[1], image.shape[0]))
    detector = ForwardHeadDetector()

    while True:
        ret_val, origin_image = cam.read()

        # logger.debug('image process+')
        result, image = detector.detect(origin_image)

        if result == 1:
            result_sentence = "forward_head_posture"
        elif result == 0:
            result_sentence = "Good Posture"
        else:
            result_sentence = "waiting.."

        # logger.debug('show+')
        cv2.putText(image,
                    "FPS: %f" % (1.0 / (time.time() - fps_time)),
                    (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.putText(image, result_sentence,
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)

        cv2.imshow('tf-pose-estimation result', image)
        fps_time = time.time()

        #ESC key
        if cv2.waitKey(1) == 27:
            break
        # logger.debug('finished+')

    cv2.destroyAllWindows()

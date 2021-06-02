import sys, os
import cv2

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from tf_pose_estimation.tf_pose.forward_head_detector import ForwardHeadDetector


class NeckTracker:

    def __init__(self):
        self.detector = ForwardHeadDetector()

    def is_good_posture(self, img_ori):

        result, image = self.detector.detect(img_ori)

        if result == 1:
            result_sentence = "forward_head_posture"
        elif result == 0:
            result_sentence = "Good Posture"
        else:
            result_sentence = "waiting.."

        cv2.putText(image,
                    (10, 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)
        cv2.putText(image, result_sentence,
                    (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)

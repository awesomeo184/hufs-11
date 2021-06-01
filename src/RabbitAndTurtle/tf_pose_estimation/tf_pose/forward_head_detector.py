import argparse
import logging
import math
import cv2

from estimator import TfPoseEstimator
from networks import get_graph_path, model_wh
import common


logger = logging.getLogger('TfPoseEstimator')
logger.handlers.clear()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

def str2bool(v):
    return v.lower() in ("yes", "true", "t", "1")


class ForwardHeadDetector:
    def __init__(self):
        parser = argparse.ArgumentParser(description='tf-pose-estimation realtime webcam')
        parser.add_argument('--camera', type=int, default=0)

        parser.add_argument('--resize', type=str, default='0x0',
                            help='if provided, resize images before they are processed. default=0x0, Recommends : 432x368 or 656x368 or 1312x736 ')
        parser.add_argument('--resize-out-ratio', type=float, default=4.0,
                            help='if provided, resize heatmaps before they are post-processed. default=1.0')

        parser.add_argument('--model', type=str, default='mobilenet_thin',
                            help='cmu / mobilenet_thin / mobilenet_v2_large / mobilenet_v2_small')
        parser.add_argument('--show-process', type=bool, default=False,
                            help='for debug purpose, if enabled, speed for inference is dropped.')

        parser.add_argument('--tensorrt', type=str, default="False",
                            help='for tensorrt process.')
        self.args = parser.parse_args()

        logger.debug('initialization %s : %s' % (self.args.model, get_graph_path(self.args.model)))
        self.w, self.h = model_wh(self.args.resize)
        if self.w > 0 and self.h > 0:
            self.estimator = TfPoseEstimator(get_graph_path(self.args.model),
                                             target_size=(self.w, self.h), trt_bool=str2bool(self.args.tensorrt))
        else:
            self.estimator = TfPoseEstimator(get_graph_path(self.args.model),
                                             target_size=(432, 368), trt_bool=str2bool(self.args.tensorrt))

    def draw_triangle(self, npimg, user, ratio):
        image_h, image_w = npimg.shape[:2]

        nose = user.body_parts[0]
        r_shoulder = user.body_parts[2]
        l_shoulder = user.body_parts[5]

        nose_center = (int(nose.x * image_w + 0.5), int(nose.y * image_h + 0.5))
        r_shoulder_center = (int(r_shoulder.x * image_w + 0.5), int(r_shoulder.y * image_h + 0.5))
        l_shoulder_center = (int(l_shoulder.x * image_w + 0.5), int(l_shoulder.y * image_h + 0.5))
        bisector = (int((r_shoulder_center[0] + l_shoulder_center[0]) / 2.0),
                    int((r_shoulder_center[1] + l_shoulder_center[1]) / 2.0))

        # draw points
        cv2.circle(npimg, nose_center, 3, common.CocoColors[0], thickness=3, lineType=8, shift=0)
        cv2.circle(npimg, r_shoulder_center, 3, common.CocoColors[2], thickness=3, lineType=8, shift=0)
        cv2.circle(npimg, l_shoulder_center, 3, common.CocoColors[5], thickness=3, lineType=8, shift=0)
        cv2.circle(npimg, bisector, 3, (255, 255, 255), thickness=3, lineType=8, shift=0)

        # draw lines
        cv2.line(npimg, r_shoulder_center, l_shoulder_center, (0, 255, 0), 3)
        cv2.line(npimg, nose_center, bisector, (0, 255, 0), 3)

        cv2.putText(npimg,
                    "ratio: %f" % ratio,
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                    (0, 255, 0), 2)

        return npimg

    def detect(self, npimg):
        result = 0
        humans = self.estimator.inference(npimg, resize_to_default=(self.w > 0 and self.h > 0),
                                          upsample_size=self.args.resize_out_ratio)
        if not humans:
            return -1, npimg

        image_h, image_w = npimg.shape[:2]

        nose_key = 0
        r_shoulder_key = 2
        l_shoulder_key = 5
        user = humans[0]
        if nose_key in user.body_parts.keys() and r_shoulder_key in user.body_parts.keys() and\
                l_shoulder_key in user.body_parts.keys():
            nose = user.body_parts[0]
            r_shoulder = user.body_parts[2]
            l_shoulder = user.body_parts[5]

            nose_center = (int(nose.x * image_w + 0.5), int(nose.y * image_h + 0.5))
            r_shoulder_center = (int(r_shoulder.x * image_w + 0.5), int(r_shoulder.y * image_h + 0.5))
            l_shoulder_center = (int(l_shoulder.x * image_w + 0.5), int(l_shoulder.y * image_h + 0.5))
            bisector = (int((r_shoulder_center[0] + l_shoulder_center[0]) / 2.0),
                            int((r_shoulder_center[1] + l_shoulder_center[1]) / 2.0))

            height = math.sqrt(pow(nose_center[0] - bisector[0], 2) + pow(nose_center[1] - bisector[1], 2))
            width = math.sqrt(pow(r_shoulder_center[0] - l_shoulder_center[0], 2) + pow(r_shoulder_center[1] - l_shoulder_center[0], 2))

            ratio = height / width
            if ratio < 0.5:
                result = 1

            #for debugging
            # self.draw_triangle(npimg, user, ratio)

        return result, npimg



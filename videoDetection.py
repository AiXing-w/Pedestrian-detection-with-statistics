import cv2
from centernet import CenterNet
from PIL import Image
import numpy as np

path = "test.flv"  # 视频路径
centernet = CenterNet()
capture = cv2.VideoCapture(path)
fps = capture.get(cv2.CAP_PROP_FPS)
ref, frame = capture.read()
print("fps:{}".format(int(fps)))

i = 0
while capture.isOpened():
    ref, frame = capture.read()
    if frame is not None:
        frame = cv2.resize(frame, (frame.shape[1]//2, frame.shape[0]//2))
        frame = Image.fromarray(np.uint8(frame))
        frame, num = centernet.detect_image(frame)
        frame = np.array(frame)
        cv2.imwrite('./videos/{:06d}.png'.format(i), frame)
        print(i)
        i += 1
    else:
        break


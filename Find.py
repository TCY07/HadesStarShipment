
# 查找各种图像,主要涉及图像处理

import cv2
import numpy as np


def Find(template, background, range):
    filename = 'Pictures/' + str(template) + '.PNG'
    target = cv2.imread(filename)
    target = cv2.cvtColor(target, cv2.COLOR_RGB2GRAY)
    background = cv2.cvtColor(background, cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(background, target, cv2.TM_SQDIFF_NORMED)

    if range > 0:
        loc = np.where(result > range)
    elif range < 0:
        loc = np.where(result < -range)

    if len(loc[0]) == 0:
        print("模板" + str(template) + "匹配失败")

    for pt in zip(*loc[::-1]):
        bottom_right = (pt[0] + target.shape[1], pt[1] + target.shape[0])
        cv2.rectangle(background, pt, bottom_right, (255, 255, 255), 2)

    return loc



# 查找各种图像,主要涉及图像处理

import cv2
import numpy as np
import window
import data


# 通过星球编号number，从传入图像background中查找星球坐标
def findPlanet(number, background, tolerance):
    filename = 'Pictures/' + str(number) + '.PNG'
    target = cv2.imread(filename)
    target = cv2.cvtColor(target, cv2.COLOR_RGB2GRAY)
    background = cv2.cvtColor(background, cv2.COLOR_RGB2GRAY)
    result = cv2.matchTemplate(background, target, cv2.TM_SQDIFF_NORMED)

    if tolerance > 0:
        locs = np.where(result > tolerance)
    elif tolerance < 0:
        locs = np.where(result < -tolerance)

    if len(locs) == 0:
        print("星球%d模板匹配失败", number)
        return None

    x = y = 0
    for pt in zip(*locs[::-1]):
        x += pt[0] + 0.5 * target.shape[1]
        y += pt[1] + 0.5 * target.shape[0]

    loc = (int(x / len(list(zip(*locs[::-1])))), int(y / len(list(zip(*locs[::-1])))))

    return loc


# 让指定的星区进入视野范围,tolerance容忍星区不完全在视野内
def findSector(planetNum, tolerance):
    sectorName = data.PLANET_SECTOR[planetNum]
    sector_x, sector_y = data.sectorPostion(sectorName)

    sunPos = window.sunPosition()
    # 当前屏幕视野范围（星系坐标）
    up_left = (-700 - sunPos[0], -442 - sunPos[1])
    down_right = (700 - sunPos[0], 442 - sunPos[1])

    if sector_x + tolerance < up_left[0]:  # 星区位于视野左侧
        newSunPos_x = sunPos[0] + up_left[0] - sector_x - tolerance
    elif sector_x + 2 * data.a - tolerance > down_right[0]:  # 星区位于视野右侧
        newSunPos_x = sunPos[0] + down_right[0] - sector_x - 2 * data.a + tolerance
    else:
        newSunPos_x = sunPos[0]

    if sector_y + tolerance < up_left[1]:  # 星区位于视野上侧
        newSunPos_y = sunPos[1] + up_left[1] - sector_y - tolerance
    elif sector_y + 2 * data.r - tolerance > down_right[1]:  # 星区位于视野下侧
        newSunPos_y = sunPos[1] + down_right[1] - sector_y - 2 * data.r + tolerance
    else:
        newSunPos_y = sunPos[1]

    # 重新定位视野，使得指定星区进入视野中
    window.Relocate((newSunPos_x, newSunPos_y), 10)

    # 截取指定星区图像
    screen, (screen_x, screen_y, _, _) = window.ScreenShot()
    sunPos = window.sunPosition()
    # 当前屏幕视野范围（星系坐标）
    up_left = (-700 - sunPos[0], -442 - sunPos[1])

    x1 = max(0, sector_x - up_left[0])
    x1 = int(x1)
    x2 = min(x1 + 2 * data.a + min(sector_x - up_left[0], 0), 1400)
    x2 = int(x2)

    y1 = max(0, sector_y - up_left[1])
    y1 = int(y1)
    y2 = min(y1 + 2 * data.r + min(sector_y - up_left[1], 0), 885)
    y2 = int(y2)

    img = screen[y1:y2, x1:x2]  # 选取指定星区

    # 获得星球在星区截图中的坐标
    loc = findPlanet(planetNum, img, -0.3)
    # 在屏幕中的坐标
    pos = (screen_x + loc[0] + x1, screen_y + loc[1] + y1)

    return pos



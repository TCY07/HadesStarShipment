
# 查找各种图像,主要涉及图像处理
import time

import cv2
import numpy as np
import win32api, win32gui, win32con
import window
import data


# 通过星球编号number，从传入图像background中查找星球坐标
def match(number, background, tolerance):
    if isinstance(number, int) and number < 1000:
        filename = 'Pictures/' + str(number) + '.PNG'
    else:
        filename = 'Pictures/center.PNG'
    target = cv2.imread(filename)
    target = cv2.split(target)[1]
    background = cv2.split(background)[1]

    result = cv2.matchTemplate(background, target, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if tolerance > 0:
        if max_val > tolerance:
            x = max_loc[0] + 0.5 * target.shape[1]
            y = max_loc[1] + 0.5 * target.shape[0]

            # cv2.rectangle(background, max_loc,
            #               (max_loc[0] + target.shape[1], max_loc[1] + target.shape[0]), (255, 255, 255), 2)
            # window.imshow(background, str(number))
            # print(max_val)

            return int(x), int(y)
        else:
            # print("星球%d匹配失败" % number)
            return None
    elif tolerance < 0:
        if min_val < -tolerance:
            x = max_loc[0] + 0.5 * target.shape[1]
            y = max_loc[1] + 0.5 * target.shape[0]
            return int(x), int(y)
        else:
            # print("星球%d匹配失败" % number)
            return None


# 返回指定星球的屏幕坐标
# 让指定的星区进入视野范围,tolerance容忍星区不完全在视野内
def findPlanet(planetNum, tolerance=-60):
    # 特例：要寻找的是曲道枢纽
    if planetNum > 2000:
        if planetNum == 2003:  # 3号枢纽
            center, temp = findPlanet(16)
            return (center[0] - 15, center[1] + 55), (temp[0] - 15, temp[1] + 55)

    sunPos = window.sunPosition()
    # 当前屏幕视野范围（星系坐标）
    up_left = (-700 - sunPos[0], -442 - sunPos[1])
    down_right = (700 - sunPos[0], 242 - sunPos[1])  # 考虑下方信息窗口的遮挡

    sectorName = data.PLANET_SECTOR[planetNum]
    sector_x, sector_y = data.sectorPostion(sectorName)
    if planetNum < 1000:  # 是星球
        h = 2 * data.r
        w = 2 * data.a
    elif planetNum < 2000:  # 是贸易站
        h = w = 130

    if sector_x + tolerance < up_left[0]:  # 星区位于视野左侧
        newSunPos_x = sunPos[0] + up_left[0] - sector_x - tolerance
    elif sector_x + w - tolerance > down_right[0]:  # 星区位于视野右侧
        newSunPos_x = sunPos[0] + down_right[0] - sector_x - w + tolerance
    else:
        newSunPos_x = sunPos[0]

    if sector_y + tolerance < up_left[1]:  # 星区位于视野上侧
        newSunPos_y = sunPos[1] + up_left[1] - sector_y - tolerance
    elif sector_y + h - tolerance > down_right[1]:  # 星区位于视野下侧
        newSunPos_y = sunPos[1] + down_right[1] - sector_y - h + tolerance
    else:
        newSunPos_y = sunPos[1]

    # 重新定位视野，使得指定星区进入视野中
    window.Relocate((newSunPos_x, newSunPos_y), 70)

    # 截取指定星区图像
    screen, (screen_x, screen_y, _, _) = window.ScreenShot()
    sunPos = window.sunPosition()
    # 当前屏幕视野范围（星系坐标）
    up_left = (-700 - sunPos[0], -442 - sunPos[1])

    x1 = max(0, sector_x - up_left[0])
    x1 = int(x1)
    x2 = min(x1 + w + min(sector_x - up_left[0], 0), 1400)
    x2 = int(x2)

    y1 = max(0, sector_y - up_left[1])
    y1 = int(y1)
    y2 = min(y1 + h + min(sector_y - up_left[1], 0), 885)
    y2 = int(y2)

    img = screen[y1:y2, x1:x2]  # 选取指定星区

    # 获得星球在星区截图中的坐标
    loc = match(planetNum, img, 0.4)
    # 在屏幕中的坐标
    pos = (screen_x + loc[0] + x1, screen_y + loc[1] + y1)
    # 星球在星区坐标系下的坐标
    pos1 = (up_left[0] + x1 + loc[0], up_left[1] + y1 + loc[1])

    # 返回星球的：屏幕坐标，星区坐标
    return pos, pos1


# 尝试在结果图中找到两颗卫星的轮廓
def tryGetMoon(result, threshold):
    _, bw = cv2.threshold(result, threshold, 255, cv2.THRESH_BINARY)  # 转化为二值图像
    s = np.ones((5, 5))
    bw = cv2.dilate(bw, s)

    contours, _ = cv2.findContours(np.uint8(bw), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    return contours


# 找卫星
def findMoon(planetNum):
    # 先找所环绕的行星
    planetPos, _ = findPlanet(int(planetNum / 100), -250)
    win32api.SetCursorPos(planetPos)
    window.Roll(1, 8)  # 以行星为中心放大
    time.sleep(0.2)
    win32api.SetCursorPos((planetPos[0] - 130, planetPos[1] - 130))  # 鼠标移开避免影响识别
    time.sleep(0.5)

    # 截取指定星区图像
    screen, (screen_x, screen_y, _, _) = window.ScreenShot()
    # 当前屏幕视野范围（星系坐标）
    x1 = planetPos[0] - screen_x - 137
    y1 = planetPos[1] - screen_y - 137

    img = screen[y1:y1 + 274, x1:x1 + 274]  # 选取指定星区

    # 初始行星有2个很像的卫星，之后单独处理
    if int(planetNum / 100) != 1:
        loc = match(planetNum, img, 0.4)

        truePos = (planetPos[0] - 117 + loc[0], planetPos[1] - 117 + loc[1])
        return truePos
    else:
        filename = 'Pictures/' + str(planetNum) + '.PNG'
        target = cv2.imread(filename)
        target = cv2.split(target)[1]
        img = cv2.split(img)[1]

        result = cv2.matchTemplate(img, target, cv2.TM_CCORR_NORMED)

        threshold = 0.7
        contours = tryGetMoon(result, threshold)
        while len(contours) < 2:
            threshold -= 0.01
            contours = tryGetMoon(result, threshold)
            if len(contours) > 2:
                print("定位卫星失败")
                window.imshow(result)
                exit(1)
        if len(contours) != 2:
            print("定位卫星失败")
            window.imshow(result)
            exit(1)
        (x1, y1), _ = cv2.minEnclosingCircle(contours[0])
        (x2, y2), _ = cv2.minEnclosingCircle(contours[1])
        # 到行星的距离平方
        r1 = abs(x1 - 117) ** 2 + abs(y1 - 117) ** 2
        r2 = abs(x2 - 117) ** 2 + abs(y2 - 117) ** 2
        # 保证第一组数据储存的是内层卫星
        if r1 > r2:
            temp = x1
            x1 = x2
            x2 = temp
            temp = y1
            y1 = y2
            y2 = temp

        if planetNum % 100 == 1:
            truePos = (int(planetPos[0] - 117 + x1), int(planetPos[1] - 117 + y1))
            return truePos
        else:
            truePos = (int(planetPos[0] - 117 + x2), int(planetPos[1] - 117 + y2))
            return truePos


# 调试用
if __name__ == '__main__':
    handle = win32gui.FindWindow(None, 'Hades\' Star')
    win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)  # 取消最小化
    win32gui.SetForegroundWindow(handle)  # 高亮显示在前端
    # 设置窗口大小/位置
    win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 160, 50, 1600, 900, win32con.SWP_SHOWWINDOW)
    time.sleep(0.3)

    screen, _ = window.ScreenShot(handle)  # 窗口截图
    for num in range(1, 17):
        loc = match(num, screen, 0.5)

    '''
    pos, _ = findPlanet(16)
    pos = (pos[0] - 15, pos[1] + 55)
    win32api.SetCursorPos(pos)'''

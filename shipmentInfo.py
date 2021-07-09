
# 用于读取货物信息框内的内容

import window
import win32gui
import win32con
import cv2
import numpy as np
import time


# 传入单个货物的信息条截图，返回该货物的详细信息
def detailInfo(img):
    numberArea = img[0:20, 90:180]
    # _, numberArea = cv2.threshold(numberArea, 175, 255, cv2.THRESH_BINARY_INV)
    # cv2.imwrite('Pictures/name2.PNG', numberArea)
    # window.imshow(numberArea)
    k = nameMatch(numberArea, 'name1', 'name2')
    print(k)


# 传入星球名字截图，返回两个选项中可能性更大的一个序号
def nameMatch(img, p1, p2):
    template1 = cv2.imread('Pictures/' + str(p1) + '.PNG')
    template1 = cv2.cvtColor(template1, cv2.COLOR_RGB2GRAY)
    template2 = cv2.imread('Pictures/' + str(p2) + '.PNG')
    template2 = cv2.cvtColor(template2, cv2.COLOR_RGB2GRAY)

    # 将img转换为黑底白字
    _, img = cv2.threshold(img, 175, 255, cv2.THRESH_BINARY_INV)
    _, template1 = cv2.threshold(template1, 175, 255, cv2.THRESH_BINARY_INV)
    _, template2 = cv2.threshold(template2, 175, 255, cv2.THRESH_BINARY_INV)

    score1 = cv2.matchTemplate(img, template1, cv2.TM_CCORR_NORMED)
    score2 = cv2.matchTemplate(img, template2, cv2.TM_CCORR_NORMED)
    print(score1)
    print(score2)

    if score1 > score2:
        return 1
    else:
        return 2


# 将输入的轮廓按从上到下排序
def sortContours(contours):
    boundingBoxes = [cv2.boundingRect(cont) for cont in contours]
    (cnt, boundingBoxes) = zip(*sorted(zip(contours, boundingBoxes),
                                       key=lambda b: b[1][1]))
    return cnt


# 通过轮廓外接矩形的长宽比以及面积进行筛选
def contoursFilter(conts, ar, area):
    results = []
    for cont in conts:
        (x, y, w, h) = cv2.boundingRect(cont)
        # 轮廓外接矩形宽比长的值
        a = w / float(h)

        # 获取指定长宽比的轮廓
        if abs(ar - a) < 0.2 * ar:
            if abs(cv2.contourArea(cont) - area) < 0.1 * area:  # 通过面积二次确认
                # print(a)
                # print(cv2.contourArea(cont))
                results.append(cont)
    if len(results) > 0:
        return results
    else:
        print("轮廓获取失败")
        return None


handle = win32gui.FindWindow(None, 'Hades\' Star')

win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)  # 取消最小化
win32gui.SetForegroundWindow(handle)  # 高亮显示在前端
# 设置窗口大小/位置
win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 160, 50, 1600, 900, win32con.SWP_SHOWWINDOW)
time.sleep(0.3)

img, _ = window.ScreenShot(handle)
gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转换为灰度图
_, gray = cv2.threshold(gray, 65, 255, cv2.THRESH_BINARY_INV)  # 二值化

contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
conts = contoursFilter(contours, 0.535, 170000)  # 过滤得到货物窗口的轮廓
(x, y, w, h) = cv2.boundingRect(conts[0])
shipmentWindow = gray[y:y + h, x:x + w]  # 截取货物窗口图像
_, shipmentWindow = cv2.threshold(shipmentWindow, 175, 255, cv2.THRESH_BINARY_INV)

# s = np.ones((3, 3), np.uint8)
# shipmentWindow = cv2.morphologyEx(shipmentWindow, cv2.MORPH_CLOSE, s)  # 开运算，消除小亮点
upSide = shipmentWindow[0: 370, :]  # 截取星球货物部分（上侧）
coin = cv2.imread('Pictures/coin.PNG')
coin = cv2.cvtColor(coin, cv2.COLOR_RGB2GRAY)
match = cv2.matchTemplate(upSide, coin, cv2.TM_CCORR_NORMED)

locs = np.where(match > 0.5)
for pt in zip(*locs[::-1]):
    cv2.rectangle(upSide, (pt[0] - 230, pt[1]), (pt[0] + coin.shape[1], pt[1] + coin.shape[0]), (255, 255, 255), 1)

_, upSide = cv2.threshold(upSide, 175, 255, cv2.THRESH_BINARY_INV)
contours, _ = cv2.findContours(upSide, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

conts = contoursFilter(contours, 5.6, 10000)

# 将轮廓按从上到下排序
conts = sortContours(conts)
for ct in conts:
    (x, y, w, h) = cv2.boundingRect(ct)
    cut = upSide[y:y + h, x:x + w]
    detailInfo(cut)

cv2.drawContours(upSide, conts, -1, (0, 0, 0), 1)
window.imshow(upSide)

# cv2.drawContours(img, contours, i, (255, 255, 255), 2)
# window.imshow(img)



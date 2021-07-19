
# 用于读取货物信息框内的内容
import win32api

import window
import win32gui
import win32con
import cv2
import numpy as np
import time

nameTempla = {}

# 读入星球名字图像模板（黑底白字）
for num in range(1, 17):
    templa = cv2.imread('Pictures/name' + str(num) + '.PNG')
    templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
    # _, templa = cv2.threshold(templa, 175, 255, cv2.THRESH_BINARY_INV)
    nameTempla[num] = templa

templa = cv2.imread('Pictures/name101.PNG')
templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
# _, templa = cv2.threshold(templa, 175, 255, cv2.THRESH_BINARY_INV)
nameTempla[101] = templa

templa = cv2.imread('Pictures/name102.PNG')
templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
# _, templa = cv2.threshold(templa, 175, 255, cv2.THRESH_BINARY_INV)
nameTempla[102] = templa

templa = cv2.imread('Pictures/name201.PNG')
templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
# _, templa = cv2.threshold(templa, 175, 255, cv2.THRESH_BINARY_INV)
nameTempla[201] = templa

templa = cv2.imread('Pictures/name301.PNG')
templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
# _, templa = cv2.threshold(templa, 175, 255, cv2.THRESH_BINARY_INV)
nameTempla[301] = templa

coin = cv2.imread('Pictures/coin.PNG')
coin = cv2.cvtColor(coin, cv2.COLOR_RGB2GRAY)

crystal = cv2.imread('Pictures/crystal.PNG')
crystal = cv2.cvtColor(crystal, cv2.COLOR_RGB2GRAY)


for i in range(1, 4):
    templa = cv2.imread('Pictures/name' + str(1000 + i) + '.PNG')
    templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
    # _, templa = cv2.threshold(templa, 175, 255, cv2.THRESH_BINARY_INV)
    nameTempla[1000 + i] = templa


# 传入单个货物的信息条截图，返回该货物的详细信息
def detailInfo(img):
    # 目的地信息截图
    numberArea = img[0:25, 80:185]

    # 可用于制作模板
    # numberArea = img[5:20, 90:175]
    # _, numberArea = cv2.threshold(numberArea, 175, 255, cv2.THRESH_BINARY_INV)
    # cv2.imwrite('Pictures/name8.PNG', numberArea)
    # window.imshow(numberArea, '模板')

    planetName, _ = nameMatch(numberArea)
    return planetName


# 传入星球名字截图，返回星球序号和对应的匹配分数
def nameMatch(img):
    # 记录匹配得分
    scores = {}

    for i, templa in nameTempla.items():
        _, scores[i], _, _ = cv2.minMaxLoc(cv2.matchTemplate(img, templa, cv2.TM_CCORR_NORMED))

    max_Key = max(scores, key=scores.get)
    # print(max_Key)

    return max_Key, scores[max_Key]


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
            if abs(cv2.contourArea(cont) - area) < 0.2 * area:  # 通过面积二次确认
                # print(a)
                # print(cv2.contourArea(cont))
                results.append(cont)
    if len(results) > 0:
        return results
    else:
        print("轮廓获取失败")
        return None


# 获取货物窗口截图（黑底白字）,以及窗口的坐标信息
def getShipmentWindow():
    img, (x1, y1, _, _) = window.ScreenShot()
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转换为灰度图
    _, gray = cv2.threshold(gray, 65, 255, cv2.THRESH_BINARY_INV)  # 二值化

    contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    conts = contoursFilter(contours, 0.535, 170000)  # 过滤得到货物窗口的轮廓

    if conts is None:
        print("错误，视野中没有发现货物窗口")
        exit(1)

    # window.imshow(gray)
    (x, y, w, h) = cv2.boundingRect(conts[0])
    shipmentWindow = gray[y:y + h, x:x + w]  # 截取货物窗口图像
    _, shipmentWindow = cv2.threshold(shipmentWindow, 175, 255, cv2.THRESH_BINARY_INV)  # 转换为黑底白字

    return shipmentWindow, (x1 + x, y1 + y, w, h)


# 将货物窗口拆分成上下两部分，返回需要的部分的货物信息列表
def devideInfo(img, conts, part):
    if conts is None:  # 没有货物
        return []
    res = []
    for ct in conts:
        (x, y, w, h) = cv2.boundingRect(ct)
        if part == 'UP' and y < 360:  # 获取当前上侧（星球）货物信息列表
            cut = img[y:y + h, x:x + w]
            res.append(detailInfo(cut))
        elif part == 'BOTTOM' and y > 360:  # 获取当前下侧（货船）货物信息列表
            cut = img[y:y + h, x:x + w]
            res.append(detailInfo(cut))

    return res


# 获取当前货物视窗内所有货物的信息条轮廓，以及画了轮廓的货物视窗
def shipmentPosition():
    shipmentWindow, _ = getShipmentWindow()

    match = cv2.matchTemplate(shipmentWindow, coin, cv2.TM_CCORR_NORMED)
    match1 = cv2.matchTemplate(shipmentWindow, crystal, cv2.TM_CCORR_NORMED)

    # 用方框框出每一个货物信息条
    locs = np.where(match > 0.65)
    for pt in zip(*locs[::-1]):
        cv2.rectangle(shipmentWindow, (pt[0] - 230, pt[1]), (pt[0] + coin.shape[1], pt[1] + coin.shape[0]),
                      (255, 255, 255), 1)
    locs = np.where(match1 > 0.65)
    for pt in zip(*locs[::-1]):
        cv2.rectangle(shipmentWindow, (pt[0] - 230, pt[1]), (pt[0] + coin.shape[1], pt[1] + coin.shape[0]),
                      (255, 255, 255), 1)

    # 变为白底黑字，以获得信息条轮廓
    _, inverse = cv2.threshold(shipmentWindow, 175, 255, cv2.THRESH_BINARY_INV)

    # 过滤得到信息条内轮廓
    contours, hierarch = cv2.findContours(inverse, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    conts = []
    for num in range(len(contours)):
        if hierarch[0][num][3] < 0:  # 该轮廓无父轮廓
            conts.append(contours[num])
    # 再次过滤
    conts = contoursFilter(conts, 5.6, 10000)

    if conts is not None:
        # 将轮廓按从上到下排序
        conts = sortContours(conts)

    # 返回货物信息窗口，以及窗口各个货物信息条的轮廓
    return shipmentWindow, conts


# 拉取货物信息窗口的内容，获取该星球上的所有货物列表
def getPlanetShipment():
    i = 0
    info = []
    while 1:
        _, (x, y, _, _) = getShipmentWindow()  # 获取货物窗口的位置
        win32api.SetCursorPos((x + 80, y + 120))
        # 获取当前可见的货物信息轮廓
        shipmentWindow, conts = shipmentPosition()
        # 获取当前上侧（星球）货物信息列表
        res = devideInfo(shipmentWindow, conts, 'UP')

        if len(res) != 4:
            if i > 1:
                print("错误！期望读入4个数据，但读入了%d个" % len(res))
                exit(1)
            elif i == 1 and len(info[0]) == 4:
                print("错误！期望读入4个数据，但读入了%d个" % len(res))
                exit(1)

        info.append(res)

        # 与上一轮读入数据进行比较
        if i != 0:
            if info[i] == info[i - 1]:  # 与上一轮读入数据完全相同，视为已读到结尾
                if i == 1:
                    return info[0]
                elif i == 2:
                    result = []
                    if info[1][0] == info[0][3]:
                        result.extend(info[0])
                        result.extend([info[1][1], info[1][2], info[1][3]])
                        return result
                    elif info[1][0] == info[0][2]:
                        result.extend(info[0])
                        result.extend([info[1][2], info[1][3]])
                        return result
                    elif info[1][0] == info[0][1]:
                        result.extend(info[0])
                        result.append(info[1][3])
                        return result
                    else:
                        result.extend(info[0])
                        result.extend(info[1])
                        return result

                window.Roll(1, 3, 0)
                time.sleep(0.2)
                shipmentWindow, conts = shipmentPosition()
                back = devideInfo(shipmentWindow, conts, 'UP')  # 退回3个位置，读入货物信息

                if info[i - 2] == back:  # 1234 5678 999
                    connectingMode = 0
                    break
                elif [info[i - 3][3], info[i - 2][0], info[i - 2][1], info[i - 2][2]] == back:  # 1234 9999 99
                    connectingMode = 1
                    break
                elif [info[i - 3][2], info[i - 3][3], info[i - 2][0], info[i - 2][1]] == back:  # 1234 5678 9
                    connectingMode = 2
                    break
                elif [info[i - 2][1], info[i - 2][2], info[i - 2][3], info[i - 1][0]] == back:  # 1234 5678 9999
                    connectingMode = 3
                    break
                #  以下情况发生在info[i - 1]和info[i]其实不是完全相同的4个货物，也就是误判了结尾
                elif [info[i - 2][2], info[i - 2][3], info[i - 1][0], info[i - 1][1]] == back:
                    connectingMode = 4
                    break
                elif [info[i - 2][3], info[i - 1][0], info[i - 1][1], info[i - 1][2]] == back:
                    connectingMode = 5
                    break
                else:
                    print("错误！货物列表末尾出现了意料之外的布局")
                    exit(1)

        # 按照5-4-5-5-5的节奏滚动，可保证每次读入4个新货物的数据
        if i % 5 == 1:
            window.Roll(-1, 4, 0)
        else:
            window.Roll(-1, 5, 0)
        time.sleep(0.2)
        i += 1

    result = []
    # print(connectingMode)
    # print(info)
    # print("back:", back)
    if connectingMode == 0:  # 1234 5678 999
        for num in range(i - 1):
            result.extend(info[num])
        result.extend([info[i][1], info[i][2], info[i][3]])
    elif connectingMode == 1:  # 1234 5678 99
        for num in range(i - 1):
            result.extend(info[num])
        result.extend([info[i][2], info[i][3]])
    elif connectingMode == 2:  # 1234 5678 9
        for num in range(i - 1):
            result.extend(info[num])
        result.append(info[i][3])
    elif connectingMode == 3:  # 1234 5678 9999
        for num in range(i):
            result.extend(info[num])
    elif connectingMode == 4:
        for num in range(i):
            result.extend(info[num])
        result.append(info[i][0])
    elif connectingMode == 5:
        for num in range(i):
            result.extend(info[num])
        result.extend([info[i][0], info[i][1]])

    return result


# 调试用
if __name__ == '__main__':
    handle = win32gui.FindWindow(None, 'Hades\' Star')
    win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)  # 取消最小化
    win32gui.SetForegroundWindow(handle)  # 高亮显示在前端
    # 设置窗口大小/位置
    win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 160, 50, 1600, 900, win32con.SWP_SHOWWINDOW)
    time.sleep(0.3)

    print(getPlanetShipment())



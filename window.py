# 用于窗口操作及视野移动控制
import time
import win32gui
import win32con
import win32api
from PIL import Image, ImageGrab
import numpy as np
import cv2
import Find
import data
from enum import Enum


class WindowName(Enum):
    SHIPMENT = 0
    INFO = 1


openedWindow = []
locationInfo = {}  # 星球坐标信息

# 打开指定的窗口
def openWindow(name):
    if name in openedWindow:  # 已经是打开状态，无需操作
        return
    else:
        if name == WindowName.SHIPMENT:  # 打开货物窗口
            openedWindow.append(name)
            KeyDown('r')

    time.sleep(0.5)


# 显示图片（测试用）
def imshow(img, name=''):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# 初始化窗口
def Init(name):
    # 获取游戏窗口句柄
    handle = win32gui.FindWindow(None, name)
    if handle == 0:
        print("没有找到游戏窗口")
        exit(0)

    win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)  # 取消最小化
    win32gui.SetForegroundWindow(handle)  # 高亮显示在前端
    # 设置窗口大小/位置
    win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 160, 50, 1600, 900, win32con.SWP_SHOWWINDOW)
    time.sleep(0.3)

    # 标准化窗口视野
    KeyDown('1', 0.1)
    KeyDown('1', 0.1)  # 双击某艘船编号
    KeyDown('F11')  # F11设置为时间调制器的快捷键
    # KeyDown('esc')  # esc关闭下方信息窗口
    x1, y1, x2, y2 = win32gui.GetWindowRect(handle)
    pos = (int((x1+x2)/2), int((y1+y2+35)/2))
    win32api.SetCursorPos(pos)
    Roll(-1, 13, 0.1)  # 滚轮调整视野缩放

    return handle


# 截取指定窗口画面,并返回截取的窗口对角坐标(左上/右下)
def ScreenShot(handle=None):
    if handle is None:
        handle = win32gui.FindWindow(None, 'Hades\' Star')

    x1, y1, x2, y2 = win32gui.GetWindowRect(handle)
    img = ImageGrab.grab((x1, y1, x2, y2))  # 截图
    img = np.array(img)
    img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)

    screen = img[50:935, 100:1500]  # 裁去边缘部分
    return screen, (x1 + 100, y1 + 50, x2 - 100, y2 - 15)


# 鼠标左键点击
def LClick(pos):
    win32api.SetCursorPos(pos)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, pos[0], pos[1], 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, pos[0], pos[1], 0, 0)


# 鼠标右键点击
def RClick(pos):
    win32api.SetCursorPos(pos)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, pos[0], pos[1], 0, 0)
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, pos[0], pos[1], 0, 0)


# 键盘输入,按下与抬起间隔时间downtime
def KeyDown(key, downtime=0.05):
    win32api.keybd_event(data.VK_CODE[key], 0, 0, 0)
    time.sleep(downtime)
    win32api.keybd_event(data.VK_CODE[key], 0, win32con.KEYEVENTF_KEYUP, 0)


# 鼠标滚轮操作(复数向下,正数向上)
def Roll(direction, times, sleeptime=0.05):
    for _ in range(times):
        win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, direction)
        time.sleep(sleeptime)


# 当前视野坐标定位
def sunPosition(handle=None):
    if handle is None:
        handle = win32gui.FindWindow(None, 'Hades\' Star')

    screen, _ = ScreenShot(handle)  # 窗口截图

    # 找到黄星
    s = np.ones((20, 20), np.uint8)
    opened = cv2.morphologyEx(screen, cv2.MORPH_OPEN, s)  # 开运算，消除小亮点
    grey = cv2.cvtColor(opened, cv2.COLOR_RGB2GRAY)  # 转换为灰度图
    _, grey = cv2.threshold(grey, 210, 255, cv2.THRESH_BINARY)  # 转化为二值图像

    # 计算黄星中心相对于图片中心坐标
    contours, _ = cv2.findContours(grey, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    if len(contours) == 0:  # 视野中没有找到黄星
        print("视野中没有找到黄星，通过其他星球计算")
        # 通过视野中的其他星球定位
        for num in range(1, 17):
            loc = Find.match(num, screen, 0.9)
            if loc is not None:  # 该星球出现在视野中
                # 从该星球坐标推算黄星坐标
                print('以星球%d为基准' % num)
                location = (int(loc[0] - locationInfo[num][0] - 700),
                            int(loc[1] - locationInfo[num][1] - 442))
                print(location)
                return location
        print("视野定位失败")
        exit(1)

    (x, y), _ = cv2.minEnclosingCircle(contours[0])
    # 如果有多个疑似点，则选择面积最大的点视为黄星
    if len(contours) != 1:
        print("有%d个疑似点" % len(contours))
        # 选择面积最大的点视为黄星
        maxArea = cv2.contourArea(contours[0])
        for cont in contours:
            if cv2.contourArea(cont) > maxArea:
                (x, y), _ = cv2.minEnclosingCircle(cont)

    location = (int(x - screen.shape[1] / 2), int(y - screen.shape[0] / 2))
    return location


# 移动视野,使黄星坐标变为给定坐标
def Relocate(pos, tolerance=50):
    current = sunPosition()

    x = pos[0] - current[0]
    y = pos[1] - current[1]

    while x > tolerance:
        KeyDown('left_arrow', 0.001 * abs(x))
        current = sunPosition()
        x = pos[0] - current[0]
    while x < -tolerance:
        KeyDown('right_arrow', 0.001 * abs(x))
        current = sunPosition()
        x = pos[0] - current[0]

    while y > tolerance:
        KeyDown('up_arrow', 0.001 * abs(y))
        current = sunPosition()
        y = pos[1] - current[1]
    while y < -tolerance:
        KeyDown('down_arrow', 0.001 * abs(y))
        current = sunPosition()
        y = pos[1] - current[1]


# 获取星球坐标信息并保存到本地
def savePlanetLocation():
    info = {}
    for num in range(1, 17):
        _, loc = Find.findPlanet(num)  # 获取星球的星区坐标
        info[num] = loc
    fileObject = open('locationInfo.txt', 'w')
    fileObject.write(str(info))
    fileObject.close()


# 读取星球位置信息文件
def getPlanetLocation():
    global locationInfo
    try:
        fileObject = open('locationInfo.txt', 'r')
    except IOError:
        savePlanetLocation()
        fileObject = open('locationInfo.txt', 'r')
    locationInfo = eval(fileObject.read())
    fileObject.close()



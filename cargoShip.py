
# 用于管理货船

from enum import Enum
import window
import cv2
import shipmentInfo
import win32gui
import win32con
import win32api
import time

# 读入匹配模板
moving_templa = cv2.imread('Pictures/moving.PNG')
moving_templa = cv2.cvtColor(moving_templa, cv2.COLOR_RGB2GRAY)
stop_templa = cv2.imread('Pictures/stop.PNG')
stop_templa = cv2.cvtColor(stop_templa, cv2.COLOR_RGB2GRAY)
button4 = cv2.imread('Pictures/button4.PNG')
button4 = cv2.cvtColor(button4, cv2.COLOR_RGB2GRAY)


# 货船状态类型
class State(Enum):
    UNCLER = 0
    STOP_STATION = 1
    STOP_ELSEWHERE = 2
    MOVING = 3


# 进行模板匹配
def match(img, templa, threshold=0.0):
    res = cv2.matchTemplate(img, templa, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)

    # print(max_val)
    if max_val < threshold:  # 匹配失败
        return None

    return max_val, max_loc


# 卸掉所有货物
def dischargeAll():
    window.openWindow(window.WindowName.shipment)
    img, _ = window.ScreenShot()
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转换为灰度图
    _, gray = cv2.threshold(gray, 65, 255, cv2.THRESH_BINARY_INV)  # 二值化

    contours, _ = cv2.findContours(gray, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    conts = shipmentInfo.contoursFilter(contours, 0.535, 170000)  # 过滤得到货物窗口的轮廓
    (x, y, w, h) = cv2.boundingRect(conts[0])
    shipmentWindow = gray[y:y + h, x:x + w]  # 截取货物窗口图像
    _, shipmentWindow = cv2.threshold(shipmentWindow, 175, 255, cv2.THRESH_BINARY_INV)


# 一艘货船的对象
class Ship:
    number = 0  # 该货船的编号
    statement = State.UNCLER  # 当前状态
    destination = None  # 当前目的地
    arriveTime = 0  # 到达目的地的时间

    onboardShipment = []  # 搭载的货物

    # 载入货物栏最上方的一个货物,要求当前货船处于选中状态
    def load(self, des):
        if window.WindowName.shipment not in window.openedWindow:  # 货物窗口未打开
            # 打开货物窗口
            window.KeyDown('r')
            window.openedWindow.append(window.WindowName.shipment)

        window.LClick((330, 350))
        self.onboardShipment.append(des)

    # 初始化，获取货船信息
    def __init__(self, num):
        self.number = num  # 获取编号

        # 本段主要方便调试，最后可删除
        handle = win32gui.FindWindow(None, 'Hades\' Star')
        win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)  # 取消最小化
        win32gui.SetForegroundWindow(handle)  # 高亮显示在前端
        # 设置窗口大小/位置
        win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 160, 50, 1600, 900, win32con.SWP_SHOWWINDOW)
        time.sleep(0.3)

        # window.KeyDown(str(num))
        # time.sleep(0)

        img, _ = window.ScreenShot()
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转换为灰度图
        infoWindow = gray[710:, 525:875]  # 截取信息窗口图像
        window.imshow(infoWindow)

        score1, _ = match(infoWindow, stop_templa)
        score2, _ = match(infoWindow, moving_templa)

        if score1 > score2:  # 状态是“泊靠在”
            if match(infoWindow, button4, 0.95) is not None:  # 检测到货物按钮
                self.statement = State.STOP_STATION  # 停靠在星球或贸易站上

            else:
                self.statement = State.STOP_ELSEWHERE  # 停靠在其他地方
        else:  # 状态是“移动至...”
            self.statement = State.MOVING

        print(self.statement)


for i in range(5, 6):
    ship = Ship()
    ship.load(i)


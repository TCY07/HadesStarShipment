
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

empty = cv2.imread('Pictures/cargoship_empty.PNG')
empty = cv2.split(empty)[2]
full = cv2.imread('Pictures/cargoship_full.PNG')
full = cv2.split(full)[2]


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


# 一艘货船的对象
class Ship:
    number = 0  # 该货船的编号
    statement = State.UNCLER  # 当前状态
    destination = None  # 当前目的地
    arriveTime = 0  # 到达目的地的时间
    chosen = False  # 这艘船是否是当前选中目标

    # 选中这艘货船
    def chose(self):
        if not self.chosen:  # 未被选中（已被选中则无需操作）
            window.KeyDown(str(self.number))
            self.chosen = True

    # 装载星球货物栏最上方的一个货物
    def load(self):
        # 选中并打开货物窗口
        self.chose()
        window.openWindow(window.WindowName.SHIPMENT)

        _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口的位置
        window.LClick((x + 80, y + 120))  # 点击第一个货物的位置
        print((x + 80, y + 120))

    # 卸载货船货物栏的一个货物,输入参数决定是卸载最上方还是最下方
    def discharge(self, side):
        # 选中并打开货物窗口
        self.chose()
        window.openWindow(window.WindowName.SHIPMENT)

        _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口的位置
        if side == 'TOP':
            win32api.SetCursorPos((x + 80, y + 420))
            window.Roll(1, 50, 0)  # 将货物条拉至最上方
            window.LClick((x + 80, y + 420))  # 点击第一个货物的位置
        elif side == 'BOTTOM':
            win32api.SetCursorPos((x + 80, y + 480))
            window.Roll(-1, 50, 0)  # 将货物条拉至最下方
            window.LClick((x + 80, y + 480))  # 点击最后一个货物的位置

    # 装载所有货物（一键装货）
    def loadAll(self):
        # 选中并打开货物窗口
        self.chose()
        window.openWindow(window.WindowName.SHIPMENT)

        _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口的位置
        window.LClick((x + 195, y + 380))  # 点击一键装货

    # 卸掉所有货物（一键卸货）
    def dischargeAll(self):
        # 选中并打开货物窗口
        self.chose()
        window.openWindow(window.WindowName.SHIPMENT)

        _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口图像
        window.LClick((x + 250, y + 380))  # 点击一键卸货

    # 根据图像判断本货船是否有载货
    def isLoaded(self):
        # 双击放大选中
        window.KeyDown(str(self.number))
        window.KeyDown(str(self.number))
        time.sleep(0.5)

        img, (x1, y1, x2, y2) = window.ScreenShot()
        x = int((x2 - x1) / 2) - 40
        y = int((y2 - y1) / 2) - 35
        center = img[y:y + 70, x: x + 80]  # 截取中心部分（货船所在位置）
        center = cv2.split(center)[2]
        window.imshow(center)

        res1 = cv2.matchTemplate(center, empty, cv2.TM_CCORR_NORMED)
        res2 = cv2.matchTemplate(center, full, cv2.TM_CCORR_NORMED)
        _, score1, _, _ = cv2.minMaxLoc(res1)
        _, score2, _, _ = cv2.minMaxLoc(res2)

        print(score1)
        print(score2)

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

        # h = infoWindow[115:130, 180:240]
        # window.imshow(h)

        score1, _ = match(infoWindow, stop_templa)
        score2, _ = match(infoWindow, moving_templa)

        if score1 > score2:  # 状态是“泊靠在”
            if match(infoWindow, button4, 0.95) is not None:  # 检测到货物按钮
                self.statement = State.STOP_STATION  # 停靠在星球或贸易站上

            else:
                self.statement = State.STOP_ELSEWHERE  # 停靠在其他地方
        else:  # 状态是“移动至...”
            self.statement = State.MOVING


for i in range(5, 6):
    ship = Ship(i)
    ship.isLoaded()


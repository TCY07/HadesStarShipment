
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
# “移动至”
moving_templa = cv2.imread('Pictures/moving.PNG')
moving_templa = cv2.cvtColor(moving_templa, cv2.COLOR_RGB2GRAY)
# “泊靠在”
stop_templa = cv2.imread('Pictures/stop.PNG')
stop_templa = cv2.cvtColor(stop_templa, cv2.COLOR_RGB2GRAY)
# 第四个按钮
button4 = cv2.imread('Pictures/button4.PNG')
button4 = cv2.cvtColor(button4, cv2.COLOR_RGB2GRAY)
# “太空曲道枢纽”
warplane = cv2.imread('Pictures/warplane.PNG')
warplane = cv2.cvtColor(warplane, cv2.COLOR_RGB2GRAY)

# 读入曲道外星球的信息窗口名字模板
nameTempla = {}
templa = cv2.imread('Pictures/info4.PNG')
templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
nameTempla[4] = templa
templa = cv2.imread('Pictures/info5.PNG')
templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
nameTempla[5] = templa
templa = cv2.imread('Pictures/info7.PNG')
templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
nameTempla[7] = templa
templa = cv2.imread('Pictures/info8.PNG')
templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
nameTempla[8] = templa
templa = cv2.imread('Pictures/info10.PNG')
templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
nameTempla[10] = templa
templa = cv2.imread('Pictures/info16.PNG')
templa = cv2.cvtColor(templa, cv2.COLOR_RGB2GRAY)
nameTempla[16] = templa


# 货船状态类型
class State(Enum):
    UNCLER = 0
    STOP_PLANET = 1
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


# 传入目的地信息截图，返回可能的星球序号和对应的匹配分数
def nameMatch(img):
    # 记录匹配得分
    scores = {}

    for i, templa in nameTempla.items():
        _, scores[i], _, _ = cv2.minMaxLoc(cv2.matchTemplate(img, templa, cv2.TM_CCORR_NORMED))

    max_Key = max(scores, key=scores.get)
    # print(max_Key)

    return max_Key, scores[max_Key]


# 一艘货船的对象
class Ship:
    # 货船列表
    ships = {}

    number = None  # 该货船的编号
    statement = State.UNCLER  # 当前状态
    destination = None  # 当前目的地
    arriveTime = 0  # 估计到达目的地的时间
    chosen = False  # 这艘船是否是当前选中目标
    loaded = False  # 这艘船是否有载货

    # 选中这艘货船
    def chose(self):
        if not self.chosen:  # 未被选中（已被选中则无需操作）
            # 取消所有货船的选中状态
            for item in self.ships.values():
                item.chosen = False
            # 选中自己
            window.KeyDown(str(self.number))
            self.chosen = True

            time.sleep(0.5)

    # 装载星球货物栏最上方的一个货物
    def load(self):
        # 选中并打开货物窗口
        self.chose()
        window.openWindow(window.WindowName.SHIPMENT)

        _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口的位置
        window.LClick((x + 80, y + 120))  # 点击第一个货物的位置
        print((x + 80, y + 120))

    # 判断该货船上有无货物，并更新货物信息
    def isLoaded(self):
        self.where()
        if self.statement == State.STOP_PLANET:  # 停靠在货点
            window.openWindow(window.WindowName.SHIPMENT)
            # 判断货船内有无货物
            shipmentWindow, conts = shipmentInfo.shipmentPosition()
            if len(shipmentInfo.devideInfo(shipmentWindow, conts, 'BPTTOM')) == 0:  # 货物窗口无货物
                self.loaded = False
                return False
            else:
                self.loaded = True
                return True
        else:  # 停靠在非货点
            return None

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
        time.sleep(1.5)
        win32api.SetCursorPos((x + 120, y + 380))  # 鼠标移开，避免影响轮廓检测
        time.sleep(0.1)

    # 卸掉所有货物（一键卸货）
    def dischargeAll(self):
        # 选中并打开货物窗口
        self.chose()
        window.openWindow(window.WindowName.SHIPMENT)

        _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口图像
        window.LClick((x + 250, y + 380))  # 点击一键卸货
        time.sleep(1.5)
        win32api.SetCursorPos((x + 120, y + 380))  # 鼠标移开，避免影响轮廓检测
        time.sleep(0.1)

    # 更新本货船的状态，并返回目的地/停靠点信息
    def where(self):
        self.chose()

        # 获取货船移动状态
        img, _ = window.ScreenShot()
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转换为灰度图
        infoWindow = gray[710:, 525:875]  # 截取信息窗口图像

        score1, _ = match(infoWindow, stop_templa)
        score2, _ = match(infoWindow, moving_templa)
        if score1 > score2:  # 状态是“泊靠在”
            if match(infoWindow, button4, 0.95) is not None:  # 检测到货物按钮
                self.statement = State.STOP_PLANET  # 停靠在星球或贸易站上

            else:
                self.statement = State.STOP_ELSEWHERE  # 停靠在其他地方
        else:  # 状态是“移动至...”
            self.statement = State.MOVING

        # 获取货船停靠点/目的地信息
        destination = infoWindow[10:60, 50:150]  # 截取目的地/停靠点名字
        _, destination = cv2.threshold(destination, 120, 255, cv2.THRESH_BINARY)  # 二值化

        num, score1 = nameMatch(destination)  # 在星球中获取最可能的目的地及其对应分数
        # 进一步与非星球目的地进行比对
        _, score2, _, _ = cv2.minMaxLoc(cv2.matchTemplate(destination, warplane, cv2.TM_CCORR_NORMED))  # 曲道枢纽

        if max(score1, score2) < 0.75:  # 目的地是贸易站或曲道内星球
            self.destination = 1000
        elif score1 > score2:  # 目的地是曲道外星球或集货星球
            self.destination = num
        else:  # 目的地是曲道枢纽
            self.destination = 0

        print(self.number, self.destination)
        return self.destination

    # 初始化，获取货船信息
    def __init__(self, num):
        self.ships[num] = self

        self.number = num  # 获取编号

        # 获取货船移动状态，和停靠点
        self.where()
        # # 获取载货状态
        # self.isLoaded()


# 本段主要方便调试，最后可删除
# handle = win32gui.FindWindow(None, 'Hades\' Star')
# win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)  # 取消最小化
# win32gui.SetForegroundWindow(handle)  # 高亮显示在前端
# # 设置窗口大小/位置
# win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 160, 50, 1600, 900, win32con.SWP_SHOWWINDOW)
# time.sleep(0.3)

# 本段可用于截图保存信息窗口的名字图像模板
# img, _ = window.ScreenShot()
# gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转换为灰度图
# infoWindow = gray[710:, 525:875]  # 截取信息窗口图像
# h = infoWindow[35:48, 50:90]
# _, h = cv2.threshold(h, 120, 255, cv2.THRESH_BINARY)
# cv2.imwrite('Pictures/info16.PNG', h)
# window.imshow(h)



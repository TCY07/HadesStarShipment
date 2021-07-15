
# 用于管理货船

from enum import Enum
import window
import cv2
import shipmentInfo
import win32gui
import win32con
import win32api
import time
import Find
import main

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
    STOP = 1
    MOVING = 2


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

    # 初始化，获取货船信息
    def __init__(self, num):
        Ship.ships[num] = self  # 将自身添加到货船列表

        self.number = num  # 该货船的编号
        self.chosen = False  # 这艘船是否是当前选中目标
        self.loaded = False  # 这艘船是否有载货
        self.statement, self.destination = self.where()  # 当前运动状态，以及当前目的地
        self.hasMission = False  # 登记自身是否在执行任务中

        # # 获取载货状态
        # self.isLoaded()

    # 选中这艘货船
    def choose(self):
        if not self.chosen:  # 未被选中（已被选中则无需操作）
            # 取消所有货船的选中状态
            for item in self.ships.values():
                item.chosen = False
            # 选中自己
            window.KeyDown(str(self.number))
            self.chosen = True
            time.sleep(0.5)

    # 装载星球货物栏中的一个货物，最上还是最下由side决定
    def load(self, side='TOP'):
        # 选中并打开货物窗口
        self.choose()
        window.openWindow(window.WindowName.SHIPMENT)
        _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口的位置

        if side == 'TOP':
            win32api.SetCursorPos((x + 80, y + 120))
            window.Roll(1, 50, 0)  # 将货物条拉至最上方
            time.sleep(0.1)
            window.LClick((x + 80, y + 120))  # 点击第一个货物的位置
        elif side == 'BOTTOM':
            win32api.SetCursorPos((x + 80, y + 330))
            window.Roll(-1, 50, 0)  # 将货物条拉至最下方
            time.sleep(0.1)
            window.LClick((x + 80, y + 330))  # 点击最后一个货物的位置

    # 判断该货船上有无货物，并更新货物信息
    def isLoaded(self):
        self.where()
        if self.statement == State.STOP:  # 停靠状态
            window.openWindow(window.WindowName.SHIPMENT)
            # 判断货船内有无货物
            shipmentWindow, conts = shipmentInfo.shipmentPosition()
            if len(shipmentInfo.devideInfo(shipmentWindow, conts, 'BOTTOM')) == 0:  # 货物窗口无货物
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
        self.choose()
        window.openWindow(window.WindowName.SHIPMENT)

        _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口的位置
        if side == 'TOP':
            win32api.SetCursorPos((x + 80, y + 420))
            window.Roll(1, 50, 0)  # 将货物条拉至最上方
            time.sleep(0.1)
            window.LClick((x + 80, y + 420))  # 点击第一个货物的位置
        elif side == 'BOTTOM':
            win32api.SetCursorPos((x + 80, y + 480))
            window.Roll(-1, 50, 0)  # 将货物条拉至最下方
            time.sleep(0.1)
            window.LClick((x + 80, y + 480))  # 点击最后一个货物的位置

    # 装载所有货物（一键装货）
    def loadAll(self):
        # 选中并打开货物窗口
        self.choose()
        window.openWindow(window.WindowName.SHIPMENT)

        _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口的位置
        window.LClick((x + 195, y + 380))  # 点击一键装货
        time.sleep(1.5)
        win32api.SetCursorPos((x + 120, y + 380))  # 鼠标移开，避免影响轮廓检测
        time.sleep(0.1)

    # 卸掉所有货物（一键卸货）
    def dischargeAll(self):
        # 选中并打开货物窗口
        self.choose()
        window.openWindow(window.WindowName.SHIPMENT)

        _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口图像
        window.LClick((x + 250, y + 380))  # 点击一键卸货
        time.sleep(1.5)
        win32api.SetCursorPos((x + 120, y + 380))  # 鼠标移开，避免影响轮廓检测
        time.sleep(0.1)

    # 更新并返回本货船的移动状态，以及目的地/停靠点信息
    def where(self):
        self.choose()

        # 获取货船移动状态
        img, _ = window.ScreenShot()
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转换为灰度图
        infoWindow = gray[710:, 525:875]  # 截取信息窗口图像

        score1, _ = match(infoWindow, stop_templa)
        score2, _ = match(infoWindow, moving_templa)
        if score1 > score2:  # 状态是“泊靠在”
            self.statement = State.STOP  # 停靠在星球或贸易站上
        else:  # 状态是“移动至...”
            self.statement = State.MOVING

        # 获取货船停靠点/目的地信息
        destination = infoWindow[10:60, 50:150]  # 截取目的地/停靠点名字
        _, destination = cv2.threshold(destination, 120, 255, cv2.THRESH_BINARY)  # 二值化

        num, score1 = nameMatch(destination)  # 在星球中获取最可能的目的地及其对应分数
        # 进一步与非星球目的地进行比对
        _, score2, _, _ = cv2.minMaxLoc(cv2.matchTemplate(destination, warplane, cv2.TM_CCORR_NORMED))  # 曲道枢纽

        if max(score1, score2) < 0.9:  # 目的地是贸易站或曲道内星球
            self.destination = 1000
        elif score1 > score2:  # 目的地是曲道外星球或集货星球
            self.destination = num
        else:  # 目的地是曲道枢纽
            self.destination = 0

        # print(self.number, self.destination)
        return self.statement, self.destination


class ACTION(Enum):
    Arriving = 0  # 前往并停靠在某处
    Passing = 1  # 经过且不停靠某处
    DischargeAll = 2  # 在当前停靠点卸载全部货物
    LoadAll = 3  # 装载当前停靠点的全部货物
    Discharge_TOP = 4  # 从上方开始卸货，卸货数量由第三个参数决定
    Load_TOP = 5  # 从顶层装载星球货物，装载数量由第三个参数决定
    Load_BOTTOM = 6  # 从底层装载星球货物，装载数量由第三个参数决定
    Carrying = 7  # 在贸易站提供货物存放功能


# 货船执行的任务
class Mission:
    # 执行中的任务列表
    missions = []

    # way_act是传入的action列表，形如[[1003, ACTION], [16, ACTION]]
    def __init__(self, ship, way_act):
        Mission.missions.append(self)

        self.master = ship  # 本任务由哪一艘货船执行
        ship.hasMission = True  # 将该货船登记为执行任务状态
        self.checkTime = -1  # 需要查验任务完成情况的时间，负数表示未设置
        self.process = 0  # 当前正在wayPoints中的第几项

        # 安排任务具体内容
        self.actions = way_act  # 需要经过的地点：经过或到达每个地点后需要完成的动作（装载、卸载、取消航线等）

    # 删除本任务
    def delete(self):
        Mission.missions.remove(self)
        self.master.hasMission = False
        print("任务完成")
        del self

    # 检查当前移动任务的完成进度若任务已完成则返回True
    def checkMovingStatus(self):
        statement, destination = self.master.where()  # 获取货船的当前运动状态和位置

        # 执行的任务是--到达某处
        if self.actions[self.process][1] == ACTION.Arriving:
            if statement == State.STOP:  # 已到达目的地
                self.process += 1  # 进行到下一步
                self.checkTime = -1
                return True
            else:
                return False
        # 执行的任务是--经过（不停靠）某处
        elif self.actions[self.process][1] == ACTION.Passing:
            if destination != self.actions[self.process][0] and statement == State.MOVING:  # 处于移动中，已经过该处
                self.process += 1  # 进行到下一步
                self.checkTime = -1
                return True
            else:
                return False

    # 检查货物装/卸载任务的完成情况。若任务已完成则返回True
    def checkCargoStatus(self):
        # 执行的任务是--卸载所有载货
        if self.actions[self.process][1] == ACTION.DischargeAll:
            if not self.master.isLoaded():  # 货物已经卸载完全
                self.process += 1
                time.sleep(0.3)
                window.closeWindow(window.WindowName.SHIPMENT)  # 关闭货物窗口
                return True
            else:
                return False
        # 执行的任务是--装载所有星球货物
        elif self.actions[self.process][1] == ACTION.LoadAll:
            self.master.choose()
            window.openWindow(window.WindowName.SHIPMENT)

            shipmentWindow, conts = shipmentInfo.shipmentPosition()
            res = shipmentInfo.devideInfo(shipmentWindow, conts, 'UP')
            if len(res) == 0:  # 已经全部装载
                self.process += 1
                time.sleep(0.3)
                window.closeWindow(window.WindowName.SHIPMENT)  # 关闭货物窗口
                return True
            else:
                return False

    # 执行当前任务,传入当前时间判断是否需要进行移动状态检查
    def act(self, time_):
        # 任务列表已经全部完成
        if self.actions[self.process][0] == 0:  # 以action == [0, 0]表示任务结束
            self.delete()
            return

        # 任务是--在贸易站提供货物容量
        if self.actions[self.process][1] == ACTION.Carrying:
            self.master.choose()
            window.openWindow(window.WindowName.SHIPMENT)
            self.master.loadAll()  # 装载星球上的全部货物

            shipmentWindow, conts = shipmentInfo.shipmentPosition()
            res = shipmentInfo.devideInfo(shipmentWindow, conts, 'UP')
            if len(res) > 0:  # 星球上有剩余货物，表明自身已经满载
                self.process += 1
                window.closeWindow(window.WindowName.SHIPMENT)  # 关闭货物窗口
            else:  # 任务还未完成
                window.closeWindow(window.WindowName.SHIPMENT)  # 关闭货物窗口
                return

        # 任务是--从底层装载货物，数量由第三个参数决定
        elif self.actions[self.process][1] == ACTION.Load_BOTTOM:
            if self.actions[self.process][0] == main.centerPlanet:  # 是要取走集货星球的曲道外货物
                if not main.took[main.centerPlanet]:  # 集货星球的曲道外货物还未被取走
                    main.took[main.centerPlanet] = True  # 记录自己取走了货物

                    # 获取集货星球的货物信息
                    shipments = main.getShipmentInfo(main.centerPlanet)
                    outer = 0  # 曲道外货物计数
                    for i in range(len(shipments) - 1, 0, -1):  # 倒序循环
                        if not main.isInner(shipments[i]):
                            outer += 1
                        else:
                            break

                    # 按指定数量取货
                    for i in range(outer):
                        self.master.load('BOTTOM')
                    # 插入新任务：将取到的货物移送至贸易站1003
                    self.actions.insert(self.process + 1, [1003, ACTION.Arriving, 25])
                    self.actions.insert(self.process + 2, [1003, ACTION.Carrying])

                self.process += 1

        # 任务是--装载所有货物
        elif self.actions[self.process][1] == ACTION.LoadAll:
            # 检查任务是否完成，完成则进入下一个任务阶段
            if self.checkCargoStatus():
                return
            # 任务还未完成
            # if self.master.isLoaded():  # 有载货则全卸掉
            #     self.master.dischargeAll()
            self.master.loadAll()  # 装载星球上的全部货物
            # 再次检查任务是否完成
            self.checkCargoStatus()

        # 任务是--卸载所有货物
        elif self.actions[self.process][1] == ACTION.DischargeAll:
            if self.actions[self.process][0] == main.centerPlanet:  # 是在集货星球卸货
                if main.discharge(self):  # 轮到自己卸货
                    self.master.dischargeAll()  # 一键卸货
                    # 判断是否卸掉了全部货物
                    if self.checkCargoStatus():  # 已全部卸载
                        main.pendingList.remove(self)  # 将自己从等待列表中删去

        # 任务是--到达某处
        elif self.actions[self.process][1] == ACTION.Arriving:
            if time_ < self.checkTime and self.checkTime > 0:  # 还未到检查时间
                return
            if self.checkTime > 0:
                print("检查是否到达目的地")
            else:
                print("启航去", self.actions[self.process][0])
            statement, destination = self.master.where()
            if statement == State.STOP:  # 现在处于停靠状态
                # 尚未出发
                if self.checkTime < 0:
                    self.master.choose()
                    pos, _ = Find.findPlanet(self.actions[self.process][0])
                    # 右键双击
                    window.RClick(pos)
                    time.sleep(0.3)
                    window.RClick(pos)
                    time.sleep(2)

                    # 设置下次检查时间
                    self.checkTime = time.time() + self.actions[self.process][2]
                # 已经移动到目标点
                else:
                    self.checkMovingStatus()
            elif statement == State.MOVING:  # 现在处于移动状态
                self.checkTime = time.time() + 5

        # 任务是--卸下顶层的货物，货物数量由第三个参数决定
        elif self.actions[self.process][1] == ACTION.Discharge_TOP:
            for i in range(0, self.actions[self.process][2]):  # 按照要求卸载相应个数的货物
                if main.shipmentCount[self.actions[self.process][0]] < 36:  # 卸货贸易站还未满载
                    main.shipmentCount[self.actions[self.process][0]] += 1  # 其载货增加1
                    self.master.discharge('TOP')
                else:
                    print(self.actions[self.process][0], "已满载，警告！")
                    break  # 停止卸货，剩下货物直接带去集货星球（待优化）
            # 任务已完成，进行到下一个任务
            self.process += 1

        # 任务是--从星球或贸易站装载部分顶层货物
        elif self.actions[self.process][1] == ACTION.Load_TOP:
            # 任务是取走贸易站的曲道内货物
            if self.actions[self.process][0] > 1000:
                if main.took[self.actions[self.process][0]]:  # 但贸易站的曲道内货物已经被取走
                    self.process += 1
                    return
                else:
                    main.took[self.actions[self.process][0]] = True  # 记录自己取走了贸易站的曲道内货物

            for i in range(0, self.actions[self.process][2]):  # 按照要求装载相应个数的货物
                main.shipmentCount[self.actions[self.process][0]] -= 1
                self.master.load()
            # 任务已完成，进行到下一个任务
            self.process += 1
            window.closeWindow(window.WindowName.SHIPMENT)  # 关闭货物窗口




# 调试用
if __name__ == '__main__':
    handle = win32gui.FindWindow(None, 'Hades\' Star')
    win32gui.SendMessage(handle, win32con.WM_SYSCOMMAND, win32con.SC_RESTORE, 0)  # 取消最小化
    win32gui.SetForegroundWindow(handle)  # 高亮显示在前端
    # 设置窗口大小/位置
    win32gui.SetWindowPos(handle, win32con.HWND_NOTOPMOST, 160, 50, 1600, 900, win32con.SWP_SHOWWINDOW)
    time.sleep(0.3)

    _, (x, y, _, _) = shipmentInfo.getShipmentWindow()  # 获取货物窗口的位置
    win32api.SetCursorPos((x + 80, y + 330))

    # # 本段可用于截图保存信息窗口的名字图像模板
    # img, _ = window.ScreenShot()
    # gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)  # 转换为灰度图
    # infoWindow = gray[710:, 525:875]  # 截取信息窗口图像
    # h = infoWindow[35:48, 50:90]
    # _, h = cv2.threshold(h, 120, 255, cv2.THRESH_BINARY)
    # cv2.imwrite('Pictures/info16.PNG', h)
    # window.imshow(h)



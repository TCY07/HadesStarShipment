
# 这是主程序

import time
import cv2
import numpy as np
import win32gui, win32api, win32con
import window
import Find
import shipmentInfo
import cargoShip
import data


# 读取某星球当前货物信息列表
def getShipmentInfo(name):
    pos, _ = Find.findPlanet(name)
    window.LClick(pos)

    # 取消了所有货船的选中状态
    for item in cargoShip.Ship.ships.values():
        item.chosen = False

    window.openWindow(window.WindowName.SHIPMENT)
    time.sleep(0.2)
    shipments = shipmentInfo.getPlanetShipment()  # 得到货物信息列表
    window.closeWindow(window.WindowName.SHIPMENT)
    return shipments


# 判断货物是否以曲道内星球(集货星球除外)为目的地
def isInner(name):
    if name in data.outerPlanet or name == data.centerPlanet or name > 1000:
        return False
    else:
        return True


# 集中曲道外星球上的货物
def gatherOuter():
    # 统计两个贸易站的货物信息
    cargo1002 = getShipmentInfo(1002)
    cargo1003 = getShipmentInfo(1003)
    data.shipmentCount[1002] = len(cargo1002)
    data.shipmentCount[1003] = len(cargo1003)

    inner = {1002: 0, 1003: 0}  # 贸易站的曲道内的货物计数
    for i in range(len(cargo1002)):
        if isInner(cargo1002[i]):
            inner[1002] += 1
        else:
            break
    for i in range(len(cargo1003)):
        if isInner(cargo1003[i]):
            inner[1003] += 1
        else:
            break

    for planet in data.outerPlanet:
        # 读取该星球的货物信息
        shipments = getShipmentInfo(planet)
        if len(shipments) == 0:  # 星球上无货物
            continue  # 进行下一个星球

        # 星球上有货物
        center2 = center3 = 0  # 到两个贸易站的货物计数
        outer = 0  # 曲道外货物计数
        for i in range(len(shipments) - 1, 0, -1):  # 倒序循环
            if shipments[i] == 1002:
                center2 += 1
                outer += 1
            elif shipments[i] == 1003:
                center3 += 1
                outer += 1
            elif not isInner(shipments[i]):
                outer += 1
            else:
                break

        # 判断该去哪个贸易站卸货，并计算卸货个数
        if center2 < center3:
            dropStation = 1002
            outer -= center2
        else:
            dropStation = 1003
            outer -= center3

        for ship in cargoShip.Ship.ships.values():
            # 此货船停靠在该曲道外星球上
            if ship.statement == cargoShip.State.STOP and ship.destination == planet:
                # 创建任务
                m = [
                    [planet, cargoShip.ACTION.LoadAll],
                    [dropStation, cargoShip.ACTION.Arriving, 35],
                    [dropStation, cargoShip.ACTION.Discharge_TOP, outer],
                    [dropStation, cargoShip.ACTION.Load_TOP, inner[dropStation]],  # 取走贸易站的曲道内货物
                    [data.centerPlanet, cargoShip.ACTION.Arriving, 25],
                    [data.centerPlanet, cargoShip.ACTION.DischargeAll],
                    [data.centerPlanet, cargoShip.ACTION.Load_BOTTOM, -1],  # 第三个参数待真正执行时再设置
                    [0, 0]  # 任务结束
                ]
                # 排入任务列表
                mission = cargoShip.Mission(ship, m)
                del m
                # 启航
                mission.act(time.time())
                break  # 进行下一个曲道外星球


# 在集货星球依次卸货。输入任务，判断是否轮到该货船卸货
def discharge(mission):
    if mission not in data.pendingList:  # 该任务还未进入等待列表
        data.pendingList.append(mission)

    # 判断是否轮到该任务执行卸货任务（排第一个的任务才执行）
    if mission == data.pendingList[0]:
        return True
    else:
        return False


# 第一轮计算机加成的三种主要路线
route = [
    [2003, 11, 12, 9, 6, 1, 2],  # 左
    [2003, 13, 14, 15, 3, 2, 1],  # 右
    # [2003, 101, 102, 201, 301]  # 中
]


# 第一轮计算机加成，加成集货星球的货物_第一步：主要航线取货
def buffCenterShipment_1():
    c = 0
    for ship in cargoShip.Ship.ships.values():
        if ship.hasMission:
            continue
        # 是空闲货船
        # 创建任务
        if c < len(route):
            m = [
                [data.centerPlanet, cargoShip.ACTION.Passing, 0, route[c]],  # 经过集货星球进行计算机加成
                [2003, cargoShip.ACTION.Cancel],  # 取消航线
                [2003, cargoShip.ACTION.Passing, 0, [data.centerPlanet]],  # 经过曲道枢纽
                [data.centerPlanet, cargoShip.ACTION.Arriving, 5],  # 停靠集货星球
                [data.centerPlanet, cargoShip.ACTION.DischargeAll],  # 卸载所有货物
                [0, 0]
            ]
            # 排入任务列表
            mission = cargoShip.Mission(ship, m)
            # 删除列表，否则会使所有货船共用一个任务列表
            del m
            # 启航
            mission.act(time.time())
            c += 1
        else:  # 主要航线已经设置完毕
            break


# 暂停程序以及恢复运行
def pauseAndResume():
    pos = win32gui.GetCursorPos()
    if pos[0] > 1900:  # 鼠标贴在右边
        print("程序暂停中。。。")
        while pos[0] > 20:
            pos = win32gui.GetCursorPos()
        print("程序恢复运行。")


if __name__ == '__main__':
    # 初始化游戏窗口
    handle = window.Init('Hades\' Star')
    # window.savePlanetLocation()
    window.getPlanetLocation()

    # 初始化货船信息
    for num in range(data.shipCount):
        cargoShip.Ship(num)
    # 取消所有货船的选中状态
    window.KeyDown('esc')
    for item in cargoShip.Ship.ships.values():
        item.chosen = False

    # # 测试
    # m = [
    #     [data.centerPlanet, cargoShip.ACTION.Load_BOTTOM, 15],
    #     [0, 0]
    # ]
    # mis = cargoShip.Mission(cargoShip.Ship.ships[2], m)
    # mis.act(time.time())
    # exit(0)

    if data.outerClear is False:  # 初始时曲道外星球上有货物
        # 第一轮集货
        gatherOuter()  # （注意：现要求曲道外各星球均有货船停靠）

    # 遍历任务列表并执行--当前任务：收集曲道外星球上的货物
    while len(cargoShip.Mission.missions) > 0 and len(data.pendingList) == 0:  # 进入下一步的条件：所有任务都已做完或者集货星球已满
        pauseAndResume()
        for m in cargoShip.Mission.missions:
            m.act(time.time())
    print("第一阶段任务完成")

    # 主要航线设置
    buffCenterShipment_1()
    # 遍历任务列表并执行--当前任务：计算机加成集货星球货物
    while len(cargoShip.Mission.missions) > 0:  # 进入下一步的条件：所有任务都已做完或者集货星球已满
        pauseAndResume()
        for m in cargoShip.Mission.missions:
            m.act(time.time())

    # # 创建测试任务
    # m = [
    #     [0, 0]
    # ]
    # # 排入任务列表
    # cargoShip.Ship(5)
    # cargoShip.Mission(cargoShip.Ship.ships[5], m)
    #
    # while len(cargoShip.Mission.missions) > 0:
    #     for m in cargoShip.Mission.missions:
    #         m.act(time.time())


# ————初始化————
# 获取视野位置、视野缩放大小
# 读取星球上货物信息
# 读取货船信息

# ————第一轮集货————
# 货船：无曲道星球(装载：全部货物)-指定贸易站(卸载：曲道外货物)(装载：曲道内货物)-集货星球
# "停靠集货星球"货船：(卸载：全部货物)-直到集货星球满载

# ————第一轮计算机加成————
# "空闲"货船:当前停靠点-集货星球-暂停点-曲道内星球-...
# "货物已加成"货船:清除所有航线-设置返回集货星球
# "停靠集货星球,货物未加成"货船：(卸载：全部货物)-直到集货星球满载
# 第一轮货物全部加成完毕后:"停靠集货星球"货船:(卸载:全部货物)-直到集货星球满载

# ————第二轮集货(同时加成)————
# "空闲"货船:当前停靠点-取货星球-暂停点-曲道内星球
# "货物已加成"货船:清除所有航线-指定贸易站(卸载:曲道外货物)-集货星球
# "停靠集货星球,货物未加成"货船：(卸载：全部货物)-直到集货星球满载

# ————释放无人机————
# "停靠集货星球,货物未加成"货船：(卸载：全部货物)-直到集货星球满载
# "空闲"货船:当前停靠点-取货星球-暂停点-曲道内星球

# ————第三轮集货————
# "空闲"货船:当前停靠点-取货星球(装载:所有货物)-贸易站1/2


# 这是主程序

import time
import cv2
import numpy as np
import win32gui, win32api, win32con
import window
import Find
import shipmentInfo
import cargoShip


# 空闲货船列表
avaShips = []
# 曲道外星球列表
outerPlanet = [4, 5, 7, 8, 10]
# 集货星球
centerPlanet = 16

# 各类参数
shipCount = 8  # 货船数量
outerClear = False  # 初始状态时，曲道外星球是否已人工清空


# 点击指定的星球,i用来区分左右击
def clickPlanet(num, i):
    pos, _ = Find.findPlanet(num)
    if i == 0:  # 左键
        window.LClick(pos)
    elif i == 1:  # 右键
        window.RClick(pos)


# 获取空闲(停靠+无货物)货船的列表，返回空闲货船个数
# def getAvailable():
#     avaShips.clear()
#     count = 0
#     for ship in ships.values():
#         ship.where()
#         if ship.statement == cargoShip.State.MOVING:  # 非停靠状态
#             continue
#         if ship.isLoaded():  # 有载货
#             continue
#         avaShips.append(ship)
#         count += 1
#     return  count


# 集中曲道外星球上的货物
def gatherOuter():
    for planet in outerPlanet:
        for ship in cargoShip.Ship.ships.values():
            # 此货船停靠在该曲道外星球上
            if ship.statement == cargoShip.State.STOP_PLANET and ship.destination == planet:
                    if ship.isLoaded():  # 有载货则全卸掉
                        ship.dischargeAll()
                    ship.loadAll()  # 装载星球上的全部货物
                    # clickPlanet(centerPlanet, 1)  # 前往集货星球
                    break  # 前进到下一个曲道外星球


if __name__ == '__main__':
    # 初始化游戏窗口
    handle = window.Init('Hades\' Star')
    # window.savePlanetLocation()
    window.getPlanetLocation()
    for num in range(1, 17):
        pos, _ = Find.findPlanet(num)
        window.LClick(pos)
    exit(0)
    # 初始化货船信息
    for num in range(0, shipCount):
        cargoShip.Ship(num)
    # print(cargoShip.Ship.ships)

    if outerClear is False:  # 初始时曲道外星球上有货物
        # 集中曲道外星球上的货物
        gatherOuter()  # 注意：现要求曲道外各星球均有货船停靠





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

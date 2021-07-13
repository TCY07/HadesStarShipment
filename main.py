
# 这是主程序

import time
import cv2
import numpy as np
import win32gui, win32api, win32con
import window
import Find
import shipmentInfo
import cargoShip


# 计时器
TIME = 0
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


# 集中曲道外星球上的货物
def gatherOuter():
    for planet in outerPlanet:
        for ship in cargoShip.Ship.ships.values():
            # 此货船停靠在该曲道外星球上
            if ship.statement == cargoShip.State.STOP and ship.destination == planet:
                # 创建任务
                m = [
                    [planet, cargoShip.ACTION.LoadAll],
                    [1003, cargoShip.ACTION.Arriving],
                    [1003, cargoShip.ACTION.DischargeOuter_TOP],
                    [centerPlanet, cargoShip.ACTION.DischargeAll]
                ]
                # 进入任务列表
                cargoShip.Mission(ship, m)


if __name__ == '__main__':
    # 初始化游戏窗口
    handle = window.Init('Hades\' Star')
    # window.savePlanetLocation()
    window.getPlanetLocation()
    # 初始化货船信息
    for num in range(1, 2):
        cargoShip.Ship(num)

    if outerClear is False:  # 初始时曲道外星球上有货物
        # 创建任务列表：集中曲道外星球上的货物
        gatherOuter()  # （注意：现要求曲道外各星球均有货船停靠）
    # 遍历任务列表并执行
    while True:
        for m in cargoShip.Mission.missions:
            m.act(time.time())





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

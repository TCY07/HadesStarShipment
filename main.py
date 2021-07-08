
# 这是主程序

import time
import cv2
import numpy as np
import win32gui
import win32api
import win32con
import window
import Find


if __name__ == '__main__':
    # 初始化游戏窗口
    handle = window.Init('Hades\' Star')

    pos = Find.findMoon(101)
    win32api.SetCursorPos(pos)

    # for num in range(15, 17):
    #     pos = Find.findPlanet(num, 0)
    #     win32api.SetCursorPos(pos)
        # window.Roll(1, 8)
        # window.RClick(pos)
        # window.KeyDown('esc')
        # time.sleep(0.01)

    # while 1:
    #     locate = window.sunPosition(handle)
    #     print(locate)
    #     window.Relocate((0, 0, 10))

    # time.sleep(1)
    # img = window.ScreenShot(handle)
    # img2 = img.copy()
    #
    # for num in range(1, 17):
    #     loc = Find.Find(num, img, -0.30)
    #     filename = 'Pictures/' + str(num) + '.PNG'
    #     target = cv2.imread(filename)
    #     for pt in zip(*loc[::-1]):
    #         bottom_right = (pt[0] + target.shape[1], pt[1] + target.shape[0])
    #         cv2.rectangle(img2, pt, bottom_right, (255, 255, 255), 2)
    #
    # window.imshow(img2)



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

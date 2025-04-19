# import sensor,image,lcd,math,time,pyb
# from pyb import UART
# import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,lidar
# import binascii
# import framebuf

from models import *

import math
# timer.start(1)
PI = 3.14159265 #//定义π常量  用PI是3.14


def LidarPos():
    iJumpSample = 18
    iSampleNumber = 20
    lOutData = [[],[]]
    for _ in range(iSampleNumber*iJumpSample):
        lRawData=lidar.read()
        for i in range(int(40/iJumpSample)):
            lOutData[0].append(lRawData[0][int(i*iJumpSample)])
            lOutData[1].append(lRawData[1][int(i*iJumpSample)])
    print(len(lOutData[0]))
    lRawDists = [[],[],[],[]]
    lOutDists = []
    for i in range(iSampleNumber):
        # x方向 sin 270-90
        if 90 < lRawData[0][i] < 270:
            lRawDists[0].append(int(lOutData[1][i]*math.cos(lOutData[0][i]*PI/180)))
        else:
            lRawDists[2].append(int(lOutData[1][i]*math.cos(lOutData[0][i]*PI/180)))
        # y方向 sin 0-180
        if 0 < lRawData[0][i] < 180:
            lRawDists[1].append(int(lOutData[1][i]*math.sin(lOutData[0][i]*PI/180)))
        else:
            lRawDists[3].append(int(lOutData[1][i]*math.sin(lOutData[0][i]*PI/180)))

    for l in lRawDists:
        iOut = 0
        iDist = 0
        for i in l:
            iOut = iOut + i**2
            print(i)
        iDist = int((iOut/40)**0.5)
        lOutDists.append(iDist)
    return lOutDists

if __name__ == "__main__":
    # while True:
        print(LidarPos())


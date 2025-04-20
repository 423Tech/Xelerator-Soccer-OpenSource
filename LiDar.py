# import sensor,image,lcd,math,time,pyb
# from pyb import UART
# import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,lidar
# import binascii
# import framebuf

from models import *

import math


def LidarPos():
    iJumpSample = 10
    iSampleNumber = 6
    angle = 20*iSampleNumber
    print(angle)
    lRawDists = [[],[],[],[]]
    lOutData = [[],[]]
    lOutDists = []
    for _ in range(iSampleNumber):
        lRawData=lidar.read()
        for i in range(int(40/iJumpSample)):
            lOutData[0].append(lRawData[0][int(i*iJumpSample)])
            lOutData[1].append(lRawData[1][int(i*iJumpSample)])
    for i in range(int(40/iJumpSample)*iSampleNumber):
        # y方向 sin 270-90
        if 90 < lOutData[0][i] < 270:
            lRawDists[0].append(lOutData[1][i]*math.cos(math.radians(lOutData[0][i])))
        else:
            lRawDists[2].append(lOutData[1][i]*math.cos(math.radians(lOutData[0][i])))
        # x方向 sin 0-180
        if 0 < lOutData[0][i] < 180:
            lRawDists[1].append(lOutData[1][i]*math.sin(math.radians(lOutData[0][i])))
        else:
            lRawDists[3].append(lOutData[1][i]*math.sin(math.radians(lOutData[0][i])))

    for l in lRawDists:
        iOut = 0
        iDist = 0
        for i in l:
            iOut = iOut + i**2
            # print(i)
        iDist = int((iOut/40)**0.5)
        lOutDists.append(iDist)
    return lOutDists

if __name__ == "__main__":
    # while True:
        print(LidarPos())


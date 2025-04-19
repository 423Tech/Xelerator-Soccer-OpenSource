# import sensor,image,lcd,math,time,pyb
# from pyb import UART
# import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,lidar
# import binascii
# import framebuf

from models import *

import math
# timer.start(1)
PI = 3.14159265 #//定义π常量  用PI是3.14

def LidarPlus():
	lOutData = [[],[]]
	for i in range(0,6):
		lRawData1=Lidar.read()
		for i in range(0,40):
			lOutData[0].append(lRawData1[0][int(i)])
			lOutData[1].append(lRawData1[1][int(i)])
		delay.us(1)
	# while (timer.read(1) <= 500):
	# 	delay.ms(1)
	# lRawData2=lidar.read()
	# timer.clear(1)
	# timer.start(1)
	# print(timer.read(1))
	# for l in range(20):
	# 	lOutData[0].append(lRawData1[0][2*l-1])
	# 	lOutData[1].append(lRawData1[1][2*l-1])
	# 	lOutData[0].append(lRawData2[0][2*l-1])
	# 	lOutData[1].append(lRawData2[1][2*l-1])
	return lOutData

	

def LidarPos():
    lRawData=LidarPlus()
    # lRawData=lidar.read()
    lRawDists = [[],[],[],[]]
    lOutDists = []
    for i in range(240):
        # x方向 sin 270-90
        if 90 < lRawData[0][i] < 270:
            lRawDists[0].append(int(lRawData[1][i]*math.cos(lRawData[0][i]*PI/180)))
        else:
            lRawDists[2].append(int(lRawData[1][i]*math.cos(lRawData[0][i]*PI/180)))
        # y方向 sin 0-180
        if 0 < lRawData[0][i] < 180:
            lRawDists[1].append(int(lRawData[1][i]*math.sin(lRawData[0][i]*PI/180)))
        else:
            lRawDists[3].append(int(lRawData[1][i]*math.sin(lRawData[0][i]*PI/180)))
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


# from LunaPre import *

Cache = False
##BallX, BallY 获取[球]相对于[机器几何中心]的距离
# p =Positions()
from utils.IceLoongBits import IceLoongBits
from chassis import Car, Peripherals, Key # Universal-Movement-Standard

Bits = IceLoongBits()
chassis = Car(Bits.SetWheelSpeed,Bits.GetYaw)

try:
    '''
    ball = Positions().AbsBallDistance()
    rob = Positions()._UpdateAbsRoboPosition()
    XXX=ball[0]
    YYY=ball[1]
    XX=rob[0]
    YY=rob[1]
    '''
    '''   
    if(XXX<0 and YY>0):
        chassis.AbsMoveVetor(XXX-10,YY-10,0)
        chassis.AbsMoveVetor(XXX-10,YYY,0)
        chassis.AbsMoveVetor(XXX,YYY,0)
    '''

        # print(rob[1])
    while(1):
        chassis.AbsMoveAngle(0,0,-100)
    #     time.sleep(5)
        # chassis.AbsMoveVetor(0,-20,0)
    #     time.sleep(5)
    #     chassis.AbsMoveVetor(-20,0,0)
    #     time.sleep(5)
    #     chassis.AbsMoveVetor(-0,-20,0)
    #     time.sleep(5)

except Exception as e:
    raise e
finally:
    chassis.stop()
    # lidar.stop()
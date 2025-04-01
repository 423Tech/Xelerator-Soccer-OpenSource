import sensor,image,lcd,math,time,pyb
from pyb import UART
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led
import binascii
import framebuf

from cfg import QkJson

cfg = QkJson()

def GoV(iFacingAngle,iAimAngle,iSpeed):
    iGlobalPIDK = 2
    iCMP = compass.read()
    iSpeedX = int(math.sin(math.radians(iAimAngle)) * iSpeed)
    iSpeedY = int(math.cos(math.radians(iAimAngle)) * iSpeed)

    iSpeedU = iSpeedX + iSpeedY
    iSpeedV = iSpeedY - iSpeedX
    iDeltaAngle = iCMP-iFacingAngle
    if iDeltaAngle > 180:
        iDeltaAngle = iDeltaAngle - 360
    set_motor.RPM(iSpeedU - iDeltaAngle * iGlobalPIDK,iSpeedV - iDeltaAngle * iGlobalPIDK,iSpeedV + iDeltaAngle * iGlobalPIDK,iSpeedU + iDeltaAngle * iGlobalPIDK)

def getDists(Num: int) -> list[int,int,int]:
    lDists = []
    for i in range(Num):
        # lDists.append(set_adc.read(i))
        lDists.append(
            int(set_adc.read(cfg.read("Tofs",str(i)))*cfg.read("Tofs","K")+cfg.read("Tofs","B"))
            )
    return lDists

def GetPos() -> list[int,int]:
    Distance = getDists(4)
    if Distance[0]+Distance[2] < cfg.read("Position","Height") - 100:
        if Distance[0] > Distance[2]:
            Y = cfg.read("Position","Height")/2 - Distance[0]
        else:
            Y = cfg.read("Position","Height")/2 - Distance[2]
    else:
        Y = ((cfg.read("Position","Height")/2 - Distance[0]) + (cfg.read("Position","Height")/2 - Distance[2]))/2
    if Distance[1]+Distance[3] < cfg.read("Position","Width") - 100:
        if Distance[0] > Distance[2]:
            X = cfg.read("Position","Width")/2 - Distance[1]
        else:
            X = cfg.read("Position","Width")/2 - Distance[3]
    else:
        X = ((cfg.read("Position","Width")/2 - Distance[1]) + (cfg.read("Position","Width")/2 - Distance[3]))/2

    return [X,Y]

def AimPos(iAimX:int,iAimY:int,) -> int:
    iSelfX = GetPos()[0]
    iSelfY = GetPos()[1]
    iDeltaX = iSelfX - iAimX
    iDeltaY = iSelfY - iAimY
    if iDeltaX > 0:
        
        pass#right
    elif iDeltaX < 0:
        pass#left
    else:
        pass
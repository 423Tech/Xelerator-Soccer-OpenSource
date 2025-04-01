# A2O.py | RCJ Version 0.0.2(2025032800) Developer 423

import sensor,image,lcd,math,time,pyb
from pyb import UART
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led
import binascii
import framebuf


clock = time.clock()

from cfg import QkJson
Cfg = QkJson()

def getadc():
    global iTof1,iTof0,iTof3,iTof2,dhl,dhb,dhr,bx,by
    bx = set_adc.read(11)
    by = set_adc.read(12)
    iTof0 = int(set_adc.read(Cfg.read("Tofs","0"))/3.5)
    iTof1 = int(set_adc.read(Cfg.read("Tofs","1"))/3.5)
    iTof2 = int(set_adc.read(Cfg.read("Tofs","2"))/3.5)
    iTof3 = int(set_adc.read(Cfg.read("Tofs","3"))/3.5)


iNumOfDist = Cfg.read("A2AOb","NumOfDist")
iMaxLife = Cfg.read("A2AOb","LifeTime")
iMemoLife = iMaxLife
bLife = False
lBlockedMemo = []
lStatusOfDist = []

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
        lDists.append(set_adc.read(Cfg.read("Tofs",str(i))))
    print(lDists)
    return lDists
    
def ObtDetect():
    global lBlockedMemo,lStatusOfDist,iMemoLife,bLife
    lDists = getDists(iNumOfDist)
    if len(lStatusOfDist) < iNumOfDist:
        for d in range(iNumOfDist):
            lStatusOfDist.append(True)
    for i in range(iNumOfDist):
        if lStatusOfDist[i] and lDists[i] <= Cfg.read("A2AOb","ActiveRange"):
            lStatusOfDist[i] = False
            iMemoLife = iMaxLife
            lBlockedMemo.append(i)
            if len(lBlockedMemo) > (iNumOfDist - 1):
                lStatusOfDist[lBlockedMemo[0]] = True
                lBlockedMemo.pop(0)
            bLife = False
        if not lStatusOfDist[i] and lDists[i] >= Cfg.read("A2AOb","IgnoreRange"):
            bLife = True
        else:
            bLife = False
    if bLife:
        if len(lBlockedMemo) > 0 and iMemoLife > 0:
            iMemoLife = iMemoLife - 1
            if iMemoLife == 0:
                lStatusOfDist[lBlockedMemo[0]] = True
                lBlockedMemo.pop(0)
                iMemoLife = iMaxLife
        if len(lStatusOfDist) == 0:
            iMemoLife = iMaxLife
        bLife = False


def find_nearest_element(arr, target):
    return min(arr, key=lambda x: abs(x - target))

    
def AvoidObt(iFacingAngle: int) -> None:
    ObtDetect()
    lAvailbeAngles = []
    lBlockedAngles = []
    iPerAngle = int(359/iNumOfDist)
    #获取挡住/被挡住的角度
    for i in range(iNumOfDist):
        if lStatusOfDist[i]:
            lAvailbeAngles.append(i*iPerAngle)
        else:
            lBlockedAngles.append(i*iPerAngle)
   #判断
    if len(lBlockedAngles) == 3:#被挡住三个
        if lAvailbeAngles[0] == 89:
            lAvailbeAngles[0] = lAvailbeAngles + 180
        iAimAngle = lAvailbeAngles[0]
    elif len(lBlockedAngles) == 2:#被挡住两个
        iAimAngle = find_nearest_element(lAvailbeAngles,iFacingAngle)
    elif len(lBlockedAngles) == 1:#被挡住一个
        iAimAngle = lBlockedAngles[0] + 180
        if iAimAngle > 360:
            iAimAngle = iAimAngle - 360
        else:
            iAimAngle = iAimAngle
    else:
        # iAimAngle = iFacingAngle
        return 0
    GoV(iFacingAngle,iAimAngle,150)
    # car.z_move(iFacingAngle,iAimAngle,200)  
    print(lAvailbeAngles[0])


while(key.read() == 0):
    print(getDists(4))

while(True):
    AvoidObt(0)
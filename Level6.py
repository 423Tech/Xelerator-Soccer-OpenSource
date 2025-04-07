import sensor,image,lcd,math,time,pyb
from pyb import UART
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led
import binascii
import framebuf


# config.py | RCJ Version 1.0.2(2025032800) Developer 423
import ujson
import os
CONFIG_FILE = "./cfg.json"
class QkJson:
    def __init__(self):
        try:
            os.stat(CONFIG_FILE)
        except:
            data = {
                "model": {
                    "number" : 1,
                    "type": "Off",
                },
                "Tofs": {
                    0: 1,
                    1: 2,
                    2: 3,
                    3: 4,
                    "K": 0.67,
                    "B": 4,
                    },
                "A2AOb": {
                    "ActiveRange": 30,
                    "IgnoreRange": 40,
                    "NumOfDist" : 4,
                    "LifeTime" : 3,
                },
                "Border" : {
                    "0": 20,
                    "1": 30,
                    "2": 20,
                    "3": 30,
                },
                "Position" : {
                    "Width": 1800,
                    "Height": 2400,
                },
                "Advanced": {
                    "Cover2Start": False,
                }
            }
            with open(CONFIG_FILE, "w") as f:
                ujson.dump(data, f)
        with open(CONFIG_FILE) as f:
            self.cfg = ujson.load(f)

    def write(self, section: str, option: str, value: int) -> int:
        self.cfg[section][option] = value
        with open(CONFIG_FILE, "w") as f:
            ujson.dump(self.cfg, f)

    def read(self, section: str, option: str) -> int:
        return self.cfg[section][option]

cfg = QkJson()


#Values
bLife = False
lBlockedMemo = []
lStatusOfDist = []


#Math Mod
def FindNearstAngle(arr, target):
    return min(arr, key=lambda x: abs(x - target))


#Move Mod
def GoV(iFacingAngle,iAimAngle,iSpeed):
    iFacingAngle = int(iFacingAngle)
    iAimAngle = int(iAimAngle)
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

def Go2(iFacingAngle,iSpeedX,iSpeedY):
    iGlobalPIDK = 2
    iCMP = compass.read()
    iSpeedU = int(iSpeedX + iSpeedY)
    iSpeedV = int(iSpeedY - iSpeedX)
    iDeltaAngle = iCMP-iFacingAngle
    if iDeltaAngle > 180:
        iDeltaAngle = iDeltaAngle - 360
    set_motor.RPM(iSpeedU - iDeltaAngle * iGlobalPIDK,iSpeedV - iDeltaAngle * iGlobalPIDK,iSpeedV + iDeltaAngle * iGlobalPIDK,iSpeedU + iDeltaAngle * iGlobalPIDK)



#Value Mod
def GetDists(Num: int) -> list[int,int,int]:
    lDists = []
    for i in range(Num):
        # lDists.append(set_adc.read(i))
        lDists.append(
            int(set_adc.read(cfg.read("Tofs",str(i)))*cfg.read("Tofs","K")+cfg.read("Tofs","B"))
            )
    return lDists

def GetPos() -> list[int,int]:
    Distance = GetDists(cfg.read("A2AOb","NumOfDist"))
    if Distance[0]+Distance[2] < cfg.read("Position","Height") - 50:
        if Distance[0] > Distance[2]:
            Y = cfg.read("Position","Height")/2 - Distance[0] -4
        else:
            Y = Distance[2] - cfg.read("Position","Height")/2 + 4
    else:
        Y = ((cfg.read("Position","Height")/2 - Distance[0]) + (Distance[2] - cfg.read("Position","Height")/2))/2
    if Distance[1]+Distance[3] < cfg.read("Position","Width") - 50:
        if Distance[1] > Distance[3]:
            X = -(cfg.read("Position","Width")/2 - Distance[1] - 4)
        else:
            X = -(Distance[3] - cfg.read("Position","Width")/2 + 4)
    else:
        X = -((cfg.read("Position","Width")/2 - Distance[1]) + (Distance[3] - cfg.read("Position","Width")/2))/2
    return [X,Y]

def AvoidOutBorder():
    lAvailbeAngles = []
    lBlockedAngles = []
    Dists = GetDists("A2AOb","NumOfDist")
    iNumOfDist = cfg.read("A2AOb","NumOfDist")
    iPerAngle = int(359/iNumOfDist)
    for i in range(iNumOfDist):
        if i < iNumOfDist/2:#左半部分
            if lStatusOfDist[i]:
                lAvailbeAngles.append(-i*iPerAngle)
            else:
                lBlockedAngles.append(-i*iPerAngle)
        else:#右半部分
            if lStatusOfDist[1]:
                lAvailbeAngles.append((i-iNumOfDist+1)*iPerAngle)
            else:
                lBlockedAngles.append((i-iNumOfDist+1)*iPerAngle)          
    for d in Dists:
        if d < cfg.read("Border",str(d)):  
            pass


def ObtDetect():
    global lBlockedMemo,lStatusOfDist,iMemoLife,bLife
    iNumOfDist = cfg.read("A2AOb","NumOfDist")
    iMaxLife = cfg.read("A2AOb","LifeTime")
    lDists = GetDists(iNumOfDist)
    if len(lStatusOfDist) < iNumOfDist:
        for d in range(iNumOfDist):
            lStatusOfDist.append(True)
    for i in range(iNumOfDist):
        if lDists[i] <= cfg.read("A2AOb","ActiveRange"):
        # if lStatusOfDist[i] and lDists[i] <= cfg.read("A2AOb","ActiveRange"):
            lStatusOfDist[i] = False
            # iMemoLife = iMaxLife
            # lBlockedMemo.append(i)
            # if len(lBlockedMemo) > (iNumOfDist - 1):
            #     lStatusOfDist[lBlockedMemo[0]] = True
            #     lBlockedMemo.pop(0)
            # bLife = False
        # if lDists[i] >= cfg.read("A2AOb","IgnoreRange"):
        # # if not lStatusOfDist[i] and lDists[i] >= cfg.read("A2AOb","IgnoreRange"):
        #     bLife = True
        else:
            lStatusOfDist[i] = True
            # bLife = True
    # if bLife:
    #     if len(lBlockedMemo) > 0 and iMemoLife > 0:
    #         iMemoLife = iMemoLife - 1
    #         if iMemoLife == 0:
    #             lStatusOfDist[lBlockedMemo[0]] = True
    #             lBlockedMemo.pop(0)
    #             iMemoLife = iMaxLife
    #     if len(lBlockedMemo) == 0:
    #         iMemoLife = iMaxLife
    #     bLife = False

    
def AvoidObt(iFacingAngle: int,iTargetAngle:int) -> None:
    iTargetAngle = -iTargetAngle
    ObtDetect()
    lAvailbeAngles = []
    lBlockedAngles = []
    iNumOfDist = cfg.read("A2AOb","NumOfDist")
    iPerAngle = int(359/iNumOfDist)
    #获取挡住/被挡住的角度
    for i in range(iNumOfDist):
        if i < iNumOfDist/2:#左半部分
            if lStatusOfDist[i]:
                lAvailbeAngles.append(-i*iPerAngle-1)
            else:
                lBlockedAngles.append(-i*iPerAngle-1)
        else:#右半部分
            if lStatusOfDist[i]:
                lAvailbeAngles.append((abs(i-iNumOfDist))*iPerAngle+1)
            else:
                lBlockedAngles.append((abs(i-iNumOfDist))*iPerAngle+1)
   #判断
    if len(lBlockedAngles) == 3:#被挡住三个
        iAimAngle = lAvailbeAngles[0]
        GoV(iFacingAngle,iAimAngle,100)
    elif len(lBlockedAngles) <= 2:#被挡住两个
        iAimAngle = FindNearstAngle(lAvailbeAngles,iTargetAngle)
        GoV(iFacingAngle,iAimAngle,200)
    else:
        car.stop()
    # print(iAimAngle)
    print(iTargetAngle)
    # car.z_move(iFacingAngle,iAimAngle,200)


def Pos2Angle(lAimPos:list[int,int]) -> int:
    iAimX = lAimPos[0]
    iAimY = lAimPos[1]
    iLocX = GetPos()[0]
    iLocY = GetPos()[1]
    iDeltaX = iAimX - iLocX
    iDeltaY = iAimY - iLocY
    try:
        iDeltaAngle = -math.degrees(math.atan(iDeltaX/iDeltaY))
    except:
        if iDeltaX > 0:
            iDeltaAngle = -90
        else:
            iDeltaAngle = 90
    return int(iDeltaAngle)

def Pos2Pos(iFacingAngle,lAimPos:list[int,int], A2O:bool) -> int:
    iAimX = lAimPos[0]
    iAimY = lAimPos[1]
    iLocX = GetPos()[0]
    iLocY = GetPos()[1]
    iDeltaX = iAimX - iLocX
    iDeltaY = iAimY - iLocY
    if A2O:
        if 5 > iDeltaX > -5 and 5 > iDeltaY > -5:
            car.stop()
        else:
            # print(lAimPos)
            # print(Pos2Angle(lAimPos))
            if 0 > iDeltaX:
                PA = Pos2Angle(lAimPos) + 180
            else:
                PA = Pos2Angle(lAimPos)
            if 0 > iDeltaY:
                PA = Pos2Angle(lAimPos) - 180
            AvoidObt(iFacingAngle,PA)
    else:
        if iDeltaX > 500:
            iDeltaX = iDeltaX/5
        if iDeltaY > 500:
            iDeltaY = iDeltaY/5
        if iDeltaX < 100:
            iDeltaX = iDeltaX*5
        if iDeltaY < 100:
            iDeltaY = iDeltaY*5
        Go2(iFacingAngle,iDeltaX,iDeltaY)



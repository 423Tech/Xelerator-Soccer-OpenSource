import sensor,image,lcd,math,time,pyb
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,lidar
import binascii
import framebuf

set_io.out(15,1)

# config.py | RCJ Version 1.8.0(2025042300) Developer 423
import ujson
import os
CONFIG_FILE = "./cfg.json"
CACHE_FILE = "./cfg.cache.json"
class QkJson:
    def __init__(self):
        data = {
                "model": {
                    "number" : 1,
                    "type": "Off",
                },
                "Tofs": {
                    "On": True,
                    0: 1,
                    1: 2,
                    2: 3,
                    3: 4,
                    "K": 0.67,
                    "B": 4,
                    },
                "A2AOb": {
                    "ActiveRange": 30,
                    "IgnoreRange": 30,
                    "NumOfDist" : 4,
                    "LifeTime" : 3,
                },
                "Border" : {
                    "0": [60,95],
                    "1": [40,85],
                },
                "Position" : {
                    "ErrorRange": 20,
                    "Width": 180,
                    "Height": 240,
                    "Home": [0,-70],
                },
                "BLE" : {
                    "MAC" : "NONE",
                    "REMOTE" : "NONE",
                    "Type" : "Domain",
                },
                "Advanced": {
                    "Cover2Start": False,
                }
            }
        try:
            os.stat(CONFIG_FILE)
        except:
            with open(CONFIG_FILE, "w") as f:
                ujson.dump(data, f)
        with open(CONFIG_FILE) as f:
            self.cfg = ujson.load(f)
            bUpdate = False
            for i in data:
                for c in data[i].keys():
                    try:
                        self.cfg[str(i)][str(c)]
                    except:
                        bUpdate = True
        if bUpdate:
            os.rename(CONFIG_FILE,CACHE_FILE)
            with open(CACHE_FILE, "r") as ca:
                self.cache = ujson.load(ca)
            with open(CONFIG_FILE, "w") as d:
                ujson.dump(data, d)
            with open(CONFIG_FILE, "r") as d:
                self.cfg = ujson.load(d)
            for i in data:
                for c in data[i].keys():
                    try:
                        vCache = self.cache[str(i)][str(c)]
                        print(vCache)
                        self.cfg[str(i)][str(c)] = vCache
                        with open(CONFIG_FILE, "w") as d:
                            ujson.dump(self.cfg, d)
                    except:
                        pass
            os.remove(CACHE_FILE)
                

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
lxCache = 32767
lyCache = 32767


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
    iDeltaAngle = int(iCMP-iFacingAngle)
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
        iDeltaAngle = int(iDeltaAngle - 360)
    else:
        iDeltaAngle = int(iDeltaAngle)
    set_motor.RPM(
        iSpeedU - iDeltaAngle * iGlobalPIDK,
        iSpeedV - iDeltaAngle * iGlobalPIDK,
        iSpeedV + iDeltaAngle * iGlobalPIDK,
        iSpeedU + iDeltaAngle * iGlobalPIDK
        )



#Value Mod
def LidarCache()->list[list[int],list[int]]:
    iJumpSample = 2
    iSampleNumber = 10
    lOutData = [[],[]]
    for _ in range(iSampleNumber):
        lRawData=lidar.read()
        for i in range(0,40,iJumpSample):
            lOutData[0].append(lRawData[0][i])
            lOutData[1].append(lRawData[1][i])
        delay.us(8050)
    return lOutData

def LidarDists():
    lOutData = [[],[]]
    lCache = [0,0,0,0]
    lRawDists = [[],[],[],[]]
    lOut = [[],[],[],[]]
    lOutDists = []
    lOutData = LidarCache()

    for i in range(len(lOutData[0])):
            if lOutData[1][i] < 3000:
                # y方向 sin 270-90
                if 90 < lOutData[0][i] < 270:
                    lRawDists[2].append(lOutData[1][i]*abs(math.cos((math.radians(lOutData[0][i])))))
                else:
                    lRawDists[0].append(lOutData[1][i]*abs(math.cos((math.radians(lOutData[0][i])))))
                # x方向 sin 0-180
                if 0 < lOutData[0][i] < 180:
                    lRawDists[3].append(lOutData[1][i]*abs(math.sin((math.radians(lOutData[0][i])))))
                else:
                    lRawDists[1].append(lOutData[1][i]*abs(math.sin((math.radians(lOutData[0][i])))))

    for i in range(len(lRawDists)):
        for j in range(len(lRawDists[i])):
            if (0 > (lRawDists[i][j]-lRawDists[i][j-1]) > -2.65):
                lOut[i].append(lRawDists[i][j])
            else:
                lCache[i] = lRawDists[i][j]
        if len(lOut[i]) == 0:
            try:
                lOut[i].append(max(lRawDists[i]))
            except:
                lOut[i].append(0)

    for l in lOut:
        iDist = (((sum(l))/len(l)))
        lOutDists.append(iDist)
    
    return lOutDists

def GetDists() -> list[int,int,int]:
    if not cfg.read("Tofs","On"):
        return LidarDists()
    else:
        lDists = []
        Num = cfg.read("A2AOb","NumOfDist")
        for i in range(Num):
            lDists.append(
                int(set_adc.read(cfg.read("Tofs",str(i)))*cfg.read("Tofs","K")+cfg.read("Tofs","B"))
                )
        return lDists

def GetPos() -> list[int,int]:
    global lxCache,lyCache
    if not cfg.read("Tofs","On"):
        Distance = GetDists()
        iCfgK = 10
        # if Distance[0]+Distance[2] < (cfg.read("Position","Height")*iCfgK):
        #     if (cfg.read("Position","Height")*iCfgK) > Distance[0] > Distance[2]:
        #         Y = (((cfg.read("Position","Height")*(iCfgK/2))) - (Distance[0]))
        #     else:
        #         Y = -(((Distance[2]) - (cfg.read("Position","Height")*iCfgK/2)))
        # else:
        #     Y = -(((cfg.read("Position","Height")*(iCfgK/2)) - Distance[0]) + (Distance[2] - (cfg.read("Position","Height")*(iCfgK/2))))/2
        # if Distance[1]+Distance[3] < (cfg.read("Position","Width")*iCfgK):
        #     if (cfg.read("Position","Height")*iCfgK) > Distance[1] > Distance[3]:
        #         X = (cfg.read("Position","Width")*(iCfgK/2) - Distance[1])
        #     else:
        #         X = (Distance[3] - cfg.read("Position","Width")*(iCfgK/2))
        # else:
        #     X = ((cfg.read("Position","Width")*(iCfgK/2) - Distance[1] ) + (Distance[3] - cfg.read("Position","Width")*(iCfgK/2)))/2
        Y = -(((cfg.read("Position","Height")*(iCfgK/2)) - Distance[0]) + (Distance[2] - (cfg.read("Position","Height")*(iCfgK/2))))/2
        X = ((cfg.read("Position","Width")*(iCfgK/2) - Distance[1] ) + (Distance[3] - cfg.read("Position","Width")*(iCfgK/2)))/2
        return [int(X)/10,int(Y)/10]
    else:
        Distance = GetDists()
        if Distance[0]+Distance[2] < (cfg.read("Position","Height") - 35):
            if Distance[0] > Distance[2]:
                Y = cfg.read("Position","Height")/2 - Distance[0] -4
            else:
                Y = Distance[2] - cfg.read("Position","Height")/2 + 4
        else:
            Y = ((cfg.read("Position","Height")/2 - Distance[0]) + (Distance[2] - cfg.read("Position","Height")/2))/2
        if Distance[1]+Distance[3] < (cfg.read("Position","Width") - 35):
            if Distance[1] > Distance[3]:
                X = -(cfg.read("Position","Width")/2 - Distance[1] - 4)
            else:
                X = -(Distance[3] - cfg.read("Position","Width")/2 + 4)
        else:
            X = -((cfg.read("Position","Width")/2 - Distance[1]) + (Distance[3] - cfg.read("Position","Width")/2))/2
        return [X,Y]

def AvoidOutBorder():
    return 0
    lLocalPos = GetPos()
    if lLocalPos[0] <= 0:
        iKX = -1
    else:
        iKX = 1
    if lLocalPos[1] <= 0:
        iKY = -1
    else:
        iKY = 1
    if lLocalPos[1]*iKY >= list(cfg.read("Border","0"))[1]:
        if lLocalPos[0]*iKX >= list(cfg.read("Border","0"))[0]:
            iMoveAngle = -135
        else:
            iMoveAngle = 180
    elif lLocalPos[1]*iKY >= list(cfg.read("Border","1"))[1]:
        if lLocalPos[0]*iKX >= list(cfg.read("Border","0"))[0]:
            iMoveAngle = -90
        elif lLocalPos[0]*iKX <= list(cfg.read("Border","1"))[0]:
            # print(GetPos())
            iMoveAngle = 180
        else:
            pass
    else:
        pass
    try:
        iMoveAngle = iMoveAngle*iKX*iKY
        if iMoveAngle == -180:
            iMoveAngle = 0
        GoV(0,-iMoveAngle,200)
    except:
        car.stop()

def ObtDetect() -> list[bool,bool]:
    '''
    返回一个列表，包含了每个角度是否被遮挡
    '''
    #TODO 无法走迷宫
    global lBlockedMemo,iMemoLife,bLife
    lStatusOfDist = []
    # iMaxLife = cfg.read("A2AOb","LifeTime")
    lDists = GetDists()
    iNumOfDist = len(lDists)
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
    #         bLife = True
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
    return lStatusOfDist

def AvoidObt(iFacingAngle: int | None = 0,iTargetAngle:int | None = 0,iSpeed:int | None = 150) -> None:
    '''
    iFacingAngle 移动时面对的方向 0~360
    iTargetAngle 需要移动的方向 可能不采用 -180~180
    iSpeed 移动的速度 默认150
    '''
    iTargetAngle = -iTargetAngle
    lAvailbeAngles = []
    lBlockedAngles = []
    lStatusOfDist = ObtDetect()
    iNumOfDist = len(GetDists())
    iPerAngle = int(359/iNumOfDist)
    #获取挡住/被挡住的角度
    for i in range(iNumOfDist):
        if i < iNumOfDist/2:#左半部分
            if lStatusOfDist[i]:
                lAvailbeAngles.append(-i*iPerAngle)
            else:
                lBlockedAngles.append(-i*iPerAngle)
        else:#右半部分
            if lStatusOfDist[i]:
                lAvailbeAngles.append((abs(i-iNumOfDist))*iPerAngle+1)
            else:
                lBlockedAngles.append((abs(i-iNumOfDist))*iPerAngle+1)
   #判断
    if len(lBlockedAngles) > 0.75*iNumOfDist:#被挡住三个
        iAimAngle = lAvailbeAngles[0]
        GoV(iFacingAngle,iAimAngle,iSpeed)
    elif len(lBlockedAngles) == 0.5*iNumOfDist:#被挡住两个以下
        if (all(lAvailbeAngles[i] - lAvailbeAngles[i - 1] == lAvailbeAngles[1] - lAvailbeAngles[0] for i in range(2, len(lAvailbeAngles)))) and (lAvailbeAngles[0] > iTargetAngle > lAvailbeAngles[-1]):
            iAimAngle = iTargetAngle
        else:
            iAimAngle = FindNearstAngle(lAvailbeAngles,iTargetAngle)
        # print(lBlockedAngles,lAvailbeAngles)
        GoV(iFacingAngle,iAimAngle,iSpeed)
    elif len(lBlockedAngles) < iNumOfDist:
        iAimAngle = iTargetAngle
        # if lAvailbeAngles[0] > iTargetAngle > lAvailbeAngles[-1]:
        #     print(1)
        # else:
        #     iAimAngle = FindNearstAngle(lAvailbeAngles,iTargetAngle)
        # # print(iTargetAngle,iFacingAngle,iAimAngle,iSpeed)
        print(lAvailbeAngles,lBlockedAngles)
        GoV(iFacingAngle,iAimAngle,iSpeed)
    else:
        car.stop()
    # car.z_move(iFacingAngle,iAimAngle,200)

def Pos2Angle(lAimPos:list[int,int]) -> int:
    '''
    lAimPos 一个坐标 示例：[0,0]
    '''
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

def Pos2Pos(iFacingAngle,lAimPos:list[int,int], A2O:bool | None = True) -> int:

    '''
    iFacingAngle 移动时面对的方向 0~360
    lAimPos 目标坐标位置 如[0,0] 距离越近速度越小
    A2O 是否开启自动避障 默认True
    '''
    # AvoidOutBorder()
    iAimX = lAimPos[0]
    iAimY = lAimPos[1]
    lLocal = GetPos()
    iLocX = lLocal[0]
    iLocY = lLocal[1]
    iDeltaX = iAimX - iLocX
    iDeltaY = iAimY - iLocY
    if iDeltaX > 500:
        iDeltaX = iDeltaX/7
    if iDeltaY > 500:
        iDeltaY = iDeltaY/5
    if iDeltaX < 100:
        iDeltaX = iDeltaX*3
    if iDeltaY < 100:
        iDeltaY = iDeltaY*3
    #TODO 得出的是0刻度与目标距离的夹角
    iErrorRange = cfg.read("Position","ErrorRange")/2
    if A2O:
        if iErrorRange > iDeltaX > -iErrorRange and iErrorRange > iDeltaY > -iErrorRange:
            car.stop()
        else:
            if 0 > iDeltaX:
                PA = Pos2Angle(lAimPos) + 180
            else:
                PA = Pos2Angle(lAimPos)
            if 0 > iDeltaY:
                PA = Pos2Angle(lAimPos) - 180
            # car.turn(iFacingAngle)
            AvoidObt(iFacingAngle,PA,(abs(iDeltaX) - abs(iDeltaY))/1.3)
    else:
        if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY):
            car.stop()
        else:
        # car.turn(iFacingAngle)
            Go2(iFacingAngle,iDeltaX,iDeltaY)



def Move2Path(iFacingAngle:int,Posistions:list[list[int,int],list[int,int]],A2O:bool):
    iErrorRange = cfg.read("Position","ErrorRange")/2
    for i in Posistions:
        while (1):
            iAimX = i[0]
            iAimY = i[1]
            lLocal = GetPos()
            iLocX = lLocal[0]
            iLocY = lLocal[1]
            iDeltaX = iAimX - iLocX
            iDeltaY = iAimY - iLocY
            if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY):
                break
            else:
                Pos2Pos(iFacingAngle=iFacingAngle,lAimPos=i,A2O=A2O)
        
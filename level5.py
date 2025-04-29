import sensor,image,lcd,math,time,pyb
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,lidar
from pyb import UART

# if (set_adc.read(14)*11*3.3/1024) <= 11:
#    raise Exception("电池电压过低，请充电")

set_io.out(6,1)
set_io.out(6,0)

# config.py | RCJ Version 2.1.0(2025042700) Developer 423
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
                    "On": False,
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
                    "Type": "Slave",
                    "MAC" : "NONE",
                    "REMOTE" : "NONE",
                    "Setup" : False,
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

class BlueTooth:
    def __init__(self):
        self.cfg = QkJson()
        self.Bluetooth = UART(3,115200)
        self.BlueDelayMs = 10
        self.BlueConnected = 0
        self.BlueSlaveMAC = self.cfg.read("BLE","REMOTE")
        if self.cfg.read("BLE","Setup") == False:
            self.Bluetooth.write("+++")
            delay.ms(self.BlueDelayMs)
            if self.Bluetooth.any():
                BlueMsg=self.Bluetooth.read().decode()
                print("+++ : %s" % BlueMsg[0:BlueMsg.index("\r\n")])
            ####################################################
            if self.cfg.read("BLE","Type") == "Domain":
                self.Bluetooth.write("AT+ROLE=1\r\n")
            else:
                self.Bluetooth.write("AT+ROLE=0\r\n")
            delay.ms(self.BlueDelayMs)
            if self.Bluetooth.any():
                BlueMsg=self.Bluetooth.read().decode()
                print("Role : %s" % BlueMsg[0:BlueMsg.index("\r\n")])
                if "ERROR" in BlueMsg:
                    self.Bluetooth.write("AT+ROLE=2\r\n")
                    delay.ms(self.BlueDelayMs)
                    if self.Bluetooth.any():
                        BlueMsg=self.Bluetooth.read().decode()
                        print("Role : %s" % BlueMsg[0:BlueMsg.index("\r\n")])
            self.Bluetooth.write("AT+MAC?\r\n")
            delay.ms(self.BlueDelayMs)
            if self.Bluetooth.any():
                BlueMsg=self.Bluetooth.read().decode()
                print("MAC : %s" % BlueMsg[BlueMsg.index("CC:")+3:BlueMsg.index("\r\n")])
                self.cfg.write("BLE","MAC",BlueMsg[BlueMsg.index("CC:")+3:BlueMsg.index("\r\n")])
            self.Bluetooth.write("AT+AUTO_CNT=1,CC:%s,1\r\n" % self.BlueSlaveMAC)
            delay.ms(self.BlueDelayMs)
            if self.Bluetooth.any():
                print("AT+AUTO_CNT=1,CC:%s,1 : %s" % (self.BlueSlaveMAC, self.Bluetooth.read().decode()[0:BlueMsg.index("\r\n")]))
            ####################################################
            self.Bluetooth.write("AT+RESTART\r\n")
            delay.ms(1000)
            cfg.write("BLE","Setup",True)
        else:
            pass

    def errorHandler(self):
        self.Bluetooth.write("AT+EXIT\r\n")
        delay.ms(self.BlueDelayMs)
        if self.Bluetooth.any():
            BlueMsg=self.Bluetooth.read().decode()
            print("AT+EXIT : %s" % BlueMsg[0:BlueMsg.index("\r\n")])
            if "ERROR" in BlueMsg:
                self.Bluetooth.write("AT+EXIT\r\n")
                delay.ms(self.BlueDelayMs)
                if self.Bluetooth.any():
                    BlueMsg=self.Bluetooth.read().decode()
                    print("AT+EXIT : %s" % BlueMsg[0:BlueMsg.index("\r\n")])
        self.Bluetooth.write("+++")
        delay.ms(self.BlueDelayMs)
        if self.Bluetooth.any():
            BlueMsg=self.Bluetooth.read().decode()
            print("+++ : %s" % BlueMsg[0:BlueMsg.index("\r\n")])

    def connect(self):
        if (self.BlueConnected == 0):
            self.Bluetooth.write("+++")
            delay.ms(self.BlueDelayMs)
            if self.Bluetooth.any():
                BlueMsg=self.Bluetooth.read().decode()
                print(":151 +++ : %s" % BlueMsg[0:BlueMsg.index("\r\n")])
                if "ERROR" in BlueMsg:
                    self.errorHandler()
                self.Bluetooth.write("AT+CNT_LIST\r\n")                  #串口发送一条信息
                delay.ms(self.BlueDelayMs)
                if self.Bluetooth.any():
                    Blue_read_buf=self.Bluetooth.read().decode()         #取出读到的字节串，并把它转换成字符串
                    print("AT+CNT_LIST : %s" % Blue_read_buf)       #取出读到的字节串，并把它转换成字符串
                    if self.BlueSlaveMAC in Blue_read_buf:
                        self.BlueConnected = 1
                        print("Slave connect ok ")                  #取出读到的字节串，并把它转换成字符串
                        self.Bluetooth.write("AT+EXIT\r\n")              #串口发送一条信息
                        delay.ms(self.BlueDelayMs)
                        if self.Bluetooth.any(): #如果字符串里有东西，则进来判断东西是什么
                            print("AT+EXIT : %s" % self.Bluetooth.read().decode())    #取出读到的字节串，并把它转换成字符串
            return False
        if self.BlueConnected == 1:
            print("*************************************")
            if self.Bluetooth.any():
                Blue_read_buf=self.Bluetooth.read().decode()
                if "DISCONNECTED" in Blue_read_buf:
                    self.BlueConnected = 0
                    print("Slave disconnect")
                    self.Bluetooth.write("+++")
                    delay.ms(self.BlueDelayMs)
                    if self.Bluetooth.any():
                        BlueMsg=self.Bluetooth.read().decode()
                        print("+++ : %s" % BlueMsg[0:BlueMsg.index("\r\n")])
                    delay.ms(1000)
                else:
                    pass
            return True

    def send(self,Data):
        if self.BlueConnected == 1:
            self.Bluetooth.write(Data)
            print("Send to %s"% Data,cfg.read("BLE","REMOTE"))
            delay.ms(self.BlueDelayMs)
            if self.Bluetooth.any():
                print("SendData : %s" % self.Bluetooth.read().decode())
        else:
            delay.ms(self.BlueDelayMs)
            self.connect()

    def receive(self):
        if self.Bluetooth.any():
            BlueMsg = self.Bluetooth.read().decode()
            delay.ms(self.BlueDelayMs)
            if BlueMsg == None:
                return False
            print("ReceiveData : %s" % BlueMsg)
            return BlueMsg
        else:
            pass

cfg = QkJson()
ble = BlueTooth()

#Values
bLife = False
bC2S = False
lBlockedMemo = []

lBallPos = [0,0]
lLidarDists = [0,0,0,0]
bThreadControllerFlag = True
iUARTPort = 1

#Math Mod
def roundThresholdJudger(iValue, iRound, iMiddleValue, iOffset):
    iValue = iValue % iRound
    
    iLowerThreshold = (iMiddleValue - iOffset) % iRound
    iUpperThreshold = (iMiddleValue + iOffset) % iRound

    if iLowerThreshold <= iUpperThreshold:
        return iLowerThreshold <= iValue <= iUpperThreshold

    else:
        return iValue >= iLowerThreshold or iValue <= iUpperThreshold

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
    set_motor.RPM(iSpeedU - iDeltaAngle * iGlobalPIDK,iSpeedV - iDeltaAngle * iGlobalPIDK,iSpeedU + iDeltaAngle * iGlobalPIDK,iSpeedV + iDeltaAngle * iGlobalPIDK)

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
        iSpeedU + iDeltaAngle * iGlobalPIDK,
        )


#Value Mod


def LidarCache()->list[list[int],list[int]]:
    #TODO 已弃用
    iJumpSample = 1
    iSampleNumber = 8
    lOutData = [[],[]]
    for _ in range(iSampleNumber):
        lRawData=lidar.read()
        for i in range(0,40,iJumpSample):
            lOutData[0].append(abs(lRawData[0][i]+compass.read()-360))
            lOutData[1].append(lRawData[1][i])
        delay.us(8050)
    return 0

def LidarDists():
    ClearUART(1)
    iCompass = str(int(compass.read()))
    sSentData = 'cmp'+str(iCompass)+'end'
    SendUART(1,sSentData)
    sReceivedDataFrame = GetUART(1)
    sParsedDataFrame = sReceivedDataFrame[sReceivedDataFrame.index('som')+3:sReceivedDataFrame.index('eom',sReceivedDataFrame.index('som'))+3]
    iFrontDist = int(sParsedDataFrame[sParsedDataFrame.index('fd')+2:sParsedDataFrame.index('rd')])
    iRightDist = int(sParsedDataFrame[sParsedDataFrame.index('rd')+2:sParsedDataFrame.index('bd')])
    iBackDist = int(sParsedDataFrame[sParsedDataFrame.index('bd')+2:sParsedDataFrame.index('ld')])
    iLeftDist = int(sParsedDataFrame[sParsedDataFrame.index('ld')+2:sParsedDataFrame.index('eom')])
    lOutDists = [iFrontDist,iRightDist,iBackDist,iLeftDist]
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

def Cover2Start():
    global bC2S
    if cfg.read("Advanced","Cover2Start"):
        if GetDists()[5] < 500:
            bC2S = True
        else:
            pass
    else:
        bC2S = True
    return bC2S

def GetPos() -> list[int,int]:
    if not cfg.read("Tofs","On"):
        Distance = GetDists()
        iCfgK = 10
        if Distance[0]+Distance[2] < (cfg.read("Position","Height")*iCfgK):
            if (cfg.read("Position","Height")*iCfgK) > Distance[0] > Distance[2]:
                Y = (((cfg.read("Position","Height")*(iCfgK/2))) - (Distance[0]))
            else:
                Y = (((Distance[2]) - (cfg.read("Position","Height")*iCfgK/2)))
        else:
            Y = (((cfg.read("Position","Height")*(iCfgK/2)) - Distance[0]) + (Distance[2] - (cfg.read("Position","Height")*(iCfgK/2))))/2
        if Distance[1]+Distance[3] < (cfg.read("Position","Width")*iCfgK):
            if (cfg.read("Position","Height")*iCfgK) > Distance[1] > Distance[3]:
                X = -(cfg.read("Position","Width")*(iCfgK/2) - Distance[1])
            else:
                X = -(Distance[3] - cfg.read("Position","Width")*(iCfgK/2))
        else:
            X = -((cfg.read("Position","Width")*(iCfgK/2) - Distance[1] ) + (Distance[3] - cfg.read("Position","Width")*(iCfgK/2)))/2

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
    # return 0
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

def ObtDetect() -> list[list[int,int],list[bool,bool]]:
    '''
    返回一个列表，[[角度],[是否被遮挡]]
    '''
    if cfg.read("Tofs","On"):
        global lBlockedMemo,iMemoLife,bLife
        lStatusOfDist = [[],[]]
        # iMaxLife = cfg.read("A2AOb","LifeTime")
        lDists = GetDists()
        iNumOfDist = len(lDists)
        iPerAngle = int(359/iNumOfDist)
        if len(lStatusOfDist) < iNumOfDist:
            for d in range(iNumOfDist):
                lStatusOfDist.append(True)
        for i in range(iNumOfDist):
            lStatusOfDist[0].append(iPerAngle*i)
            if lDists[i] <= cfg.read("A2AOb","ActiveRange"):
                lStatusOfDist[1][i] = False
            else:
                lStatusOfDist[1][i] = True
        return lStatusOfDist
    else:
        global lBlockedMemo,iMemoLife,bLife
        lStatusOfDist = [[],[]]
        lDists = LidarCache()
        if len(lStatusOfDist) < len(lDists[0]):
            for d in range(len(lDists[0])):
                lStatusOfDist[1].append(True)
                lStatusOfDist[0].append(abs(360-lDists[0][d]))
        for i in range(len(lDists[0])):
            if lDists[1][i] <= cfg.read("A2AOb","ActiveRange"):
                lStatusOfDist[1][i] = False
            else:
                lStatusOfDist[1][i] = True
        lStatusOfDist[0] = lStatusOfDist[0][::-1]
        lStatusOfDist[1] = lStatusOfDist[1][::-1]
        return lStatusOfDist

def AvoidObt(iFacingAngle: int | None = 0,iTargetAngle:int | None = 0,iSpeed:int | None = 150) -> None:
    '''
    iFacingAngle 移动时面对的方向 0~360
    iTargetAngle 需要移动的方向 可能不采用 -180~180
    iSpeed 移动的速度 默认150
    '''
    iTargetAngle = -iTargetAngle
    lStatusOfDist = ObtDetect()
    #获取挡住/被挡住的角度

   #判断
    lAvailbeAngles = []
    for i in range(len(lStatusOfDist[0])):
        if lStatusOfDist[1][i]:
            lAvailbeAngles.append(lStatusOfDist[0][i])
    print(lAvailbeAngles)
    try:
        iAimAngle = FindNearstAngle(lAvailbeAngles,iTargetAngle)
        GoV(iFacingAngle,iAimAngle,iSpeed)
        # car.z_move(iFacingAngle,iAimAngle,200)
    except:
        car.stop()

def Local2Angle(lAimPos:list[int,int]) -> int:
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

def Pos2Angle(lInputPos:list[int,int],lAimPos:list[int,int]) -> int:
    '''
    lInputPos 输入坐标
    lAimPos 目标坐标 示例：[0,0]
    '''
    iAimX = lAimPos[0]
    iAimY = lAimPos[1]
    iLocX = lInputPos[0]
    iLocY = lInputPos[1]
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
    delay.ms(100)
    lLocal = GetPos()
    iLocX = lLocal[0]
    iLocY = lLocal[1]
    iDeltaX = iAimX - iLocX
    iDeltaY = iAimY - iLocY
    if iDeltaX > 500:
        iDeltaX = iDeltaX/5
    if iDeltaY > 500:
        iDeltaY = iDeltaY/5
    if iDeltaX < 100:
        iDeltaX = iDeltaX*3
    if iDeltaY < 100:
        iDeltaY = iDeltaY*3
    iErrorRange = cfg.read("Position","ErrorRange")/2
    if A2O:
        if iErrorRange > iDeltaX > -iErrorRange and iErrorRange > iDeltaY > -iErrorRange:
            car.stop()
        else:
            if 0 > iDeltaX:
                PA = Local2Angle(lAimPos) + 180
            else:
                PA = Local2Angle(lAimPos)
            if 0 > iDeltaY:
                PA = Local2Angle(lAimPos) - 180
            AvoidObt(iFacingAngle,PA,(abs(iDeltaX) - abs(iDeltaY))/1.3)
    else:
        if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY):
            car.stop()
        else:
        # car.turn(iFacingAngle)
            Go2(iFacingAngle,iDeltaX,iDeltaY)

def Move2Path(iFacingAngle:int,Posistions:list[list[int,int],list[int,int]],iWaitMs:int,A2O:bool):
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
                if i == Posistions[-1]:
                    return True
                else:
                    delay.ms(iWaitMs)
                    break
            else:
                Pos2Pos(iFacingAngle=iFacingAngle,lAimPos=i,A2O=A2O)

def roundThresholdJudger(iValue, iRound, iMiddleValue, iOffset):
    iValue = iValue % iRound
    iLowerThreshold = (iMiddleValue - iOffset) % iRound
    iUpperThreshold = (iMiddleValue + iOffset) % iRound
    
    if iLowerThreshold <= iUpperThreshold:
        return iLowerThreshold <= iValue <= iUpperThreshold
    else:
        return iValue >= iLowerThreshold or iValue <= iUpperThreshold

def CircleAround(iAimAngle):
    if abs(compass.read() - iAimAngle) >= 180:
        iDirectionFactor = 1
    else:
        iDirectionFactor = -1
    while(1):
        lBallPos = GetBallPos()
        iX, iY = lBallPos[0], lBallPos[1]
        if iY > 0:
            iDeltaAngle = -int(math.degrees(math.atan2(iY, iX)) - 90)     
        print(min(iDirectionFactor * (30 - iDeltaAngle),iDirectionFactor * 30),-iDirectionFactor * (130 + iDeltaAngle),max(-iDirectionFactor * (30 - iDeltaAngle),-iDirectionFactor * 30),iDirectionFactor * (130 + iDeltaAngle))
        if roundThresholdJudger(compass.read(), 360, iAimAngle, 3):
            break
        else:
            set_motor.RPM(min(iDirectionFactor * (30 - iDeltaAngle),iDirectionFactor * 30),-iDirectionFactor * (130 + iDeltaAngle),max(-iDirectionFactor * (30 - iDeltaAngle),-iDirectionFactor * 30),iDirectionFactor * (130 + iDeltaAngle))
    car.stop()

def RunCircle(r:int, angle:int,a:int):
    iSpeed = 355/r
    iRad = math.radians(angle)
    iInsideSpeed = iSpeed * r
    iOutsideSpeed = iSpeed * r
    x= int(iInsideSpeed* math.sin(iRad))
    y= int(iOutsideSpeed* math.cos(iRad))
    z= -int(iInsideSpeed * math.sin(iRad))
    w= -int(iOutsideSpeed* math.cos(iRad))
    if (a == 1):   #正
        set_motor.RPM(x,y,z,w)
    elif( a == -1 ): #反
        set_motor.RPM(z,w,x,y)
    else:
        set_motor(0,0,0,0)
    length = r * iRad  # 弧长
    time = length / iSpeed
    delay.ms(time)
    set_motor.RPM(0, 0, 0, 0)


#Communication
def GetUART(Port):
    UARTDevice = UART(Port,115200)
    while(1):
        if UARTDevice.any():
            Data = str(UARTDevice.read())
            return Data

def SendUART(iPort,sData):
    UARTDevice = UART(iPort,115200)
    UARTDevice.write(sData)

def ClearUART(iPort):
    UARTDevice = UART(iPort,115200)
    if UARTDevice.any():
        UARTDevice.read()

def GetBallPos()-> list[int,int]:
    ClearUART(1)
    sSentData = 'cmp'+str(999)+'end'
    SendUART(1,sSentData)
    sData = GetUART(1)
    iBX = int(sData[sData.index('sombx')+5:sData.index('by')])
    iBY = int(sData[sData.index('by')+2:sData.index('eom')])
    return [iBX, iBY]

#Offense & Defense
def AimBall() -> int:
    Ball = GetBallPos()
    if Ball[1] < 0:
        iAngle = 180
    else:
        iAngle = 0
    return math.radians(math.acos(Ball[0]/int((Ball[1]**2 + Ball[1]**2)**0.5)))+iAngle

def Circle(origin:list[int,int],angle:int,r:int):
    Pos2Pos(
        angle,
        [origin[0]+((r**2)/((1+math.tan(angle)**2)))**0.5,
        origin[1]+(math.tan(angle)**-1)*((r**2)/((1+math.tan(angle)**2)))**0.5]
        ,False)

def offense()->None:
    lPos = GetPos()
    lBallPos = GetBallPos()
    if lPos[1] > -50 or (lBallPos[0] == 0 and lBallPos[1] == 0):
        Pos2Pos(0,cfg.read("Position","Home"),False)
    else:
        iAngle = AimBall()
        if 180 > (iAngle-90) > 0:
            car.z_move(iAngle,iAngle+90,5*lBallPos[0])
        else:
            car.z_move(iAngle,iAngle-90,5*lBallPos[0])
        # Circle(cfg.read("Position","Home"),AimBall(cfg.read("Position","Home")),35)

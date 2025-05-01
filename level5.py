import image,lcd,math,time,pyb
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,lidar
from pyb import UART

# if (set_adc.read(14)*11*3.3/1024) <= 11:
#    raise Exception("电池电压过低，请充电")


#car.set_speed_PID(1,2,1)

# config.py | RCJ Version 2.3.0(2025042700) Developer 423
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
                "Ports": {
                    0: 1,
                    1: 2,
                    2: 3,
                    3: 4,
                    "RailGun" : 6,
                },
                "Distance": {
                    "On": False,
                    "K": 0.67,
                    "B": 4,
                    },
                "A2AOb": {
                    "NumOfDist": 4,
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
                    "Setup": False,
                    "Type": "Slave",
                    "MAC" : "NONE",
                    "REMOTE" : "NONE",
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
        try:
            return self.cfg[section][option]
        except KeyError:
            self.__init__()

class BlueTooth:
    def __init__(self):
        self.cfg = QkJson()
        self.Bluetooth = UART(3,115200)
        self.BlueDelayMs = 10
        self.BlueConnected = 0
        self.BlueSlaveMAC = self.cfg.read("BLE","REMOTE")
        while True:
            self.Bluetooth.write("AT+EXIT\r\n")
            try:
                if "OK" in self.Bluetooth.read().decode():
                    break
                else:
                    print("trying Again")
            except:
                break

    def sendCommand(self, command: str) -> str:
        self.Bluetooth.write(command)
        delay.ms(self.BlueDelayMs)
        if self.Bluetooth.any():
            BlueMsg=self.Bluetooth.read().decode()
            if "ERROR" in BlueMsg:
                if "+++" in command:
                    BlueMsg = self.sendCommand("AT+EXIT\r\n")
                    BlueMsg = self.sendCommand(command)
            # if "+++" in command:
            #     print("%s : %s" %(command, BlueMsg[0:BlueMsg.index("\r\n")]))
            # else:
            #     print("%s : %s" %(command[0:command.index("\r\n")], BlueMsg[0:BlueMsg.index("\r\n")]))
            return BlueMsg
        else:
            self.Bluetooth.write("+++")
            self.Bluetooth.write("AT+EXIT\r\n")
            delay.ms(self.BlueDelayMs)
            if self.Bluetooth.any():
                BlueMsg=self.Bluetooth.read().decode()
                if "ERROR" in BlueMsg:
                    self.Bluetooth.write("AT+EXIT\r\n")
                    delay.ms(self.BlueDelayMs)
                    if self.Bluetooth.any():
                        BlueMsg=self.Bluetooth.read().decode()
                    else:
                        raise Exception("Check Ble")
            else:
                self.Bluetooth.write("AT+EXIT\r\n")
                if self.Bluetooth.any():
                    BlueMsg=self.Bluetooth.read().decode()
                    print(BlueMsg)
                    if "ERROR" in BlueMsg:
                        self.Bluetooth.write("AT+EXIT\r\n")
                        delay.ms(self.BlueDelayMs)
                        if self.Bluetooth.any():
                            BlueMsg=self.Bluetooth.read().decode()
                        else:
                            raise Exception("Check Ble for Error")
                    else:
                        pass

    def Setup(self):
        if self.cfg.read("BLE","Setup") == False:
            self.sendCommand("+++")
            ####################################################
            # if self.cfg.read("BLE","Type") == "Domain":
            #     self.sendCommand("AT+ROLE=1\r\n")
            # else:
            #     self.sendCommand("AT+ROLE=0\r\n")
            self.sendCommand("AT+ROLE=2\r\n")
            BlueMsg = self.sendCommand("AT+MAC?\r\n")
            b = BlueMsg[BlueMsg.index("CC:")+3:BlueMsg.index("\r\n")]
            self.cfg.write("BLE","MAC",b)
            print("Bluetooth MAC:",cfg.read("BLE","MAC"))
            self.sendCommand("AT+DEV_DEL=ALL\r\n")
            self.sendCommand("AT+AUTO_CNT=1,CC:%s,1\r\n" % self.BlueSlaveMAC)
            delay.ms(self.BlueDelayMs)
            ####################################################
            self.sendCommand("AT+RESTART\r\n")
            cfg.write("BLE","Setup",True)
            delay.ms(1000)
            return False
        else:
            return True

    def connect(self):
        if self.Setup() == True:
            if self.BlueConnected == 0:
                if self.sendCommand("+++"):
                    msg = self.sendCommand("AT+CNT_LIST\r\n")
                    if self.BlueSlaveMAC in msg or "*" in msg:
                        self.BlueConnected = 1
                        print("Slave connect ok ")                  #取出读到的字节串，并把它转换成字符串
                        self.sendCommand("AT+EXIT\r\n")
                        return True
                    else:
                        self.sendCommand("AT+EXIT\r\n")
                        return False
                else:
                    return False
            if self.BlueConnected == 1:
            #     if self.Bluetooth.any():
            #         Blue_read_buf=self.Bluetooth.read().decode()
            #         print(Blue_read_buf)
            #         if "DISCONNECTED" in Blue_read_buf:
            #             self.BlueConnected = 0
            #             print("Slave disconnect")
            #             delay.ms(1000)
                return True

    def send(self,Data):
        if self.Setup():
            if self.BlueConnected == 1:
                self.Bluetooth.write(Data)
                delay.ms(self.BlueDelayMs)
            else:
                delay.ms(self.BlueDelayMs)
                self.connect()

    def receive(self):
        if self.Setup():
            if self.BlueConnected == 1:
                if self.Bluetooth.any():
                    try:
                        BlueMsg = self.Bluetooth.read().decode()
                        delay.ms(self.BlueDelayMs)
                        if BlueMsg == None:
                            pass
                        print("ReceiveData : %s" % BlueMsg)
                        return BlueMsg
                    except:
                        pass
                else:
                    pass
            else:
                delay.ms(self.BlueDelayMs)
                self.connect()

cfg = QkJson()
ble = BlueTooth()

#Values
bLife = False
lBlockedMemo = []
bCovered = False
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
    if not cfg.read("Distance","On"):
        return LidarDists()
    else:
        lDists = []
        Num = cfg.read("A2AOb","NumOfDist")
        for i in range(Num):
            lDists.append(
                int(set_adc.read(cfg.read("Ports",str(i)))*cfg.read("Distance","K")+cfg.read("Distance","B"))
                )
        return lDists

def GetPos() -> list[int,int]:
    if not cfg.read("Distance","On"):
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

#Operate models
def RailGun():
    set_io.out(cfg.read("Ports","RailGun"),1)
    set_io.out(cfg.read("Ports","RailGun"),0)

def Cover2Start():
    global bCovered
    if LidarDists()[0] < 10 or bCovered:
        bCovered = True
        return True
    else:
        bCovered = False
        return False

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
    if cfg.read("Distance","On"):
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
    iDeltaAngle = math.degrees(math.atan2(iDeltaY,iDeltaX))
    return int(iDeltaAngle)

def Pos2Pos(iFacingAngle,lAimPos:list[int,int], A2O:bool | None = False) -> int:

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
            return True
        else:
        # car.turn(iFacingAngle)
            # Go2(iFacingAngle,iDeltaX,iDeltaY)
            if iDeltaY > 0:
                iAngle = 180
            else:
                iAngle = 0
            iMovedAngle = int(math.degrees(math.atan2(iDeltaY,iDeltaX)))
            car.z_move(iFacingAngle,90-iMovedAngle,int((abs(iDeltaX)+abs(iDeltaY)/2)))
            return False

def Move2Path(iFacingAngle:int,Posistions:list[list[int,int],list[int,int]],iWaitMs:int,A2O:bool | None = False):
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
    iCompass = int(compass.read())


    if roundThresholdJudger(iCompass,360,iAimAngle+90,90):
        iDirectionFactor = 1
    else:
        iDirectionFactor = -1
    
    
#    if 0 <= abs(iCompass - iAimAngle) < 180:
#        iDirectionFactor = 1
#    elif 180 <= abs(iCompass - iAimAngle) < 360:
#        iDirectionFactor = -1
    while(1):
        lBallPos = GetBallPos()
        iX, iY = lBallPos[0], lBallPos[1]
        if iY > 0:
            iDeltaAngle = -int(math.degrees(math.atan2(iY, iX)) - 90)     
        print(iX,iY,iDeltaAngle,compass.read())
        if roundThresholdJudger(compass.read(), 360, iAimAngle, 3):
            break
        else:
            set_motor.RPM(iDirectionFactor * 30,-iDirectionFactor * (130 - iDeltaAngle),-iDirectionFactor * 30,iDirectionFactor * (130 - iDeltaAngle))
    car.turn(iAimAngle)
    while(1):
        iBX = GetBallPos()[0]
        if iBX <= -2:
            print('atleft')
            car.z_move(iAimAngle,iAimAngle + 90,-20)
#            set_motor.RPM(-30,30,30,-30)
        elif iBX >= 2:
            print('atright')
            car.z_move(iAimAngle,iAimAngle + 90,20)
#            set_motor.RPM(30,-30,-30,30)
        else:
            for _ in range(3):
                set_motor.RPM(0,0,0,0)
            break
    print('stopped')
    

def TurnToTheBall():
    while(1):
        lBallPos = GetBallPos()
        iX, iY = lBallPos[0], lBallPos[1]
        if -2 <= iX <= 2 and iY > 0:
            car.stop()
            break
        else:
            set_motor.RPM(20,20,-20,-20)

def AutoFetch(bStop = True):
    TurnToTheBall()
    while(1):
        lBallPos = GetBallPos()
        iBX, iBY = lBallPos[0], lBallPos[1]
        SpeedL = 30 + 3 * iBX
        SpeedR = 30 - 3 * iBX
        set_motor.RPM(SpeedL, SpeedL, SpeedR, SpeedR)
        if iBX > -2 and iBX < 2 and iBY >= 8 and iBY <= 10:
            if bStop:
                car.stop()
            break

def Move2Pos(iFacingAngle,lPos):
    while not Pos2Pos(0,lPos,False):
        pass
    for _ in range(3):
        set_motor.RPM(0,0,0,0)

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

def GoDistance(iDistance):
    iDistance = iDistance * 10
    iCompass = int(compass.read())
    
    if roundThresholdJudger(iCompass, 360, 0, 45):
        iFacingDistIndex = 0
        iMovingAngle = 0
    elif roundThresholdJudger(iCompass, 360, 90, 45):
        iFacingDistIndex = 3
        iMovingAngle = 90
    elif roundThresholdJudger(iCompass, 360, 180, 45):
        iFacingDistIndex = 2
        iMovingAngle = 180
    elif roundThresholdJudger(iCompass, 360, 270, 45):
        iFacingDistIndex = 1
        iMovingAngle = 270
    else:
        return False
    
    iAimDist = GetDists()[iFacingDistIndex] - iDistance
    
    while(1):
        car.straight(iMovingAngle, 20)
        iCurrentDist = GetDists()[iFacingDistIndex]
        print(iCurrentDist,iAimDist)
        if iCurrentDist < iAimDist + 10:
            set_motor.RPM(0,0,0,0)
            break

#Offense & Defense
def AimBall(Ball) -> int:
    if Ball[1] < 0:
        iAngle = 180
    else:
        iAngle = 0
    try:
        if -(math.degrees(math.atan2(Ball[1],Ball[0])) - 90) < 0:
            return -(math.degrees(math.atan2(Ball[1],Ball[0])) - 90) + 360
        else:
            return -(math.degrees(math.atan2(Ball[1],Ball[0])) - 90)
    except:
        return 0

def GoBack():
    Pos2Pos(0,cfg.read("Position","Home"),False)

def GoX(iSpeed):
    set_motor.RPM(iSpeed,-iSpeed,-iSpeed,iSpeed)

def GoY(iSpeed):
    set_motor.RPM(iSpeed,iSpeed,iSpeed,iSpeed)

def Offence():
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    lPos = GetPos()
    iX,iY = lPos[0],lPos[1]

    iAbsBX = iX + iBX
    iAbsBY = iY + iBY

    set_io.out(13,1)
    set_io.out(14,0)

    if (iBX == 0 and iBY == 0) or (iX < -60 or iX > 60) or (iY < -80 or iY > 80):
        GoBack()
    elif 7 <= iBY <= 30:
        if -2 <= iBX <= 2:
            GoY(500)
            delay.ms(50)
            GoBack()
        elif iBX < -2:
            GoX(-50)
        elif iBX > 2:
            GoX(50)
    elif iBY > 30:
        if iBX < 0:
            iAimAngle = AimBall([iBX - 2,iBY - 10])
        elif iBX >= 0:
            iAimAngle = AimBall([iBX + 2,iBY - 10])
        car.z_move(0,iAimAngle,150)
    elif iBY <= -7:
        if iAbsBX < 0:
            iAimAngle = AimBall([iBX + 20,iBY - 10])
        elif iAbsBX >= 0:
            iAimAngle = AimBall([iBX - 20,iBY - 10])
        
        car.z_move(0,iAimAngle,150)
    
    print(iX,iY,iBX,iBY,iAbsBX,iAbsBY)

def Circle(origin:list[int,int],angle:int,r:int):
    Pos2Pos(
        angle,
        [origin[0]+((r**2)/((1+math.tan(angle)**2)))**0.5,
        origin[1]+(math.tan(angle)**-1)*((r**2)/((1+math.tan(angle)**2)))**0.5]
        ,False)

def Defence()->None:
    lBallPos = GetBallPos()
    lPos = GetPos()
    if -80 > lPos[1] > -50 or abs(lPos[0]) > 65 or (lBallPos[0]*lBallPos[1] == 0):
        Pos2Pos(0,cfg.read("Position","Home"),False)
    else:
        if lBallPos[0] > 0:
            car.z_move(0,90,5*lBallPos[0])
        else:
            car.z_move(0,-90,5*lBallPos[0])
        # Circle(cfg.read("Position","Home"),AimBall(cfg.read("Position","Home")),35)

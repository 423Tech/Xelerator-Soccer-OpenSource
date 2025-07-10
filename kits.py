import math
import time
import threading

from ReasonData import QkJson, logger
cfg = QkJson()

from chassis import Car,Peripherals
from headunit import Lidar,ArisuIntelligence
ArisuCam = ArisuIntelligence()
from ReasonBeacon import MisakaNetwork
Beacon = MisakaNetwork()
if cfg.read("model","Bit") == "AB":
    from arisbit import ArisBit
    Bits = ArisBit()
    lidar = Lidar(Bits.GetYaw)
    chassis = Car(Bits.SetMotor,Bits.GetYaw)
    compass = Bits.GetYaw
    peripheral = Peripherals(Bits.SetIO)
    logger.info("Arisu Bit loaded.")
# elif cfg.read("model","Bit") == "RB":
    # from ReasonBit import motor
    # from ReasonBit import compass
    # from ReasonBit import batt
    # chassis = Car(motor.RPM,compass.get)
    # logger.info("RoboMaster Bit loaded.")
else:
    logger.error("None Bit Model found.")
    # breakpoint()
    raise ImportError("None Bit Model found.")

SelfIP = cfg.read("WIFI","SelfIP")
peer_id = cfg.read("WIFI","RemoteIP") #Kei ID1 #Arisu ID
role = "DP"    # OP攻 DP守
Dribblingdistance = 9 # 控球距离
PosXCache = 0
PosYCache = 0

# Warned Flags
WarnedLidar = False

# Values for COM
SendstatusThreadFuncStarted = False
PeerstatusThreadFuncStarted = False
peer_role, peer_owner, P2BallDirect, P_Pos, Pbx, Pby= None, None, None, None, None, None

#Math Mod
#####################################################################################################
def GetBallDistance():
    bx, by = GetBallPos()
    x, y, *_ = GetPos()
    return (bx, by ,math.sqrt((bx - x) ** 2 + (by - y) ** 2))

def Role():
    if not PeerstatusThreadFuncStarted and not SendstatusThreadFuncStarted:
        Sendstatus()
        Peerstatus()
    else:
        pass

def SendstatusThreadFunc(): # 发送身份和球权
    while (1):
        SelfPosition = GetPos()
        try:
            msg = ("BallFlag:%s;PositionX:%s;PositionY:%s"%(BallFlag,SelfPosition[0],SelfPosition[1]))
            Beacon.Send(msg)
        except Exception as e:
            raise e

def Sendstatus():
    global SendstatusThreadFuncStarted
    if not SendstatusThreadFuncStarted:
        SendstatusThread = threading.Thread(target=SendstatusThreadFunc)
        SendstatusThread.daemon = True  # 设置为守护线程，主线程结束时自动结束
        SendstatusThread.start()
        SendstatusThreadFuncStarted = True
    return True

def PeerstatusThreadFunc():
    global BallFlag,PeerPosition
    while (1):
        MessageCache = Beacon.MessageCache
        if MessageCache == None:
            print("No BlueTooth Message")
            time.sleep(1)
        if MessageCache:
            try:
                for part in MessageCache.split(";"):
                    if part.startswith("BallFlag:"):
                        BallFlag = part.split(":")[1]
                    if part.startswith("PositionX:"):
                        PeerPositionX = int(part.split(":")[1])
                    if part.startswith("PositionY:"):
                        PeerPositionY = int(part.split(":")[1])
                PeerPosition = [PeerPositionX,PeerPositionY]
            except Exception as e:
                BallFlag = False
                PeerPosition = [1024,1024]
                print(f"Failed to send status: {e}")

def Peerstatus():# 解析对方身份球权距离
    global PeerstatusThreadFuncStarted
    if not PeerstatusThreadFuncStarted:
        PeerstatusThread = threading.Thread(target=PeerstatusThreadFunc)
        PeerstatusThread.daemon = True  # 设置为守护线程，主线程结束时自动结束
        PeerstatusThread.start()
        PeerstatusThreadFuncStarted = True


###################################################################################################
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

def linear_map(value, input_range, output_range):
    """
    通用线性映射函数
    
    Args:
        value: 要映射的值
        input_range: 输入范围 (min, max)
        output_range: 输出范围 (min, max)
    
    Returns:
        映射后的值
    """
    input_min, input_max = input_range
    output_min, output_max = output_range
    
    # 计算映射
    input_span = input_max - input_min
    output_span = output_max - output_min
    
    scaled_value = (value - input_min) / input_span
    mapped_value = output_min + (scaled_value * output_span)
    
    return mapped_value

#Value Mod

#TODO Need update
def GetBallPos():
    '''
    retrun a relative position of the ball
    [x,y]
    '''
    return ArisuCam.GetBallPos()

def GetBallAngle():
    '''
    retrun a angle of the ball
    '''
    ballX,ballY = ArisuCam.GetBallPos()
    if ballY == 0:
        return 0
    try:
        if -int(math.degrees(math.atan2(ballY,ballX)) - 90) < 0:
            ballRltAngle = -int(math.degrees(math.atan2(ballY,ballX)) - 90) + 360
        else:
            ballRltAngle = -int(math.degrees(math.atan2(ballY,ballX)) - 90)
        return ballRltAngle
    except ZeroDivisionError:
        return 0
    
def AbsBallAngle():
    '''
    retrun a absolute angle of the ball
    [x,y]
    '''
    BallAngleCache = GetBallAngle() + compass()
    if BallAngleCache > 360:
        return BallAngleCache - 360
    else:
        return BallAngleCache

def GetDistance() -> list[int,int,int]:
    '''
    获取激光雷达的距离数据
    '''
    return lidar.GetDists()

def GetPos(Fusion:bool | None = False) -> list[int,int]:
    global WarnedLidar
    Distance = GetDistance()
    if Distance == [0,0,0,0] and not WarnedLidar:
        WarnedLidar = True
        logger.error("Lidar Not Started")
        time.sleep(3)
        return [0,0,compass()]
    if WarnedLidar and Distance != [0,0,0,0]:
        WarnedLidar = False
        logger.success("Lidar Started")
    k = 10
    if Distance[0]+Distance[2] < (cfg.read("Position","Height") - 50)*k:
        if Distance[0] > Distance[2]:
            Y = cfg.read("Position","Height")*k/2 - Distance[0]
        else:
            Y = Distance[2] - cfg.read("Position","Height")*k/2 -100
    else:
        Y = ((cfg.read("Position","Height")*k/2 - Distance[0]) + (Distance[2] - cfg.read("Position","Height")*k/2))/2
    if Distance[1]+Distance[3] < (cfg.read("Position","Width") - 50)*k:
        if Distance[1] > Distance[3]:
            X = -(cfg.read("Position","Width")*k/2 - Distance[1]) - 50
        else:
            X = -(Distance[3] - cfg.read("Position","Width")*k/2) + 50
    else:
        X = -((cfg.read("Position","Width")*k/2 - Distance[1]) + (Distance[3] - cfg.read("Position","Width")*k/2))/2
    # PosXCache = X
    # PosYCache = Y
    return [X/10,Y/10,compass()]

def AbsBallPos():
    '''
    retrun a absolute position of the ball
    '''
    ballX,ballY = ArisuCam.GetBallPos()
    if [ballX,ballY] == [0,0]:
        return [1024,1024] #找不到球 特征值为1024，1024
    if abs(ballY-9) < 2 and abs(ballX) < 3:
        return [1207,1207] #持球状态下 特征值为12071207
    SelfX,SelfY,SelfZ = GetPos()
    ballDistance = math.sqrt(ballX**2 + ballY**2)
    if ballY == 0:
        ballRltAngle = 0
    try:
        ballRltAngle =  -int(math.degrees(math.atan2(ballY,ballX)) - 90)
    except ZeroDivisionError:
        ballRltAngle =  0
    BallAngleCache = ballRltAngle + SelfZ
    if BallAngleCache > 360:
        ballAbsAngle = BallAngleCache%360
    else:
        ballAbsAngle = BallAngleCache
    AbsBallPositon = [
        ballDistance * math.cos(math.radians(ballAbsAngle)) + SelfX,
        ballDistance * math.sin(math.radians(ballAbsAngle)) + SelfY
        ]
    return AbsBallPositon

def AbsChassisPos():
    ChassisRawList = ArisuCam.GetChassisPos()
    SelfX,SelfY,SelfZ = GetPos()
    OutputDistanceList = []
    for c in ChassisRawList:
        cDistance = math.sqrt(c[0]**2 + c[1]**2)
        if c[1] == 0:
            ChassisRltAngle = 0
        try:
            ChassisRltAngle =  -int(math.degrees(math.atan2(c[0],c[1])) - 90)
        except ZeroDivisionError:
            ChassisRltAngle =  0
        ChassisAngleAngle = ChassisRltAngle + SelfZ
        if ChassisAngleAngle > 360:
            ChassisAbsAngle = ChassisAngleAngle - 360
        else:
            ChassisAbsAngle = ChassisAngleAngle
        AbsChassisCache = [
            cDistance * math.cos(math.radians(ChassisAbsAngle)) + SelfX,
            cDistance * math.sin(math.radians(ChassisAbsAngle)) + SelfY,
            c[2],
            c[3]
            ]
        OutputDistanceList.append(AbsChassisCache)
    return OutputDistanceList

def getChassisAngle():
    '''
    ##### retrun a list of the relative angle of the chassis
    #### output [a1,a2,a3,etc]
    '''
    ChassisRawList = ArisuCam.GetChassisPos()
    ChassisAngleList = []
    for c in ChassisRawList:
        if c[1] == 0:
            return 0
        try:
            if -int(math.degrees(math.atan2(c[1],c[0])) - 90) < 0:
                ChassisRltAngle = -int(math.degrees(math.atan2(c[1],c[0])) - 90) + 360
            else:
                ChassisRltAngle = -int(math.degrees(math.atan2(c[1],c[0])) - 90)
            ChassisAngleList.append(ChassisRltAngle)
        except ZeroDivisionError:
            ChassisAngleList.append(0)
    return ChassisAngleList

def AbsChassisAngle():
    '''
    ##### retrun a list of the absolute angles of the chassis
    #### output [a1,a2,a3,etc]
    '''
    OutputAngles = []
    CompassCache = compass()
    for i in getChassisAngle():
        ChassisAngleCache = i + CompassCache
        if ChassisAngleCache > 360:
            OutputAngles.append(int(ChassisAngleCache)%360)
        else:
            OutputAngles.append(int(ChassisAngleCache))
    return OutputAngles

##################################################################################################################

def Lockballangle():#贝尔巴托夫转身
    lBallPos = GetBallPos()#获取球的位置
    iBX,iBY = lBallPos[0],lBallPos[1]#将球的位置赋值给iBX和iBY
    Compass = chassis.GetYaw()#获取机器人的航向
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = -(Angle - Compass)
    logger.debug("Ball Angle: %f" % Fangle)
    chassis.GoZ(Fangle)

def Lockballmove():
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    chassis.GoV(iBX*4,iBY*4,0)

def LockBallSlip():
    iBX,iBY = GetBallPos()
    Compass = chassis.GetYaw()
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = Angle + Compass
    if iBX > 75 or iBY > 75:
        Kp = 2
        KpZ = 0.3
    elif 25 < iBX <= 75 or 25 < iBY <= 75:
        Kp = 3
        KpZ = 0.5
    else:
        Kp = 4
        KpZ = 0.9

    SpeedX = iBX * Kp
    SpeedY = iBY * Kp
    # if SpeedX > 300:
    #     SpeedX = 300
    # if SpeedY > 300:
    #     SpeedY = 300
    # if SpeedX < -300:
    #     SpeedX = -300
    # if SpeedY < -300:
    #     SpeedY = -300
    chassis.GoV(SpeedX,SpeedY,Fangle,KpZ) # 1.5 is a factor to make the robot turn faster, you can adjust it as needed

def NormalShoot():
    BX, BY = GetBallPos()
    logger.debug("Current Position: %s" % [BX, BY])
    if BX == 0 and BY == 0:
        logger.info("Ball not found, stopping chassis.")
        Pos2Pos([0, -85, 0], False)
        peripheral.Dribble(False)
    elif -5 < BX < 5 and 0 < BY < 10:
        logger.info("Ball is in front")
        for _ in range(20):
            BX, BY = GetBallPos()
            if not -5 < BX < 5 and 0 < BY < 10:
                break
            X,Y,_ = GetPos()
            DeltaY = 100 - Y
            DeltaX = X
            Theta = math.atan2(DeltaY, DeltaX)
            Theta = math.degrees(Theta)
            Compass = -(90 - Theta)
            # while True:
            #     chassis.GoZ(Compass)
            chassis.GoY(Compass,50)
            time.sleep(0.03)
        peripheral.ShootBall()
    else:
        peripheral.Dribble(True)
        LockBallSlip()

def Circle(origin:list[int,int],angle:int,r:int):
    Pos2Pos(
        [origin[0]+((r**2)/((1+math.tan(angle)**2)))**0.5,
        origin[1]+(math.tan(angle)**-1)*((r**2)/((1+math.tan(angle)**2)))**0.5,
        angle]
        ,False)

##################################################################################################################

#Operate models
# 定义一个函数，用于判断是否覆盖
def Cover2Start():
    # 声明一个全局变量
    global bCovered
    # 如果距离小于10或者已经覆盖，则返回True
    if GetDistance()[0] < 10 or bCovered:
        bCovered = True
        return True
    # 否则返回False
    else:
        bCovered = False
        return False
    
def AvoidOutOfRange(InputPos:list[int,int,int]) -> list[int,int,int]:
    InputX,InputY,InputZ = InputPos
    if InputX > 0:
        kX = 1
    else:
        kX = -1
    if InputY > 0:
        kY = 1
    else:
        kY = -1
    if abs(InputX) > (cfg.read("Border","0")[0]):
        OutX = (cfg.read("Border","0")[0])*kX
    else:
        OutX = InputX
    if abs(InputY) > (cfg.read("Border","0")[1]):
        OutY = (cfg.read("Border","0")[1])*kY
    else:
        OutY = InputY
    OutZ = abs(InputZ%360)
    logger.success("Fixed Position: [%s,%s,%s]"%(OutX,OutY,OutZ))
    return [OutX,OutY,OutZ]

def AvoidObject():
    '''
    '''
    pass
    
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

def Pos2Pos(lAimPos:list[int,int,int], A2O:bool | None = False, Speed:int | None = None) -> int:
    '''
    iFacingAngle 移动时面对的方向 0~360
    lAimPos 目标坐标位置 如[0,0] 距离越近速度越小
    A2O 是否开启自动避障 默认True
    '''
    iAimX,iAimY,iAimZ = AvoidOutOfRange(lAimPos)
    iLocX,iLocY,iLocZ = GetPos()
    if iLocX < 0:
        kX = -1
    else:
        kX = 1
    if iLocY < 0:
        kY = -1
    else:
        kY = 1
    iDeltaX = (iAimX) - (iLocX)
    iDeltaY = (iAimY) - (iLocY)
    RestrictedX = cfg.read("Border","1")[0]
    RestrictedY = cfg.read("Border","1")[1]
    try:
        try:
            Slope = iDeltaX/iDeltaY
        except ZeroDivisionError:
            Slope = 1
        if Slope*RestrictedY > RestrictedX:
            iAimX = (RestrictedX - 3)*kX
        if Slope/RestrictedX > RestrictedY:
            iAimY = (RestrictedY - 3)*kY
    except:
        iAimX,iAimY,iAimZ = lAimPos
    logger.info([iAimX,iAimY,iAimZ])
    if iLocZ > 180:
        iDeltaZ = 360 - abs(iAimZ) - abs(iLocZ)
    else:
        iDeltaZ = (abs(iAimZ) - abs(iLocZ))
    logger.debug([iDeltaX,iDeltaY,iDeltaZ])
    linear_map(iDeltaX,[0,300],[150,230])
    linear_map(iDeltaY,[0,300],[150,230])
    iErrorRange = cfg.read("Position","ErrorRange")/4
    iMovedAngle = int(math.degrees(math.atan2(iDeltaY,iDeltaX)))
    if A2O:
        DistanceCache = GetDistance()
        if 0 < iMovedAngle%90 <= 1 :
            if DistanceCache[0] <= DistanceCache[1]:
                Anglek = 1
            else:
                AngleK = -1
        elif 1 < iMovedAngle%90 <= 2 :
            if DistanceCache[0] >= DistanceCache[3]:
                Anglek = 1
            else:
                AngleK = -1
        elif 2 < iMovedAngle%90 <= 3 :
            if DistanceCache[3] >= DistanceCache[2]:
                Anglek = 1
            else:
                AngleK = -1
        elif 3 < iMovedAngle%90 <= 4 :
            if DistanceCache[2] >= DistanceCache[1]:
                Anglek = 1
            else:
                AngleK = -1
        for a in AbsChassisAngle():
            if a == iMovedAngle:
                iMovedAngle = iMovedAngle + int((abs(iDeltaX)+abs(iDeltaY))*1.5)*-Anglek
    if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY) and abs(iErrorRange) > iDeltaZ:
        chassis.stop()
        return True
    elif iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY) and not abs(iErrorRange) > abs(iDeltaZ):
        chassis.GoZSpeed(iDeltaZ)
    else:
        if Speed:
            chassis.GoA(lAimPos[2],90-iMovedAngle,Speed)
        else:
            chassis.GoA(lAimPos[2],90-iMovedAngle,int((abs(iDeltaX)+abs(iDeltaY))*1.5))
        return False

def Move2Path(Posistions:list[list[int,int,int],list[int,int,int]],iWaitMs:int,A2O:bool | None = False):
    iErrorRange = cfg.read("Position","ErrorRange")/2
    for i in Posistions:
        while (1):
            iAimX = i[0]
            iAimY = i[1]
            iAimZ = i[2]
            lLocal = GetPos()
            iLocX = lLocal[0]
            iLocY = lLocal[1]
            iLocZ = lLocal[2]
            iDeltaX = iAimX - iLocX
            iDeltaY = iAimY - iLocY
            iDeltaZ = iAimZ - iLocZ
            if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY) and iErrorRange > abs(iDeltaZ):
                if i == Posistions[-1]:
                    return True
                else:
                    time.sleep(iWaitMs)
                    break
            else:
                Pos2Pos(lAimPos=i,A2O=A2O)

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
            chassis.SetMotor(iDirectionFactor * 30,-iDirectionFactor * (130 - iDeltaAngle),-iDirectionFactor * 30,iDirectionFactor * (130 - iDeltaAngle))
    chassis.GoZ(iAimAngle)
    while(1):
        iBX = GetBallPos()[0]
        if iBX <= -2:
            print('atleft')
            chassis.GoA(iAimAngle,iAimAngle + 90,-20)
#            chassischassis.SetMotor(-30,30,30,-30)
        elif iBX >= 2:
            print('atright')
            chassis.GoA(iAimAngle,iAimAngle + 90,20)
#            chassis.SetMotor(30,-30,-30,30)
        else:
            for _ in range(3):
                chassis.stop()
            break
    print('stopped')

def TurnToTheBall():
    while(1):
        lBallPos = GetBallPos()
        iX, iY = lBallPos[0], lBallPos[1]
        if -2 <= iX <= 2 and iY > 0:
            chassis.stop()
            break
        else:
            chassis.SetMotor(20,20,-20,-20)

def AutoFetch(bStop = True):
    TurnToTheBall()
    while(1):
        lBallPos = GetBallPos()
        iBX, iBY = lBallPos[0], lBallPos[1]
        SpeedL = 30 + 3 * iBX
        SpeedR = 30 - 3 * iBX
        chassis.SetMotor(SpeedL, SpeedL, SpeedR, SpeedR)
        if iBX > -2 and iBX < 2 and iBY >= 7 and iBY <= 9:
            if bStop:
                chassis.stop()
            break

def Move2Pos(lPos):
    while Pos2Pos(lPos,False):
        chassis.stop()
        break
    # for _ in range(3):
    #     chassis.SetMotor(0,0,0,0)

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
        chassis.SetMotor(x,y,z,w)
    elif( a == -1 ): #反
        chassis.SetMotor(z,w,x,y)
    else:
        chassis.stop()
    length = r * iRad  # 弧长
    Ktime = length / iSpeed
    time.sleep(Ktime/100)
    chassis.stop

def GoDistance(iDistance):
    iDistance = iDistance * 10
    iCompass = int(compass())
    
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
    
    iAimDist = GetDistance()[iFacingDistIndex] - iDistance
    
    while(1):
        chassis.GoA(0,iMovingAngle, 20)
        iCurrentDist = GetDistance()[iFacingDistIndex]
        print(iCurrentDist,iAimDist)
        if iCurrentDist < iAimDist + 10:
            chassis.stop()
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
    Pos2Pos(cfg.read("Position","Home"),False)

def Offence_O():
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    lPos = GetPos()
    iX,iY = lPos[0],lPos[1]

    iAbsBX = iX + iBX
    iAbsBY = iY + iBY

    peripheral.DribbleBall()

    if (iBX == 0 and iBY == 0) or (iX < -60 or iX > 60) or (iY < -80 or iY > 80):
        GoBack()
    elif 7 <= iBY <= 30:
        if -2 <= iBX <= 2:
            chassis.GoY(0,500)
            time.sleep(0.05)
            GoBack()
        elif iBX < -2:
            chassis.GoX(0,-50)
        elif iBX > 2:
            chassis.GoX(0,50)
    elif iBY > 30:
        if iBX < 0:
            iAimAngle = AimBall([iBX - 2,iBY - 10])
        elif iBX >= 0:
            iAimAngle = AimBall([iBX + 2,iBY - 10])
        chassis.GoA(0,iAimAngle,150)
    elif iBY <= -7:
        if iAbsBX < 0:
            iAimAngle = AimBall([iBX + 20,iBY - 10])
        elif iAbsBX >= 0:
            iAimAngle = AimBall([iBX - 20,iBY - 10])
        
        chassis.GoA(0,iAimAngle,150)

def Offence():
    """
    OP进攻逻辑
    1. 默认在前半场，实时追球，首要目标是抢球。
    2. 得到球权时，判断位置，有则溜边/弹射/澳门射等，无则找球。
    3. 若未检测到球 退至中场线与己方半场交界处或回防转DP。
    4. 绝不进入己方禁区防守区域。
    """
    BallX, BallY = AbsBallPos()
    LocalX, LocalY,Yaw = GetPos()
    # 中场
    if [BallX,BallY] == [1024,1024]:   
        peripheral.StopDribble()
        Pos2Pos([0, -50, 0], False)
    if ball_owner == SelfIP:
        peripheral.Dribble(True)
        Slipsideshot(Yaw,[LocalX,LocalY],[0,0],[0,100])
    else: #无球权
        if BallY < 0:
            Pos2Pos([LocalX, 0, 0], False)
        else:
            LockBallSlip()
    print(Yaw,BallX, BallY,LocalX, LocalY,ball_owner)


def Circle(origin:list[int,int],angle:int,r:int):
    Pos2Pos(
        [origin[0]+((r**2)/((1+math.tan(angle)**2)))**0.5,
        origin[1]+(math.tan(angle)**-1)*((r**2)/((1+math.tan(angle)**2)))**0.5,
        angle]
        ,False)

# def Defence()->None:
#     lBallPos = GetBallPos()
#     lPos = GetPos()
#     logger.debug("Ball Position: %s, Local Position: %s" % (lBallPos,lPos))
#     if -80 > lPos[1] > -50 or abs(lPos[0]) > 65 or (lBallPos[0]*lBallPos[1] == 0):
#         Pos2Pos(cfg.read("Position","Home"),False)
#     else:
        
#         # if lBallPos[0] > 0:
#             # chassis.GoA(0,90,100)
#         # else:
#         chassis.GoA(0,90,lBallPos[0]*4)
#         # Circle(cfg.read("Position","Home"),AimBall(cfg.read("Position","Home")),35)

###############################################################################################
def MacaoShot(x,y,z): 
    #等待修改
    if chassis.GetYaw is None:
        return False
    Yaw = chassis.GetYaw()
    peripheral.DribbleBall()
    lLocal = GetPos()
    iLocX = lLocal[0]
    iLocY = lLocal[1]
    # # time.sleep(0.1)
    # # iLocX1 = lLocal[0]
    # # iLocY1 = lLocal[1]
    # # print((iLocX+iLocX1)/2,(iLocY+iLocY1)/2)
    Pos2Pos([x,y,0],False,200)
    logger.warning("Current Position: %s" % [iLocX,iLocY])
    if abs(abs(iLocX) - abs(x)) < 10 and abs(abs(iLocY) - abs(y)) < 10:
        if iLocX > 0:
            target_angle1 = 110
            target_angle = 40
            while True:
                Yaw = (chassis.GetYaw() + 180)%360
                chassis.GoZspeed(-50)
                if abs(Yaw - target_angle1) < 8:
                    break
            chassis.GoZspeed(0)
            time.sleep(1)
            while True:
                Yaw = (chassis.GetYaw() + 180)%360
                speed = z
                chassis.SetMotor(speed+100,speed+100,-speed,-speed)
                if abs(Yaw - target_angle)< 10:
                    break
            while True:
                Yaw = (chassis.GetYaw() + 180)%360
                chassis.GoZspeed(200)
                if abs(Yaw) < 10:
                    break
            return
        else:
            target_angle1 = 250
            target_angle = 320

            while True:
                Yaw = (chassis.GetYaw() + 180)%360
                chassis.GoZspeed(50)
                if abs(Yaw - target_angle1) < 8:
                    break
            chassis.GoZspeed(0)
            time.sleep(1)
            while True:
                Yaw = (chassis.GetYaw() + 180)%360
                speed = z
                chassis.SetMotor(-speed,-speed,speed+100,speed+100)
                if abs(Yaw - target_angle) < 10:
                    break
            while True:
                Yaw = (chassis.GetYaw() + 180)%360
                chassis.GoZspeed(-200)
                if abs(Yaw) < 10:
                    break
            return

                    
def Slipsideshot(EnemyPos,GoalPos): #溜边 10,-90
    '''
    #### Yaw : 指南针 
    ##### <code>Yaw: int | [0,360]</code>
    #### LocalPos : 本地坐标 
    ##### <code>LocalPos: list | [[-80,80],[-100,100],[0,360]]</code>
    ### EnemyPos : 敌人坐标
    ### GoalPos : 球门坐标
    '''
    # peripheral.Dribble(True)
    LocalPos = GetPos()
    LocalX,LocalY,_ = LocalPos
    EnemyX,EnemyY = EnemyPos
    _ , GoalY = GoalPos
    GoalY = 80
    AimX  = 40
    AimY  = 80
    if LocalX > 0:
        k = 45
    else:
        AimX = -AimX
        k = -45
    Angle = (math.degrees(math.atan2(LocalX - EnemyX, LocalY - EnemyY)-270)) % 360
    Pos2Pos([AimX,AimY,Angle],False,200)
    if abs(AimX-LocalX)+abs(AimX-LocalX) < 5:
        DeltaY = LocalY - GoalY
        DeltaX = LocalX
        Theta =((math.degrees(math.atan2(DeltaX, DeltaY)-270)) % 360) + 180 +k
        Compass = Theta
        for _ in range(20):
            # if not AbsBallPos() == [1207, 1207]:
            #     break
            chassis.GoZ(Compass)
            time.sleep(0.03)
        peripheral.ShootBall()
        logger.success("Ball is in possession, start shotting.")

def OHMYBACK():
    #正常
    peripheral.Dribble(True)
    lLocal = GetPos()
    iLocX = lLocal[0]
    iLocY = lLocal[1]
    ALocal = [0,0]
    ALocX = ALocal[0]
    ALocY = ALocal[1]
    Angle = (math.degrees(math.atan2(iLocX - ALocX, iLocY - ALocY)-270)) % 360
    Pos2Pos([0,70,Angle],False)

def LockDoor():
    #正常
    LocalPos = GetPos()
    GoalPos = [0, 90]
    LocalX,LocalY,_ = LocalPos
    _ ,GoalY = GoalPos
    DeltaY = LocalY - GoalY
    DeltaX = LocalX
    Theta =((math.degrees(math.atan2(DeltaX, DeltaY)-270)) % 360) + 180
    chassis.GoZ(Theta)

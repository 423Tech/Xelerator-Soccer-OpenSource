import math
import time

from ReasonData import QkJson, logger, Positions
cfg = QkJson()

from chassis import Car,Peripherals
from headunit import Lidar,ArisuIntelligence
ArisuCam = ArisuIntelligence()
from ReasonBeacon import BTBeacon
Beacon = BTBeacon()
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

def GetBallDistance():
    ballX,ballY = ArisuCam.GetBallPos()
    return math.sqrt(ballX**2 + ballY**2)

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

def GetPos() -> list[int,int]:
    Distance = GetDistance()
    if Distance[0]+Distance[2] < (cfg.read("Position","Height") - 35):
        if Distance[0] > Distance[2]:
            Y = cfg.read("Position","Height")/2 - Distance[0]
        else:
            Y = Distance[2] - cfg.read("Position","Height")/2
    else:
        Y = ((cfg.read("Position","Height")/2 - Distance[0]) + (Distance[2] - cfg.read("Position","Height")/2))/2
    if Distance[1]+Distance[3] < (cfg.read("Position","Width") - 35):
        if Distance[1] > Distance[3]:
            X = -(cfg.read("Position","Width")/2 - Distance[1])
        else:
            X = -(Distance[3] - cfg.read("Position","Width")/2)
    else:
        X = -((cfg.read("Position","Width")/2 - Distance[1]) + (Distance[3] - cfg.read("Position","Width")/2))/2
    return [X/10,Y/10,compass()]

def AbsBallPos():
    '''
    retrun a absolute position of the ball
    '''
    ballX,ballY = ArisuCam.GetBallPos()
    SelfX,SelfY,SelfZ = GetPos()
    ballDistance = math.sqrt(ballX**2 + ballY**2)
    if ballY == 0:
        ballRltAngle = 0
    try:
        if -int(math.degrees(math.atan2(ballY,ballX)) - 90) < 0:
            ballRltAngle = -int(math.degrees(math.atan2(ballY,ballX)) - 90) + 360
        else:
            ballRltAngle = -int(math.degrees(math.atan2(ballY,ballX)) - 90)
    except ZeroDivisionError:
        ballRltAngle =  0
    BallAngleCache = (ballRltAngle + compass())%360
    AbsBallPositon = [
        int(ballDistance * math.sin(math.radians(BallAngleCache))+SelfX),
        int(ballDistance * math.cos(math.radians(BallAngleCache))+SelfY)
        ]
    PosCache = Positions(
        BallXPosition = AbsBallPositon[0],
        BallYPosition = AbsBallPositon[1],
        XPosition = SelfX,
        YPosition = SelfY,
        ZPosition = SelfZ,
        Tick = time.time()
    )
    PosCache.save()
    return AbsBallPositon


#Operate models
def RailGun():
    peripheral.ShootBall()

def Cover2Start():
    global bCovered
    if GetDistance()[0] < 10 or bCovered:
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
        chassis.GoV(0,-iMoveAngle,200)
    except:
        chassis.stop()

def ObtDetect() -> list[list[int,int],list[bool,bool]]:
    '''
    返回一个列表，[[角度],[是否被遮挡]]
    '''
    global lBlockedMemo,iMemoLife,bLife
    lStatusOfDist = [[],[]]
    # iMaxLife = cfg.read("A2AOb","LifeTime")
    lDists = GetDistance()
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
    return None

def AvoidObt(iFacingAngle: int | None = 0,iTargetAngle:int | None = 0,iSpeed:int | None = 150) -> None:
    '''
    iFacingAngle 移动时面对的方向 0~360
    iTargetAngle 需要移动的方向 可能不采用 -180~180
    iSpeed 移动的速度 默认150
    已弃用
    '''
    return 0
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
        chassis.GoV(iFacingAngle,iAimAngle,iSpeed)
        # c.GoA(iFacingAngle,iAimAngle,200)
    except:
        chassis.stop()
    

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

def Pos2Pos(lAimPos:list[int,int,int], A2O:bool | None = False) -> int:

    '''
    iFacingAngle 移动时面对的方向 0~360
    lAimPos 目标坐标位置 如[0,0] 距离越近速度越小
    A2O 是否开启自动避障 默认True
    '''
    # AvoidOutBorder()
    iAimX = lAimPos[0]
    iAimY = lAimPos[1]
    iAimZ = lAimPos[2]
    # time.sleep(0.01)
    lLocal = GetPos()
    iLocX = lLocal[0]
    iLocY = lLocal[1]
    iLocZ = lLocal[2]
    iDeltaX = iAimX - iLocX
    iDeltaY = iAimY - iLocY
    iDeltaZ = iAimZ - iLocZ
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
        if iErrorRange > iDeltaX > -iErrorRange and iErrorRange > iDeltaY > -iErrorRange and iErrorRange > iDeltaZ > -iErrorRange:
            chassis.stop()
        else:
            if 0 > iDeltaX:
                PA = Local2Angle(lAimPos) + 180
            else:
                PA = Local2Angle(lAimPos)
            if 0 > iDeltaY:
                PA = Local2Angle(lAimPos) - 180
            AvoidObt(lAimPos[2],PA,(abs(iDeltaX) - abs(iDeltaY))/1.3)
    else:
        if iErrorRange > iDeltaX > -iErrorRange and iErrorRange > iDeltaY > -iErrorRange and iErrorRange > iDeltaZ > -iErrorRange:
            chassis.stop()
            return True
        else:
        # chassis.GoZ(iFacingAngle)
            # Go2(iFacingAngle,iDeltaX,iDeltaY)
            if iDeltaY > 0:
                iAngle = 180
            else:
                iAngle = 0
            iMovedAngle = int(math.degrees(math.atan2(iDeltaY,iDeltaX)))
            chassis.GoA(lAimPos[2],90-iMovedAngle,int((abs(iDeltaX)+abs(iDeltaY)/2)))
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
            iDeltaX = iAimX - iLocX
            iDeltaY = iAimY - iLocY
            if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY):
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
    while not Pos2Pos(lPos,False):
        pass
    for _ in range(3):
        chassis.SetMotor(0,0,0,0)

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
        chassis.straight(iMovingAngle, 20)
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

def Offence():
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
    

def Circle(origin:list[int,int],angle:int,r:int):
    Pos2Pos(
        [origin[0]+((r**2)/((1+math.tan(angle)**2)))**0.5,
        origin[1]+(math.tan(angle)**-1)*((r**2)/((1+math.tan(angle)**2)))**0.5,
        angle]
        ,False)

def Defence()->None:
    lBallPos = GetBallPos()
    lPos = GetPos()
    logger.debug("Ball Position: %s, Local Position: %s" % (lBallPos,lPos))
    if -80 > lPos[1] > -50 or abs(lPos[0]) > 65 or (lBallPos[0]*lBallPos[1] == 0):
        Pos2Pos(cfg.read("Position","Home"),False)
    else:
        
        # if lBallPos[0] > 0:
            # chassis.GoA(0,90,100)
        # else:
        chassis.GoA(0,90,lBallPos[0]*4)
        # Circle(cfg.read("Position","Home"),AimBall(cfg.read("Position","Home")),35)

# -*- coding: utf-8 -*-

import math
import time

from ReasonData import QkJson, logger
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

SelfID = cfg.read("model","number") # 机器人编号 1/2
role = cfg.read("model","type") # 攻防身份 OP攻 DP守
ball_owner = 0 # 0无球权 1，2对应机器有球权
Dribblingdistance = 9 # 控球距离

#Math Mod
def get_ball_distance():
    bx, by = GetBallPos()
    x, y, *_ = GetPos()
    return math.sqrt((bx - x) ** 2 + (by - y) ** 2)

def SendStatus(): # 发送身份和球权
    try:
        my_dist = get_ball_distance()
        msg = f"ROLE:{role};OWNER:{ball_owner};DIST:{my_dist:.2f}"
        Beacon.Send(msg)
    except Exception as e:
        logger.error(f"Failed to send status: {e}")

def PeerStatus():# 解析对方身份球权距离
    msg = Beacon.MessageCache
    peer_role, peer_owner, peer_dist = None, None, None
    if msg:
        try:
            for part in msg.split(";"):
                if part.startswith("ROLE:"):
                    peer_role = part.split(":")[1]
                if part.startswith("OWNER:"):
                    peer_owner = int(part.split(":")[1])
                if part.startswith("DIST:"):
                    peer_dist = float(part.split(":")[1])
        except Exception:
            pass
    return peer_role, peer_owner, peer_dist


def IdentitySwitch():
    global role, ball_owner,Dribblingdistance
    Dribblingdistance = 9
    lBallPos = GetBallPos()
    lPos = GetPos()
    bx, by = lBallPos[0], lBallPos[1]
    x, y = lPos[0], lPos[1]
    Mydist = math.sqrt((bx - x) ** 2 + (by - y) ** 2)
    peer_role, peer_owner, Peerdist = PeerStatus()
    bluetooth_disconnected = (Beacon.MessageCache is None) or (Beacon.MessageCache == "")
    # 球权
    if get_ball_distance() < Dribblingdistance and (bx != 0 and by != 0):
        ball_owner = SelfID
    else:
        ball_owner = 0
    # 攻防身份
    if by > 0:
        if bluetooth_disconnected:
            role = "DP"
        else:
            if Peerdist is not None:
                role = "OP" if Mydist < Peerdist else "DP"
            else:
                role = "OP" 
    elif by < 0:
        if Peerdist is not None and abs(Mydist - Peerdist) < 2:  
            pass
        else:
            role = "DP"
    # 3. 球在己方半场且距离相等，先到先得（默认不变）
    SendStatus()

#球权不等于攻防身份

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
    logger.debug("Ball Position: %s" % [ballX, ballY])
    if ballX == 0 and ballY == 0:
        return [0, 0]
    if abs(ballY) <= 10 and abs(ballX) == 0:
        ball_owner = SelfID
        return [1207, 1207]
    SelfX,SelfY,SelfZ = GetPos()
    ballDistance = math.sqrt(ballX**2 + ballY**2)
    if ballY == 0:
        ballRltAngle = 0
    try:
        ballRltAngle =  -int(math.degrees(math.atan2(ballY,ballX)) - 90)
    except ZeroDivisionError:
        ballRltAngle =  0
    BallAngleCache = ballRltAngle + compass()
    if BallAngleCache > 360:
        ballAbsAngle = BallAngleCache - 360
    else:
        ballAbsAngle = BallAngleCache
    AbsBallPositon = [
        ballDistance * math.cos(math.radians(ballAbsAngle)) + SelfX,
        ballDistance * math.sin(math.radians(ballAbsAngle)) + SelfY
        ]
    return AbsBallPositon

##################################################################################################################

def Lockball________angle():#贝尔巴托夫转身
    lBallPos = GetBallPos()#获取球的位置
    iBX,iBY = lBallPos[0],lBallPos[1]#将球的位置赋值给iBX和iBY
    Compass = chassis.GetYaw()#获取机器人的航向
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = -(Angle - Compass)
    logger.debug("Ball Angle: %f" % Fangle)
    chassis.GoZ(Fangle)

def Lockballangle():
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    Compass = chassis.GetYaw()
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = Angle + Compass
    chassis.GoZ(Fangle) # 1.5 is a factor to make the robot turn faster, you can adjust it as needed

def Lockballmove():
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    # if iBX > 0:
    #     iBX=linear_map(iBX,(0,140),(60,80))
    # else:
    #     iBX=linear_map(iBX,(-140,0),(-80,-60))
    # if iBY > 0:
    #     iBY=linear_map(iBY,(0,140),(60,80))
    # else:
    #     iBY=linear_map(iBY,(-140,0),(-80,-60))
    chassis.GoV(iBX*4,iBY*4,0)

def Lockballslip():
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    Compass = chassis.GetYaw()
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = Angle + Compass
    chassis.GoV(iBX*3,iBY*3,Fangle) # 1.5 is a factor to make the robot turn faster, you can adjust it as needed

##每
def Offence():#1200 400
    IdentitySwitch()
    lBallPos = AbsBallPos()
    lPos = GetPos()
    bx, by = lBallPos[0], lBallPos[1]
    x, y = lPos[0], lPos[1]
    # 中场
    if bx == 0 and by == 0:   
            peripheral.StopDribble()
            Pos2Pos([0, -50, 0], False)
            return   
    if ball_owner == SelfID:
        # 球在己方半场，优先溜边
        if abs(bx) > 50:
            Slipsideshot()
            return
        elif(abs(bx) <= 50 and by < 0):
            MacaoShot(300)
        elif(abs(bx) <= 50 and by > 0):
            if by > 50:
                Angle = math.degrees(math.atan2(abs(x),120-y))
                while True:
                    if abs(compass()-Angle) < 10:
                        chassis.stop()
                        peripheral.ShootBall()
                        break
                    elif x > 0:
                        chassis.GoZspeed(-150)
                    else:
                        chassis.GoZspeed(150)
            else:
                peripheral.StopDribble()
                Pos2Pos([0, -50, 0], False)
                return   
        else:
            peripheral.StopDribble()
            Pos2Pos([0, -50, 0], False)
            return   
    else:
        peripheral.DribbleBall()
        Lockballslip()
        return
    Lockballslip()





##################################################################################################################

#Operate models
# 定义RailGun函数
def RailGun():
    # 调用peripheral模块中的ShootBall函数
    peripheral.ShootBall()

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
            if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY) and iErrorRange > abs(iAimZ - lLocal[2]):
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

    # iAbsBX = iX + iBX
    # iAbsBY = iY + iBY
    iAbsBX, iAbsBY = AbsBallPos()
    peripheral.DribbleBall()

    if (iAbsBX == 0 and iAbsBX == 0) or (iX < -60 or iX > 60) or (iY < -80 or iY > 80):
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

###############################################################################################
def MacaoShot(x,y,z): 
    if chassis.GetYaw is None:
        return False
    Yaw = chassis.GetYaw()
    peripheral.DribbleBall()
    lAimPos = [x,y,0]
    lLocal = GetPos()
    iLocX = lLocal[0]
    iLocY = lLocal[1]
    # # time.sleep(0.1)
    # # iLocX1 = lLocal[0]
    # # iLocY1 = lLocal[1]
    # # print((iLocX+iLocX1)/2,(iLocY+iLocY1)/2)
    Pos2Pos([lAimPos[0],lAimPos[1],0],False)
    if abs(iLocX - lAimPos[0]) < 10 and abs(iLocY - lAimPos[1]) < 10:
        if iLocX > 0:
            target_angle1 = 70
            target_angle = 140
            target_angle2 = 0 
            while True:
                Yaw = chassis.GetYaw()
                chassis.GoZspeed(50)
                if abs((Yaw - target_angle1 + 180) % 360 - 180) < 8:
                    break
            chassis.GoZspeed(0)
            time.sleep(0.3)
            while True:
                Yaw = chassis.GetYaw()
                speed = z
                chassis.SetMotor(speed+100,speed+100,-speed,-speed)
                if abs((Yaw - target_angle + 180) % 360 - 180) < 20:
                    break
            peripheral.StopDribble()
            while True:
                Yaw = chassis.GetYaw()
                chassis.GoZspeed(-200)
                if abs((Yaw - target_angle2 + 180) % 360 - 180) < 30:
                    break
            peripheral.StopDribble()
        else:
            target_angle1 = 290
            target_angle = 220
            target_angle2 = 0 
            while True:
                Yaw = chassis.GetYaw()
                chassis.GoZspeed(-50)
                if abs((Yaw - target_angle1 + 180) % 360 - 180) < 8:
                    break
            chassis.GoZspeed(0)
            time.sleep(0.3)
            while True:
                Yaw = chassis.GetYaw()
                speed = z
                chassis.SetMotor(-speed,-speed,speed+100,speed+100)
                if abs((Yaw - target_angle + 180) % 360 - 180) < 20:
                    break
            peripheral.StopDribble()
            while True:
                Yaw = chassis.GetYaw()
                chassis.GoZspeed(200)
                if abs((Yaw - target_angle2 + 180) % 360 - 180) < 30:
                    break
            peripheral.StopDribble()

def Slipsideshot():
    pass

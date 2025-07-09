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

my_id = 1 #Arisu ID
peer_id = 2 #Kei ID
role = "DP"    # OP攻 DP守
ball_owner = 0 # 0无球权 1，2对应机器有球权
Dribblingdistance = 9 # 控球距离
PosXCache = 0
PosYCache = 0

#Math Mod
#####################################################################################################

def get_ball_distance():
    bx, by = GetBallPos()
    x, y, *_ = GetPos()
    return math.sqrt((bx - x) ** 2 + (by - y) ** 2)

def Sendstatus(): # 发送身份和球权
    try:
        P2Ball = get_ball_distance()
        P_Pos =  GetPos()
        msg = f"ROLE:{role};OWNER:{ball_owner};P2Ball:{P2Ball:.2f};P_Pos:{P_Pos:.2f}"
        Beacon.Send(msg)
    except Exception as e:
        logger.error(f"Failed to send status: {e}")

def Peerstatus():# 解析对方身份球权距离
    msg = Beacon.MessageCache
    peer_role, peer_owner, P2Ball, P_Pos = None, None, None, None
    if msg:
        try:
            for part in msg.split(";"):
                if part.startswith("ROLE:"):
                    peer_role = part.split(":")[1]
                if part.startswith("OWNER:"):
                    peer_owner = int(part.split(":")[1])
                if part.startswith("P_Pos:"):
                    P_Pos = float(part.split(":")[1])
                if part.startswith("P2Ball:"):
                    P2Ball = float(part.split(":")[1])
        except Exception:
            pass
    return peer_role, peer_owner, P2Ball, P_Pos


def Identityswitch(): #切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切切换
    global role, ball_owner,Dribblingdistance
    Dribblingdistance = 9
    lBallPos = GetBallPos()
    lPos = GetPos()
    bx, by = lBallPos[0], lBallPos[1]
    x, y = lPos[0], lPos[1]
    My2Ball = math.sqrt((bx - x) ** 2 + (by - y) ** 2)
    peer_role, peer_owner, P2Ball, P_Pos = Peerstatus()
    bluetooth_disconnected = (Beacon.MessageCache is None) or (Beacon.MessageCache == "")
    # 球权
    if get_ball_distance() < Dribblingdistance and (bx != 0 and by != 0):
        ball_owner = my_id
    else:
        ball_owner = 0
    # 攻防身份
    if by > 0:
        if bluetooth_disconnected:
            role = "DP"
        else:
            if P2Ball is not None:
                role = "OP" if My2Ball < P2Ball else "DP"
            else:
                role = "OP" 
    elif by < 0:
        if bluetooth_disconnected:
            role = "DP"
        else:
            if P2Ball is not None and abs(My2Ball - P2Ball) < 5:
                pass
            else:
                role = "DP" 
    # 3. 球在己方半场且距离相等，先到先得（默认不变）
    Sendstatus()


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

def GetPos(Fusion:bool | None = False) -> list[int,int]:
    Distance = GetDistance()
    # logger.debug(Distance)
    if Distance == [0,0,0,0]:
        logger.error("Lidar Not Started")
        return [0,0,compass()]
    # global PosXCache, PosYCache
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
    return [X*0.85/10,Y*0.85/10,compass()]


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
    logger.warning(lBallPos)
    iBX,iBY = lBallPos[0],lBallPos[1]
    Compass = chassis.GetYaw()
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = Angle + Compass
    chassis.GoV(iBX*5,iBY*5,Fangle) # 1.5 is a factor to make the robot turn faster, you can adjust it as needed

##每
def Offence():#1200 400
    """
    OP进攻逻辑
    1. 默认在前半场，实时追球，首要目标是抢球。
    2. 得到球权时，判断位置，有则溜边/弹射/澳门射等，无则找球。
    3. 若未检测到球 退至中场线与己方半场交界处或回防转DP。
    4. 绝不进入己方禁区防守区域。

    """
    peripheral.DribbleBall()
    if chassis.GetYaw is None:
            return False
    Yaw = chassis.GetYaw()
    Identityswitch()
    lBallPos = AbsBallPos()
    lPos = GetPos()
    bx, by = lBallPos[0], lBallPos[1]
    x, y = lPos[0], lPos[1]
    # 中场
    if bx == 0 and by == 0:   
            peripheral.StopDribble()
            Pos2Pos([0, -50, 0], False)
            return   
    if ball_owner == my_id:
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
                    if abs(Yaw-Angle) < 10:
                        chassis.stop()
                        peripheral.ShootBall()
                        break
                    elif x > 0:
                        chassis.GoZspeed(-150)
                    else:
                        chassis.GoZspeed(150)
            else:
                Lockballslip()
        else:
            Lockballslip()  
    else: #无球权
        if by < 0:
            Pos2Pos([x, 0, 0], False)
        else:
            Lockballslip()



def Offence(): #CODEGEEX希望做的修改
    if chassis.GetYaw is None:
        return False
    Yaw = chassis.GetYaw()

    # 获取球和自身位置
    lBallPos = GetBallPos()
    lPos = GetPos()
    iBX, iBY = lBallPos[0], lBallPos[1]
    iX, iY = lPos[0], lPos[1]
    
    # 计算球的绝对位置
    iAbsBX = iX + iBX
    iAbsBY = iY + iBY
    
    # 球未检测到或位置异常，回到默认位置
    if (iBX == 0 and iBY == 0) or (iX < -60 or iX > 60) or (iY < -80 or iY > 80):
        peripheral.StopDribble()
        GoBack()
        return
    
    # 有球权的进攻策略
    if ball_owner == my_id:
        logger.info("OP: 有球权，准备进攻")
        
        # 根据位置选择射门方式
        if abs(iX) > 50:  # 靠近边线
            logger.info("OP: 选择溜边射门")
            if iX > 0:
                Slipsideshot(60, iY)  # 右侧溜边
            else:
                Slipsideshot(-60, iY)  # 左侧溜边
        elif iBY < 0:  # 球在己方半场
            logger.info("OP: 选择澳门射门")
            if iX > 0:
                MacaoShot(20, -30, 300)  # 右侧澳门
            else:
                MacaoShot(-20, -30, 300)  # 左侧澳门
        elif iBY > 50:  # 深入对方半场
            logger.info("OP: 选择直接射门")
            # 计算射门角度
            Angle = math.degrees(math.atan2(abs(iX), 120-iY))
            while True:
                if abs(Yaw -Angle) < 10:
                    chassis.stop()
                    peripheral.ShootBall()
                    break
                elif iX > 0:
                    chassis.GoZspeed(-150)
                else:
                    chassis.GoZspeed(150)
        else:
            # 其他情况，控球并向前推进
            Lockballslip()
    else:  # 无球权的进攻策略
        logger.info("OP: 无球权，寻找球")
        
        if iBY < 0:  # 球在己方半场
            # 回到适当位置，不要太靠后
            target_y = max(-30, iBY + 20)  # 保持在球前方一定距离
            Pos2Pos([iX, target_y, 0], False)
        else:  # 球在对方半场
            # 积极追球
            Lockballslip()
    

def Defence(): #bX有部分最好是改为AX（敌方坐标）
    """
    DP防守逻辑
    1. 默认在己方半场，横向跟随球，保持在禁区外防守。
    2. 球过中线到对方半场，解除区域限制，积极争抢球权。
    3. 获得球权后 切换为OP。
    4. 球丢失或出界，回撤至防守点。
    5. 绝不与OP重叠在同一进攻区域。

    """
    peripheral.StopDribble()
    Identityswitch()
    lBallPos = AbsBallAngle()
    lPos = GetPos()
    iX, iY = lPos[0], lPos[1]
    bX, bY = lBallPos[0], lBallPos[1]

    HOMEPOS = [0, -90, 0]
    GOAL_POS = [0, -90]
    BLOCK_DIST = 20

    if bX == 0 and bY == 0 or abs(iX) > 70 or abs(iY) > 90:
        Pos2Pos(HOMEPOS, False)
        return
    if bY > 0 :  
        if ball_owner == my_id:
            return Offence()  #变成攻方
        elif ball_owner == peer_id:
            defend_x = - Peerstatus[2][0]   # 横向适当跟随(这里要改 是跟随谁 不确定)
            defend_y = -40 + Peerstatus[2][1] * 0.5  # 等比前移
            defend_y = max(-100, min(0, defend_y))
        else:#我方失去球权
            defend_x = bX * 0.8   
            defend_y = -40 + bY * 0.5  # 等比前移
            defend_y = max(-100, min(0, defend_y))
        Pos2Pos([defend_x, defend_y, 0], False)
    else:
        ball_to_goal_dist = math.sqrt((bX - GOAL_POS[0])**2 + (bY - GOAL_POS[1])**2)
        if ball_owner == my_id:
            return Offence()  #变成攻方
        elif ball_owner == peer_id:
            defend_x = - Peerstatus[2][0]   # 各自站左右半场
            defend_y = -90
        else:
            if ball_to_goal_dist < BLOCK_DIST: #离球门很近
                defend_x = (bX - GOAL_POS[0])/ abs(bY - GOAL_POS[1]) * abs(iY - GOAL_POS[1]) #在球和球门连线上
                defend_y = -90 
            else:
                defend_x =  bX 
                defend_y = -90          
        Pos2Pos([defend_x, defend_y, 0], False)

def Circle(origin:list[int,int],angle:int,r:int):
    Pos2Pos(
        [origin[0]+((r**2)/((1+math.tan(angle)**2)))**0.5,
        origin[1]+(math.tan(angle)**-1)*((r**2)/((1+math.tan(angle)**2)))**0.5,
        angle]
        ,False)

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
        if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY) and abs(iErrorRange) > iDeltaZ:
            chassis.stop()
            return True
        elif not abs(iErrorRange) > abs(iDeltaZ):
            chassis.GoZspeed(iDeltaZ)
        else:
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
            while True:
                Yaw = chassis.GetYaw()
                chassis.GoZspeed(-200)
                if abs((Yaw - target_angle2 + 180) % 360 - 180) < 30:
                    break
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
            while True:
                Yaw = chassis.GetYaw()
                chassis.GoZspeed(200)
                if abs((Yaw - target_angle2 + 180) % 360 - 180) < 30:
                    break

                    
def Slipsideshot(): #溜边 10,-90
    Yaw = compass()
    # peripheral.Dribble(True)
    lLocal = GetPos()
    iLocX = lLocal[0]
    iLocY = lLocal[1]
    ALocal = [0,0]
    ALocX = ALocal[0]
    ALocY = ALocal[1]
    DoorLocal = [0, -100]
    DoorY = DoorLocal[1]
    iY = 80
    if iLocX > 0:
        iX = 30
    else:
        iX = -30
    Angle = (math.degrees(math.atan2(iLocX - ALocX, iLocY - ALocY))-270) % 360
    if Pos2Pos([iX,iY,Angle],False):
        # chassis.GoV(0,Pos2Angle(GetPos(), [0,90]),100)
        # for _ in range(20):
        #     Pos2Pos([0,80,0],False)
        # Move2Path([80,0,Pos2Angle(GetPos(), [0,90])],False)
        for _ in range(20):
            if not AbsBallPos() == [1207, 1207]:
                break
            X,Y,_ = GetPos()
            DeltaY = 100 - Y
            DeltaX = X
            Theta = math.atan2(DeltaY, DeltaX)
            Theta = math.degrees(Theta)
            Compass = -(90 - Theta)
            chassis.GoZ(Compass)
            time.sleep(0.03)
        peripheral.ShootBall()
        logger.info("Ball is in possession, start shotting.")
    # if abs(iLocX - iX) < 10 and abs(iLocY - iY) < 10:
    #     while True:
    #         AngleD  = 270 + math.degrees(math.atan2(iLocX, DoorY - iLocY))
    #         Yaw = chassis.GetYaw()
    #         if iLocX > 0:
    #             chassis.GoZspeed(-100)
    #             k = -180
    #         else:
    #             chassis.GoZspeed(100)
    #             k = 180
    #         if abs((Yaw - AngleD + 180 +k) % 360) < 15:
    #                 chassis.stop()
    #                 peripheral.ShootBall()
    #                 time.sleep(0.3)
    #                 break
    #     return

def OHMYBACK():
    Yaw = compass()
    peripheral.Dribble(True)
    lLocal = GetPos()
    iLocX = lLocal[0]
    iLocY = lLocal[1]
    ALocal = [0,0]
    ALocX = ALocal[0]
    ALocY = ALocal[1]
    Angle = (math.degrees(math.atan2(iLocX - ALocX, iLocY - ALocY)-270)) % 360
    Pos2Pos([0,70,Angle],False)

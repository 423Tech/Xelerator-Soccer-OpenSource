import math
import time
import threading

from ReasonData import QkJson, logger
from kits import *
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

my_id = 1 #Arisu ID
peer_id = 2 #Kei ID
role = "DP"    # OP攻 DP守
ball_owner = 0 # 0无球权 1，2对应机器有球权
Dribblingdistance = 9 # 控球距离
PosXCache = 0
PosYCache = 0

# Values for COM
SendstatusThreadFuncStarted = False
PeerstatusThreadFuncStarted = False
peer_role, peer_owner, P2BallDirect, P_Pos, Pbx, Pby= None, None, None, None, None, None

#Math Mod
###################################################################################################

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

    HOMEPOS = [0, -80, 0]
    GOAL_POS = [0, 90]
    BLOCK_DIST = 50
    if bX == 0 and bY == 0 or abs(iX) > 70 or abs(iY) > 90:
        Pos2Pos(HOMEPOS, False,200)
        return
    if bY > 0 :  
        if ball_owner == my_id:
            return Offence()  #变成攻方
        elif ball_owner == peer_id:
            defend_x = - Peerstatus[3][0]   # 横向适当跟随( 是跟随谁 不确定)
            defend_y = -40 + Peerstatus[3][1] * 0.5  # 等比前移
            defend_y = max(-100, min(0, defend_y))
        else:#我方失去球权
            defend_x = bX * 0.8   
            defend_y = -40 + bY * 0.5  # 等比前移
            defend_y = max(-100, min(0, defend_y))
        Pos2Pos([defend_x, defend_y, 0], False,200)
    else:
        ball_to_goal_dist = math.sqrt((bX - GOAL_POS[0])**2 + (bY - GOAL_POS[1])**2)
        if ball_owner == my_id:
            return Offence()  #变成攻方
        elif ball_owner == peer_id:
            defend_x = - Peerstatus[3][0]   # 各自站左右半场
            defend_y = -90
        else:
            if ball_to_goal_dist < BLOCK_DIST: #离球门很近
                defend_x = (bX - GOAL_POS[0])/ abs(bY - GOAL_POS[1]) * abs(iY - GOAL_POS[1]) #在球和球门连线上
                defend_y = -90 
            else:
                defend_x =  bX 
                defend_y = -90          
        Pos2Pos([defend_x, defend_y, 0], False)

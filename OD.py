
from kits import *
from Defence_Back import *
from Defence_Follow_panning import *
from Defence_Follow_ratio import *
from Defence_link import *
from Offence_Back import *
# ArisuCam = ArisuIntelligence()

#Math Mod
###################################################################################################

def OD(): 
    iX,iY = GetPos()[0],GetPos()[1]
    bx,by = AbsBallPos()
    Cx = CEnemyPos()[0]
    Cy = CEnemyPos()[1]
    Fangle =(-int(math.degrees(math.atan2(Cy,Cx)) - 90)+ compass())%360
    CDistance = math.sqrt(Cx**2 + Cy**2)
    ChassisY = CDistance * math.cos(math.radians(Fangle))+iY
    if abs(iX) > 75 or abs(iX) <35 and abs(iY) <85: #防止出界限
        if iX>0:
            chassis.SetMotor(-400,400,400,-400)
        else:
            chassis.SetMotor()(400,-400,-400,400)
    elif abs(iY) > 95  or abs(iX) <35 and abs(iY) <85:
        if iY > 0:
            chassis.SetMotor(-400,-400,-400,-400)
        else:
            chassis.SetMotor(400,400,400,400)
    else:
        if BallFlag == [0,0]:
            if ChassisY > 0 or CEnemyPos() == [1204,1204]: #对方车辆位于对方半场
                if PeerPosition[1]> iY :
                    Pos2Pos(0,-40,0,False,100)
                else:
                    Pos2Pos(0,-85,0,False,100)
            else: #有可能是背身持球 没有扫描到球，锁车
                if ChassisY > -50:
                    FollowPRatio()
                else:
                    DefenceLink()
        else:
            if by > 0:
                if BallFlag == [1,0]:#ARISU要改【1,0】
                    Offence()
                elif BallFlag == [0,1]:
                    FollowPRatio()
                else:
                    LockBallSlip()
            else:
                if BallFlag == [1,0]:
                    Offence()
                elif BallFlag == [0,1]:
                    if bx > -50:
                        FollowPRatio()
                    else:
                        DefenceLink()
                else:
                    LockBallSlip()

def Offence():
    iX = GetPos()[0]
    iY = GetPos()[1]
    if abs(iX) > 35:
        OHMYBACK()
    else:
        NormalShoot()

def OffDenfence():
    bx,by = AbsBallPos()
    if [bx,by] == [1024,1024]:
        DefenceBack()
    else:
        if [bx,by] == [1207,1207]:
            Offence()
        else:
            if by > -20:
                LockBallSlip()
            else:
                if bx > -50:
                    FollowPRatio(0)
                else:
                    DefenceLink(0)


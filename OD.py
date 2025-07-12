
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
    iY = GetPos()[1]
    bx,by = AbsBallPos()
    result = AbsChassisPos()
    if result:
        ChassisX,ChassisY = result[0][0],result[0][1]
    else:
        ChassisX = None
        ChassisY = None
    if [bx,by] == [1204,1204]:
        if ChassisX > 0 or ChassisX == None: #对方车辆位于对方半场
            if PeerPosition[1]> iY :
                DefenceBack()
            else:
                OffenceBack()
        else: #有可能是背身持球 没有扫描到球，锁车
            if ChassisX > -50:
                FollowPPanning()
            else:
                DefenceLink()
    else:
        if by > 0:
            if BallFlag == [0,1]:#ARISU要改【1,0】
                Offence()
            elif BallFlag == [1,0]:
                FollowPRatio()
            else:
                LockBallSlip()
        else:
            if BallFlag == [0,1]:
                Offence()
            elif BallFlag == [1,0]:
                if bx > -50:
                    FollowPPanning()
                else:
                    DefenceLink()
            else:
                LockBallSlip()

def Offence():
    iX = GetPos()[0]
    if abs(iX) > 35 and abs(iX) < 0:
        OHMYBACK()
    else:
        NormalShoot()

def OffDenfence():
    bx,by = AbsBallPos()
    if [bx,by] == [1204,1204]:
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


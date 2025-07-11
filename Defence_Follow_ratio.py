from kits import *
def FollowPRatio():
    #Completed
    time.sleep(0.03)
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    Compass = compass()
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = Angle + Compass

    defend_x = 0
    defend_y = 0
    lPos = GetPos()
    bX,bY= AbsBallPos()
    iX= lPos[0]
    PeerX, PeerY = PeerPosition[0], PeerPosition[1]
    ChassisX, ChassisY = AbsChassisPos()[0], AbsChassisPos()[1]
    if [bX,bY] == [1024,1024]:
            peripheral.DribbleBall()
            if abs(iX) <= 60:
                defend_x = ChassisX 
                defend_y = -40 + ChassisY * 0.47  # 等比前移
                defend_y = max(-85, min(0, defend_y))
            else:
                defend_x = 0    
                defend_y = -40 + ChassisY * 0.47  # 等比前移
                defend_y = max(-85, min(0, defend_y))
    else:
        peripheral.DribbleBall()
        if abs(iX) <= 60:
            defend_x = PeerX  
            defend_y = -40 + PeerY * 0.47  # 等比前移
            defend_y = max(-85, min(0, defend_y))
        else:
            defend_x = 0    
            defend_y = -40 + PeerY * 0.47  # 等比前移
            defend_y = max(-85, min(0, defend_y))
    Pos2Pos([defend_x, defend_y, Fangle], 400)




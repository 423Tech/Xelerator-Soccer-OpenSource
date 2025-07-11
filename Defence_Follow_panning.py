from kits import *
def FollowPPanning():
    # 无法执行？
    time.sleep(0.03)
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    Compass = compass()
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = Angle + Compass

    defend_x = 0
    lPos = GetPos()
    bX,bY= AbsBallPos()
    iX= lPos[0]
    PeerX = PeerPosition[0]
    if [bX,bY] == [1024,1024]:
        defend_x = 0
        Fangle = 0
    else:
        if abs(iX) <= 60:
            defend_x = PeerX
        else:
            defend_x = 0    
            Pos2Pos([defend_x, -85, Fangle], False)

from kits import *
def FollowPRatio():
    lPos = GetPos()
    bX,bY= AbsBallPos()
    iX= lPos[0]
    PeerX, PeerY = PeerPosition[0], PeerPosition[1]
    if [bX,bY] == [1024,1024]:
        defend_x = 0
    else:
        if abs(iX) <= 60:
            defend_x = bX   
            defend_y = -40 + PeerY * 0.5  # 等比前移
            defend_y = max(-80, min(0, defend_y))
        else:
            defend_x = 0    
            defend_y = -40 + PeerY * 0.5  # 等比前移
            defend_y = max(-80, min(0, defend_y))
    Pos2Pos([defend_x, defend_y, 0], False,200)




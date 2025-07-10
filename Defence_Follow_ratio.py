from kits import *
def FollowPRatio():
    lPos = GetPos()
    iX= lPos[0]
    PeerX, PeerY = PeerPosition[0], PeerPosition[1]
    if abs(iX) <= 60:
        defend_x = PeerX   
        defend_y = -40 + PeerY * 0.5  # 等比前移
        defend_y = max(-85, min(0, defend_y))
        Pos2Pos([defend_x, defend_y, 0], False,200)
    else:
        defend_y = -40 + PeerY * 0.5  # 等比前移
        defend_y = max(-85, min(0, defend_y))
        Pos2Pos([0, defend_y, 0], False,200)




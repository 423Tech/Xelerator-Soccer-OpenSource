
from kits import *
def FollowPRatio():
    lPos = GetPos()
    
    bX, bY = AbsBallPos()
    iX,iY= lPos
    GOAL_POS = [0, -95]
    if abs(iX) <= 60:
        defend_x = bX / (bY - GOAL_POS[1]) * (iY - GOAL_POS[1]) 
        Pos2Pos([defend_x, defend_y, 0], False,200)
    else:
        defend_y = -40 + PeerY * 0.5  # 等比前移
        defend_y = max(-85, min(0, defend_y))
        Pos2Pos([0, defend_y, 0], False,200)




defend_x = (bX - GOAL_POS[0])/ abs(bY - GOAL_POS[1]) * abs(iY - GOAL_POS[1]) #在球和球门连线上
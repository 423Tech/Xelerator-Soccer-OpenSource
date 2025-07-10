
from kits import *
def DefenceLink():
    lPos = GetPos() 
    bX, bY = AbsBallPos()
    iX,iY= lPos
    GOAL_POS = [0, -95]
    if abs(iX) <= 60:
        defend_y = -40 + bY * 0.5  # 等比前移
        defend_y = max(-85, min(0, defend_y))
        defend_x = bX / (bY - GOAL_POS[1]) * (iY - GOAL_POS[1]) 
        Pos2Pos([defend_x, defend_y, 0], False,200)
    else:
        defend_y = -40 + bY * 0.5  # 等比前移
        defend_y = max(-85, min(0, defend_y))
        defend_x = 0
    Pos2Pos([defend_x, defend_y, 0], False,200)
from kits import *
def DefenceLink():
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    Compass = compass()
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = Angle + Compass


    lPos = GetPos() 
    bX, bY = AbsBallPos()
    iX,iY,_= lPos
    logger.debug("bX"+str(bX)+" bY"+str(bY))
    # GOAL_POS = [0, -100]
    if [bX,bY] == [1024,1024]:
        defend_x = 0
        defend_y = -80
    else:
        ABSx = bX / (100+bY) * 20
        if abs(ABSx) <= 35:
            defend_x = ABSx
            defend_y = -80
        elif abs(ABSx) > 35 and abs(ABSx) < 45:
            defend_x = ABSx
            defend_y = 80 - (abs(ABSx)-35)
        else:
            defend_x = 45
            defend_y = -100 + (100+bY)/bX * 45
    Pos2Pos([defend_x, defend_y, Fangle], False)
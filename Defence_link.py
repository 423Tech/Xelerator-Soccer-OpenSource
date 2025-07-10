from kits import *
def DefenceLink():#"0":[75,95],"1":[35,85]
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    Compass = compass()
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = Angle + Compass
    bX, bY = AbsBallPos()
    logger.debug("bX"+str(bX)+" bY"+str(bY))
    # GOAL_POS = [0, -100]
    if [bX,bY] == [1024,1024]:
        defend_x = 0
        defend_y = -80
    else:
        ABSx = bX / (95+bY) * 10
        print(ABSx)
        if abs(ABSx) <= 35:
            defend_x = ABSx
            defend_y = -80
        elif abs(ABSx) > 35 and abs(ABSx) < 42:
            defend_x = ABSx
            defend_y = -75 - (abs(ABSx)-35)
        else:
            if ABSx > 0:
                defend_x = 42
            else:
                defend_x = -42
            defend_y = -95 + (95+bY)/bX * 45
    Pos2Pos([defend_x, defend_y, Fangle], False)
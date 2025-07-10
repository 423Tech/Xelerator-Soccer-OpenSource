from kits import *
def DefenceLink():#"0":[75,95],"1":[35,85]
    time.sleep(0.03)
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
        defend_y = -85
    else:
        if bY == -95:
            ABSx = bX  * 10
        else:
            ABSx = bX / (95+bY) * 10
        print(ABSx)
        if abs(ABSx) <= 35:
            defend_x = ABSx
            defend_y = -85
        elif abs(ABSx) > 35 and abs(ABSx) < 42:
            defend_x = ABSx
            defend_y = -85 - (abs(ABSx)-35)
        else:
            if ABSx > 0:
                defend_x = 42
            else:
                defend_x = -42
            defend_y = -95 + (85+bY)/abs(bX) * 45
    Pos2Pos([defend_x, defend_y, Fangle], False,80)
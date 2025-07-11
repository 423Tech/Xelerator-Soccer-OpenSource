from kits import *
def DefenceLink(x):#"0":[75,95],"1":[35,85]
    #Comlpeted
    time.sleep(0.03)
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    Compass = compass()
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    Fangle = Angle + Compass

    bX, bY = AbsBallPos()
    logger.debug("bX"+str(bX)+" bY"+str(bY))
    if x == 1:
        defend_x = 0
        defend_y = 0
        ChassisX = AbsChassisPos()[0]
        ChassisY = AbsChassisPos()[1]
        if [bX,bY] == [1024,1024]: #没有扫描到球 那就锁定车辆位置
            peripheral.StopDribble()
            Fangle = AbsChassisAngle()
            if ChassisY == -95:
                ABSx = ChassisX  * 10
            else:
                ABSx = ChassisX / (95+ChassisY) * 10
            print(ABSx)
            if abs(ABSx) <= 35:
                defend_x = ABSx
                defend_y = -85
            elif abs(ABSx) > 35 and abs(ABSx) < 42:
                defend_x = ABSx
                defend_y = -85 - (abs(ABSx)-35)
            else:
                if ChassisX > 0:
                    defend_x = 42
                else:
                    defend_x = -42
                defend_y = -95 + (85+ChassisY)/abs(ChassisX) * 45
        else: #有球锁球
            peripheral.DribbleBall()
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
                if bX > 0:
                    defend_x = 42
                else:
                    defend_x = -42
                defend_y = -95 + (85+bY)/abs(bX) * 45
        Pos2Pos([defend_x, defend_y, Fangle], False,150)
    else:
        defend_x = 0
        defend_y = 0
        if [bX,bY] == [1024,1024]: 
            peripheral.StopDribble()
            Fangle = 0
        else: 
            peripheral.DribbleBall()
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
                if bX > 0:
                    defend_x = 42
                else:
                    defend_x = -42
                defend_y = -95 + (85+bY)/abs(bX) * 45
        Pos2Pos([defend_x, defend_y, Fangle], False,150)
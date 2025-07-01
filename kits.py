import math
from arisbit import ArisBit
from headunit import Lidar

from ReasonData import QkJson, logger
cfg = QkJson()




from chassis import Car
if cfg.read("model","bit") == "AB":
    from .ArisBit import ArisBit
    chassis = Car(ArisBit().SetMotor,ArisBit().GetYaw)
    logger.info("Arisu Bit loaded.")
elif cfg.read("model","bit") == "RB":
    from ReasonBit import motor
    from ReasonBit import compass
    from ReasonBit import batt
    chassis = Car(motor.RPM,compass.get)
    logger.info("RoboMaster Bit loaded.")
else:
    logger.error("None Bit Model found.")
    raise ImportError("None Bit Model found.")


Bot = ArisBit()
Lidar = Lidar(Bot.GetYaw)


if (batt.get()) <= cfg.read("advanced","BattVot"):
   raise Exception("电池电量不足，请充电")

#Values
bLife = False
lBlockedMemo = []
bCovered = False
lBallPos = [0,0]
lLidarDists = [0,0,0,0]
bThreadControllerFlag = True
iUARTPort = 1


#Math Mod
def roundThresholdJudger(iValue, iRound, iMiddleValue, iOffset):
    iValue = iValue % iRound
    
    iLowerThreshold = (iMiddleValue - iOffset) % iRound
    iUpperThreshold = (iMiddleValue + iOffset) % iRound

    if iLowerThreshold <= iUpperThreshold:
        return iLowerThreshold <= iValue <= iUpperThreshold

    else:
        return iValue >= iLowerThreshold or iValue <= iUpperThreshold

def FindNearstAngle(arr, target):
    return min(arr, key=lambda x: abs(x - target))


#Value Mod
def LidarDists():
    # ClearUART(1)
    # iCompass = str(int(compass.read()))
    # sSentData = 'cmp'+str(iCompass)+'end'
    # SendUART(1,sSentData)
    # sReceivedDataFrame = GetUART(1)
    # sParsedDataFrame = sReceivedDataFrame[sReceivedDataFrame.index('som')+3:sReceivedDataFrame.index('eom',sReceivedDataFrame.index('som'))+3]
    # iFrontDist = int(sParsedDataFrame[sParsedDataFrame.index('fd')+2:sParsedDataFrame.index('rd')])
    # iRightDist = int(sParsedDataFrame[sParsedDataFrame.index('rd')+2:sParsedDataFrame.index('bd')])
    # iBackDist = int(sParsedDataFrame[sParsedDataFrame.index('bd')+2:sParsedDataFrame.index('ld')])
    # iLeftDist = int(sParsedDataFrame[sParsedDataFrame.index('ld')+2:sParsedDataFrame.index('eom')])
    # lOutDists = [iFrontDist,iRightDist,iBackDist,iLeftDist]
    # return lOutDists
    pass

#TODO Need update
def GetDists() -> list[int,int,int]:
    return LidarDists()

def GetPos() -> list[int,int]:
    # if not cfg.read("Distance","On"):
    #     Distance = GetDists()
    #     iCfgK = 10
    #     if Distance[0]+Distance[2] < (cfg.read("Position","Height")*iCfgK):
    #         if (cfg.read("Position","Height")*iCfgK) > Distance[0] > Distance[2]:
    #             Y = (((cfg.read("Position","Height")*(iCfgK/2))) - (Distance[0]))
    #         else:
    #             Y = (((Distance[2]) - (cfg.read("Position","Height")*iCfgK/2)))
    #     else:
    #         Y = (((cfg.read("Position","Height")*(iCfgK/2)) - Distance[0]) + (Distance[2] - (cfg.read("Position","Height")*(iCfgK/2))))/2
    #     if Distance[1]+Distance[3] < (cfg.read("Position","Width")*iCfgK):
    #         if (cfg.read("Position","Height")*iCfgK) > Distance[1] > Distance[3]:
    #             X = -(cfg.read("Position","Width")*(iCfgK/2) - Distance[1])
    #         else:
    #             X = -(Distance[3] - cfg.read("Position","Width")*(iCfgK/2))
    #     else:
    #         X = -((cfg.read("Position","Width")*(iCfgK/2) - Distance[1] ) + (Distance[3] - cfg.read("Position","Width")*(iCfgK/2)))/2

    #     return [int(X)/10,int(Y)/10]
    # else:
    Distance = Lidar.GetDists()
    Compass = Bot.GetYaw()
    if Distance[0]+Distance[2] < (cfg.read("Position","Height") - 35):
        if Distance[0] > Distance[2]:
            Y = cfg.read("Position","Height")/2 - Distance[0] -4
        else:
            Y = Distance[2] - cfg.read("Position","Height")/2 + 4
    else:
        Y = ((cfg.read("Position","Height")/2 - Distance[0]) + (Distance[2] - cfg.read("Position","Height")/2))/2
    if Distance[1]+Distance[3] < (cfg.read("Position","Width") - 35):
        if Distance[1] > Distance[3]:
            X = -(cfg.read("Position","Width")/2 - Distance[1] - 4)
        else:
            X = -(Distance[3] - cfg.read("Position","Width")/2 + 4)
    else:
        X = -((cfg.read("Position","Width")/2 - Distance[1]) + (Distance[3] - cfg.read("Position","Width")/2))/2
    return [X/10,Y/10,Compass]


#Operate models
# def RailGun():
    

def Cover2Start():
    global bCovered
    if LidarDists()[0] < 10 or bCovered:
        bCovered = True
        return True
    else:
        bCovered = False
        return False

def AvoidOutBorder():
    # return 0
    lLocalPos = GetPos()
    if lLocalPos[0] <= 0:
        iKX = -1
    else:
        iKX = 1
    if lLocalPos[1] <= 0:
        iKY = -1
    else:
        iKY = 1
    if lLocalPos[1]*iKY >= list(cfg.read("Border","0"))[1]:
        if lLocalPos[0]*iKX >= list(cfg.read("Border","0"))[0]:
            iMoveAngle = -135
        else:
            iMoveAngle = 180
    elif lLocalPos[1]*iKY >= list(cfg.read("Border","1"))[1]:
        if lLocalPos[0]*iKX >= list(cfg.read("Border","0"))[0]:
            iMoveAngle = -90
        elif lLocalPos[0]*iKX <= list(cfg.read("Border","1"))[0]:
            # print(GetPos())
            iMoveAngle = 180
        else:
            pass
    else:
        pass
    try:
        iMoveAngle = iMoveAngle*iKX*iKY
        if iMoveAngle == -180:
            iMoveAngle = 0
        GoV(0,-iMoveAngle,200)
    except:
        car.stop()

def ObtDetect() -> list[list[int,int],list[bool,bool]]:
    '''
    返回一个列表，[[角度],[是否被遮挡]]
    '''
    global lBlockedMemo,iMemoLife,bLife
    lStatusOfDist = [[],[]]
    # iMaxLife = cfg.read("A2AOb","LifeTime")
    lDists = GetDists()
    iNumOfDist = len(lDists)
    iPerAngle = int(359/iNumOfDist)
    if len(lStatusOfDist) < iNumOfDist:
        for d in range(iNumOfDist):
            lStatusOfDist.append(True)
    for i in range(iNumOfDist):
        lStatusOfDist[0].append(iPerAngle*i)
        if lDists[i] <= cfg.read("A2AOb","ActiveRange"):
            lStatusOfDist[1][i] = False
        else:
            lStatusOfDist[1][i] = True
    return lStatusOfDist

def AvoidObt(iFacingAngle: int | None = 0,iTargetAngle:int | None = 0,iSpeed:int | None = 150) -> None:
    '''
    iFacingAngle 移动时面对的方向 0~360
    iTargetAngle 需要移动的方向 可能不采用 -180~180
    iSpeed 移动的速度 默认150
    '''
    iTargetAngle = -iTargetAngle
    lStatusOfDist = ObtDetect()
    #获取挡住/被挡住的角度

   #判断
    lAvailbeAngles = []
    for i in range(len(lStatusOfDist[0])):
        if lStatusOfDist[1][i]:
            lAvailbeAngles.append(lStatusOfDist[0][i])
    print(lAvailbeAngles)
    try:
        iAimAngle = FindNearstAngle(lAvailbeAngles,iTargetAngle)
        GoV(iFacingAngle,iAimAngle,iSpeed)
        # car.z_move(iFacingAngle,iAimAngle,200)
    except:
        car.stop()

def Local2Angle(lAimPos:list[int,int]) -> int:
    '''
    lAimPos 一个坐标 示例：[0,0]
    '''
    iAimX = lAimPos[0]
    iAimY = lAimPos[1]
    iLocX = GetPos()[0]
    iLocY = GetPos()[1]
    iDeltaX = iAimX - iLocX
    iDeltaY = iAimY - iLocY
    try:
        iDeltaAngle = -math.degrees(math.atan(iDeltaX/iDeltaY))
    except:
        if iDeltaX > 0:
            iDeltaAngle = -90
        else:
            iDeltaAngle = 90
    return int(iDeltaAngle)

def Pos2Angle(lInputPos:list[int,int],lAimPos:list[int,int]) -> int:
    '''
    lInputPos 输入坐标
    lAimPos 目标坐标 示例：[0,0]
    '''
    iAimX = lAimPos[0]
    iAimY = lAimPos[1]
    iLocX = lInputPos[0]
    iLocY = lInputPos[1]
    iDeltaX = iAimX - iLocX
    iDeltaY = iAimY - iLocY
    iDeltaAngle = math.degrees(math.atan2(iDeltaY,iDeltaX))
    return int(iDeltaAngle)

def Pos2Pos(iFacingAngle,lAimPos:list[int,int], A2O:bool | None = False) -> int:

    '''
    iFacingAngle 移动时面对的方向 0~360
    lAimPos 目标坐标位置 如[0,0] 距离越近速度越小
    A2O 是否开启自动避障 默认True
    '''
    # AvoidOutBorder()
    iAimX = lAimPos[0]
    iAimY = lAimPos[1]
    delay.ms(100)
    lLocal = GetPos()
    iLocX = lLocal[0]
    iLocY = lLocal[1]
    iDeltaX = iAimX - iLocX
    iDeltaY = iAimY - iLocY
    if iDeltaX > 500:
        iDeltaX = iDeltaX/5
    if iDeltaY > 500:
        iDeltaY = iDeltaY/5
    if iDeltaX < 100:
        iDeltaX = iDeltaX*3
    if iDeltaY < 100:
        iDeltaY = iDeltaY*3
    iErrorRange = cfg.read("Position","ErrorRange")/2
    if A2O:
        if iErrorRange > iDeltaX > -iErrorRange and iErrorRange > iDeltaY > -iErrorRange:
            car.stop()
        else:
            if 0 > iDeltaX:
                PA = Local2Angle(lAimPos) + 180
            else:
                PA = Local2Angle(lAimPos)
            if 0 > iDeltaY:
                PA = Local2Angle(lAimPos) - 180
            AvoidObt(iFacingAngle,PA,(abs(iDeltaX) - abs(iDeltaY))/1.3)
    else:
        if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY):
            car.stop()
            return True
        else:
        # car.turn(iFacingAngle)
            # Go2(iFacingAngle,iDeltaX,iDeltaY)
            if iDeltaY > 0:
                iAngle = 180
            else:
                iAngle = 0
            iMovedAngle = int(math.degrees(math.atan2(iDeltaY,iDeltaX)))
            car.z_move(iFacingAngle,90-iMovedAngle,int((abs(iDeltaX)+abs(iDeltaY)/2)))
            return False

def Move2Path(iFacingAngle:int,Posistions:list[list[int,int],list[int,int]],iWaitMs:int,A2O:bool | None = False):
    iErrorRange = cfg.read("Position","ErrorRange")/2
    for i in Posistions:
        while (1):
            iAimX = i[0]
            iAimY = i[1]
            lLocal = GetPos()
            iLocX = lLocal[0]
            iLocY = lLocal[1]
            iDeltaX = iAimX - iLocX
            iDeltaY = iAimY - iLocY
            if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY):
                if i == Posistions[-1]:
                    return True
                else:
                    delay.ms(iWaitMs)
                    break
            else:
                Pos2Pos(iFacingAngle=iFacingAngle,lAimPos=i,A2O=A2O)

def roundThresholdJudger(iValue, iRound, iMiddleValue, iOffset):
    iValue = iValue % iRound
    iLowerThreshold = (iMiddleValue - iOffset) % iRound
    iUpperThreshold = (iMiddleValue + iOffset) % iRound
    
    if iLowerThreshold <= iUpperThreshold:
        return iLowerThreshold <= iValue <= iUpperThreshold
    else:
        return iValue >= iLowerThreshold or iValue <= iUpperThreshold

def CircleAround(iAimAngle):
    iCompass = int(compass.read())


    if roundThresholdJudger(iCompass,360,iAimAngle+90,90):
        iDirectionFactor = 1
    else:
        iDirectionFactor = -1
    
    
#    if 0 <= abs(iCompass - iAimAngle) < 180:
#        iDirectionFactor = 1
#    elif 180 <= abs(iCompass - iAimAngle) < 360:
#        iDirectionFactor = -1
    while(1):
        lBallPos = GetBallPos()
        iX, iY = lBallPos[0], lBallPos[1]
        if iY > 0:
            iDeltaAngle = -int(math.degrees(math.atan2(iY, iX)) - 90)     
        print(iX,iY,iDeltaAngle,compass.read())
        if roundThresholdJudger(compass.read(), 360, iAimAngle, 3):
            break
        else:
            set_motor.RPM(iDirectionFactor * 30,-iDirectionFactor * (130 - iDeltaAngle),-iDirectionFactor * 30,iDirectionFactor * (130 - iDeltaAngle))
    car.turn(iAimAngle)
    while(1):
        iBX = GetBallPos()[0]
        if iBX <= -2:
            print('atleft')
            car.z_move(iAimAngle,iAimAngle + 90,-20)
#            set_motor.RPM(-30,30,30,-30)
        elif iBX >= 2:
            print('atright')
            car.z_move(iAimAngle,iAimAngle + 90,20)
#            set_motor.RPM(30,-30,-30,30)
        else:
            for _ in range(3):
                set_motor.RPM(0,0,0,0)
            break
    print('stopped')

def TurnToTheBall():
    while(1):
        lBallPos = GetBallPos()
        iX, iY = lBallPos[0], lBallPos[1]
        if -2 <= iX <= 2 and iY > 0:
            car.stop()
            break
        else:
            set_motor.RPM(20,20,-20,-20)

def AutoFetch(bStop = True):
    TurnToTheBall()
    while(1):
        lBallPos = GetBallPos()
        iBX, iBY = lBallPos[0], lBallPos[1]
        SpeedL = 30 + 3 * iBX
        SpeedR = 30 - 3 * iBX
        set_motor.RPM(SpeedL, SpeedL, SpeedR, SpeedR)
        if iBX > -2 and iBX < 2 and iBY >= 7 and iBY <= 9:
            if bStop:
                car.stop()
            break

def Move2Pos(iFacingAngle,lPos):
    while not Pos2Pos(0,lPos,False):
        pass
    for _ in range(3):
        set_motor.RPM(0,0,0,0)

def RunCircle(r:int, angle:int,a:int):
    iSpeed = 355/r
    iRad = math.radians(angle)
    iInsideSpeed = iSpeed * r
    iOutsideSpeed = iSpeed * r
    x= int(iInsideSpeed* math.sin(iRad))
    y= int(iOutsideSpeed* math.cos(iRad))
    z= -int(iInsideSpeed * math.sin(iRad))
    w= -int(iOutsideSpeed* math.cos(iRad))
    if (a == 1):   #正
        set_motor.RPM(x,y,z,w)
    elif( a == -1 ): #反
        set_motor.RPM(z,w,x,y)
    else:
        set_motor(0,0,0,0)
    length = r * iRad  # 弧长
    time = length / iSpeed
    delay.ms(time)
    set_motor.RPM(0, 0, 0, 0)

def GoDistance(iDistance):
    iDistance = iDistance * 10
    iCompass = int(compass.read())
    
    if roundThresholdJudger(iCompass, 360, 0, 45):
        iFacingDistIndex = 0
        iMovingAngle = 0
    elif roundThresholdJudger(iCompass, 360, 90, 45):
        iFacingDistIndex = 3
        iMovingAngle = 90
    elif roundThresholdJudger(iCompass, 360, 180, 45):
        iFacingDistIndex = 2
        iMovingAngle = 180
    elif roundThresholdJudger(iCompass, 360, 270, 45):
        iFacingDistIndex = 1
        iMovingAngle = 270
    else:
        return False
    
    iAimDist = GetDists()[iFacingDistIndex] - iDistance
    
    while(1):
        car.straight(iMovingAngle, 20)
        iCurrentDist = GetDists()[iFacingDistIndex]
        print(iCurrentDist,iAimDist)
        if iCurrentDist < iAimDist + 10:
            set_motor.RPM(0,0,0,0)
            break

#Offense & Defense
def AimBall(Ball) -> int:
    if Ball[1] < 0:
        iAngle = 180
    else:
        iAngle = 0
    try:
        if -(math.degrees(math.atan2(Ball[1],Ball[0])) - 90) < 0:
            return -(math.degrees(math.atan2(Ball[1],Ball[0])) - 90) + 360
        else:
            return -(math.degrees(math.atan2(Ball[1],Ball[0])) - 90)
    except:
        return 0

def GoBack():
    Pos2Pos(0,cfg.read("Position","Home"),False)

def Offence():
    lBallPos = GetBallPos()
    iBX,iBY = lBallPos[0],lBallPos[1]
    lPos = GetPos()
    iX,iY = lPos[0],lPos[1]

    iAbsBX = iX + iBX
    iAbsBY = iY + iBY

    set_io.out(13,1)
    set_io.out(14,0)

    if (iBX == 0 and iBY == 0) or (iX < -60 or iX > 60) or (iY < -80 or iY > 80):
        GoBack()
    elif 7 <= iBY <= 30:
        if -2 <= iBX <= 2:
            GoY(500)
            delay.ms(50)
            GoBack()
        elif iBX < -2:
            GoX(-50)
        elif iBX > 2:
            GoX(50)
    elif iBY > 30:
        if iBX < 0:
            iAimAngle = AimBall([iBX - 2,iBY - 10])
        elif iBX >= 0:
            iAimAngle = AimBall([iBX + 2,iBY - 10])
        car.z_move(0,iAimAngle,150)
    elif iBY <= -7:
        if iAbsBX < 0:
            iAimAngle = AimBall([iBX + 20,iBY - 10])
        elif iAbsBX >= 0:
            iAimAngle = AimBall([iBX - 20,iBY - 10])
        
        car.z_move(0,iAimAngle,150)
    
    print(iX,iY,iBX,iBY,iAbsBX,iAbsBY)

def Circle(origin:list[int,int],angle:int,r:int):
    Pos2Pos(
        angle,
        [origin[0]+((r**2)/((1+math.tan(angle)**2)))**0.5,
        origin[1]+(math.tan(angle)**-1)*((r**2)/((1+math.tan(angle)**2)))**0.5]
        ,False)

def Defence()->None:
    lBallPos = GetBallPos()
    lPos = GetPos()
    if -80 > lPos[1] > -50 or abs(lPos[0]) > 65 or (lBallPos[0]*lBallPos[1] == 0):
        Pos2Pos(0,cfg.read("Position","Home"),False)
    else:
        if lBallPos[0] > 0:
            car.z_move(0,90,5*lBallPos[0])
        else:
            car.z_move(0,-90,5*lBallPos[0])
        # Circle(cfg.read("Position","Home"),AimBall(cfg.read("Position","Home")),35)

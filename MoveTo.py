import math
from Level6 import GetPos, key, Go2, GetDists, AvoidObt, GoV
import car

def Pos2Angle(lAimPos:list[int,int]) -> int:
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
            iDeltaAngle = 90
        else:
            iDeltaAngle = 180
    return int(iDeltaAngle)

def Pos2Pos(iFacingAngle,lAimPos:list[int,int], A2O:bool | None = False) -> int:
    if not A2O:
        iAimX = lAimPos[0]
        iAimY = lAimPos[1]
        iLocX = GetPos()[0]
        iLocY = GetPos()[1]
        iDeltaX = iAimX - iLocX
        iDeltaY = iAimY - iLocY
        if iDeltaX > 500:
            iDeltaX = iDeltaX/5
        if iDeltaY > 500:
            iDeltaY = iDeltaY/5
        if iDeltaX < 100:
            iDeltaX = iDeltaX*5
        if iDeltaY < 100:
            iDeltaY = iDeltaY*5
        Go2(iFacingAngle,iDeltaX,iDeltaY)
        # print(iDeltaX,iDeltaY)
    else:
        iAimX = lAimPos[0]
        iAimY = lAimPos[1]
        iLocX = GetPos()[0]
        iLocY = GetPos()[1]
        iDeltaX = iAimX - iLocX
        iDeltaY = iAimY - iLocY
        if 3 > iDeltaX > -3 and 3 > iDeltaY > -3:
            print(iDeltaX,iDeltaY)
            car.stop()
        else:
            AvoidObt(iFacingAngle,Pos2Angle([0,0]))
        # print(GetPos())

while(key.read() == 0):
    print(Pos2Angle([0,0]))
    print(GetDists(4))

while True:
    Pos2Pos(0,[20,20],True)
    # print(GetPos())
    # print(Pos2Angle([0,0]))
    # AvoidObt(0,Pos2Angle([0,0]))
    # GoV(0,90,150)


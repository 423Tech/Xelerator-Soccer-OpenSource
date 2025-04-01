import math
from Level6 import cfg, GetPos, AvoidObt, key, Go2

def Pos2Angle(lAimPos:list[int,int]) -> int:
    iAimX = lAimPos[0]
    iAimY = lAimPos[1]
    iLocX = GetPos()[0]
    iLocY = GetPos()[1]
    iDeltaX = iAimX - iLocX
    iDeltaY = iAimY - iLocY
    iDeltaAngle = math.degrees(math.atan(iDeltaY/iDeltaX))
    if iDeltaAngle < 0:
        iDeltaAngle = 360 + iDeltaAngle
    else:
        pass
    return iDeltaAngle

def Pos2Pos(iFacingAngle,lAimPos:list[int,int]) -> int:
    iAimX = lAimPos[0]
    iAimY = lAimPos[1]
    iLocX = GetPos()[0]
    iLocY = GetPos()[1]
    iDeltaX = iAimX - iLocX
    iDeltaY = iAimY - iLocY
    Go2(iFacingAngle,iDeltaX,iDeltaY)

while(key.read() == 0):
    print(Pos2Angle([0,0]))
    print(GetPos())

while True:
    Pos2Pos(0,[0,0])


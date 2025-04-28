from level5 import *

#Offense & Defense
def AimBall() -> int:
    Pos = GetPos()
    Ball = GetBallPos()
    Ball[0] = Pos[0] + Ball[0]
    Ball[1] = Pos[1] + Ball[1]
    return Pos2Angle(Pos,Ball)

def Circle(origin:list[int,int],angle:int,r:int):
    Pos2Pos(angle,[origin[0]+((r**2)/((1+math.tan(angle)**2)))**0.5,origin[1]+(math.tan(angle)**-1)*((r**2)/((1+math.tan(angle)**2)))**0.5],False)

def offense()->None:
    lPos = GetPos()
    if lPos[1] > -50:
        Pos2Pos(0,cfg.read("Position","Home"),False)
    else:
        Circle(cfg.read("Position","Home"),AimBall(),35)

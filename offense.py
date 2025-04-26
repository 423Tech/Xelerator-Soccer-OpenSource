from level5 import *

while True:
    lBallRawPos = GetBallPos()
    lLocalPos = GetPos()
    lBallRawPos[0] = lBallRawPos[0] + lLocalPos[0]
    lBallRawPos[1] = lBallRawPos[1] + lLocalPos[1]
    

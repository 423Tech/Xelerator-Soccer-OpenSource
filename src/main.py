from LunaPre import *

Cache = False

try:
    # Positions().Move2Path([[0,0,0],[40,40,0],[40,-40,90],[-40,-40,180],[-40,40,270]],2)
    while(1):
        # print(Positions().AbsRoboPosition())
    # time.sleep(1)
        # from BasicFuc import *    
        # LockSeries().LockBallSlip()
        Positions().Pos2Pos([0,0,0])
        # chassis.AbsMoveAngle(0,45,300)

except Exception as e:
    raise e
finally:
    chassis.stop()
    lidar.stop()
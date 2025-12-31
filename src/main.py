from LunaPre import *

Cache = False

try:
    while(1):
        Positions().Move2Path([[0,0,0],[40,40,0],[40,-40,0],[-40,-40,0],[-40,40,0]],2)
        # print(Positions()._UpdateAbsRoboPosition())
        # time.sleep(1)
        # from BasicFuc import *    
        # LockSeries().LockBallSlip()
        # Positions().Pos2Pos([0,0,0])
        
        # chassis.AbsTurn(0)
        # print(chassis.GetYaw())
        # chassis.SetMotor([0,0,0,0])

except Exception as e:
    raise e
finally:
    chassis.stop()
    lidar.stop()
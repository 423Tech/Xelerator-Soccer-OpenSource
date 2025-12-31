from LunaPre import *

Cache = False

try:
    while(1):
        if Positions().Pos2Pos([0,0,0]):
            break
        else:
            pass
        # pass
    while(1):
    #     # Positions().Move2Path([[40,40,90],[40,-40,90],[-40,-40,90],[-40,40,90]],0.8)
        print(Positions().Relative_Ball_Position())
    #     # time.sleep(1)
        # from BasicFuc import *    
        # LockSeries().LockBallSlip()
    #     # Positions().Pos2Pos([0,0,0])
        # chassis.AbsMoveVetor(0,100,0)
        # chassis.AbsTurn(90)
        # print(chassis.GetYaw())
        # chassis.SetMotor([0,0,0,0])

except Exception as e:
    raise e
finally:
    chassis.stop()
    lidar.stop()
from LunaPre import *

Cache = False

try:
    while(1):
        # print(Positions().Relative_Ball_Position())
        # time.sleep(0.5)
        from BasicFuc import LockSeries
        LockSeries().LockBallSlip()
except Exception as e:
    raise e
finally:
    chassis.stop()
    lidar.stop()
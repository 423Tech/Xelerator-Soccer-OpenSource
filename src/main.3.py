from LunaPre import *


Positions().Move2Path([[0,0,0],[-100,50,0],[100,50,0],[100,-50,0],[-100,-50,0]],0.8)

from BasicFuc import *
while(1):
    ball = Positions().AbsBallPos()
    if ball == [0xfff,0xfff]:
        continue
    if ball == [0xddd,0xddd]:
        peripheral.ShootBall()
        time.sleep(0.5)
        break
    else:
        LockSeries().LockBallSlip()

chassis.stop()

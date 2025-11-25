from LunaPre import *

def ChasingBall():
    iBX,iBY = Positions.Relative_Ball_Position()
    Compass = chassis.GetYaw()
    Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
    AbsAngle = Angle + Compass
    Kp = 1.5
    SpeedX = iBX * Kp
    SpeedY = iBY * Kp
    chassis.AbsMoveVetor(SpeedX,SpeedY,AbsAngle) # 1.5 is a factor to make the robot turn faster, you can adjust it as needed


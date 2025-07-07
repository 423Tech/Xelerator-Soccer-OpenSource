#### HEADER ####
from ReasonData import QkJson, Positions
from kits import *
import signal
#### HEADER ####
logger.info("Starting Xelerator")

while True:
    # Stop the chassis
    try:
        # Lockballmove()
        # Offence()
        BallFlag = False
        # logger.debug("Current Position: %s" % AbsBallPos())
        if AbsBallPos() == [0, 0]:
            logger.info("Ball not found, stopping chassis.")
            Pos2Pos([0, 0, 0], False)
            peripheral.StopDribble()
            
        elif AbsBallPos() == [1207, 1207]:
            logger.success("Ball is at the Front, stopping chassis.")
            BallFlag = True
            # peripheral.Dribble(True)
            # while not abs(compass()) <= 10:
                # chassis.GoA(0, 100, 100)

        else:
            BallFlag = False
            logger.info("Ball is in possession, finding.")
            Lockballslip()
        if BallFlag:
            logger.info("Ball is in possession, stopping chassis.")
            # chassis.GoV(0,Pos2Angle(GetPos(), [0,90]),100)
            Pos2Pos([0,80,Pos2Angle(GetPos(), [0,90])],False)
            # Move2Path([80,0,Pos2Angle(GetPos(), [0,90])],False)
            peripheral.ShootBall()
        if BallFlag and AbsBallPos() == [1207, 1207] and GetPos()[1] < 80:
            peripheral.ShootBall()
        # Defence()
        # Pos2Pos([0, 40, 30])
        # logger.debug(Bits.get_motor_encoder())
    except KeyboardInterrupt:
        chassis.stop()
        peripheral.StopDribble()
        break
    # print(chassis.Compass())
    # Pos2Pos([0,0,30])
    # Move2Path([[0,0,0],[40,40,0],[40,-40,0]],0)
    # print(compass())
    # print(GetBallPos())
    



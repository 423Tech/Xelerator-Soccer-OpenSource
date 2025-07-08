#### HEADER ####
from ReasonData import QkJson, Positions
from kits import *
import signal
#### HEADER ####
logger.info("Starting Xelerator")

while True:
    # Stop the chassis
    try:
        peripheral.DribbleBall()
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
            # for _ in range(20):
            #     Pos2Pos([0,80,0],False)
            # Move2Path([80,0,Pos2Angle(GetPos(), [0,90])],False)
            for _ in range(20):
                X,Y,_ = GetPos()
                DeltaY = 100 - Y
                DeltaX = X
                Theta = math.atan2(DeltaY, DeltaX)
                Theta = math.degrees(Theta)
                Compass = -(90 - Theta)
                chassis.GoZ(Compass)
                time.sleep(0.03)
                # chassis.GoA(Compass, Compass, 100)
            peripheral.ShootBall()
            BallFlag = False
        # if BallFlag and AbsBallPos() == [1207, 1207] and GetPos()[1] < 80:
        #     peripheral.ShootBall()
        # Defence()
        # Pos2Pos([0, 40, 30])
        logger.debug(Bits.get_motor_encoder())
    except KeyboardInterrupt:
        chassis.stop()
        peripheral.StopDribble()
        break
    time.sleep(0.03)
    # print(chassis.Compass())
    # Pos2Pos([0,0,30])
    # Move2Path([[0,0,0],[40,40,0],[40,-40,0]],0)
    # print(compass())
    # print(GetBallPos())
    



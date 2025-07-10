#### HEADER ####
from ReasonData import QkJson, Positions
from kits import *
import signal
from OD import *
from Defence_link import *
#### HEADER ####
logger.info("Starting Xelerator")

while True:
    # Stop the chassis
    try:
        # peripheral.DribbleBall()
        # Lockballmove()
        # Offence()
        BallFlag = False
        x,y = AbsBallPos()
        logger.debug("Current Position: %s" % [x,y])
        if [x,y] == [1024, 1024]:
            logger.info("Ball not found, stopping chassis.")
            Pos2Pos([0, 0, 0], False, 200)
            peripheral.StopDribble()
        elif [x,y] == [1207, 1207]:
            peripheral.Dribble(True)
            logger.success("Ball is at the Front, Dribble.")
            BallFlag = True
            # while not abs(compass()) <= 10:
                # chassis.GoA(0, 100, 100)
        else:
            BallFlag = False
            logger.info("Ball is in possession, finding.")
            lBallPos = GetBallPos()
            logger.warning(lBallPos)
            iBX,iBY = lBallPos[0],lBallPos[1]
            Compass = chassis.GetYaw()
            Angle = (math.degrees(math.atan2(iBX, iBY)) + 360) % 360
            Fangle = Angle + Compass
            chassis.GoV(iBX*4,iBY*4,Fangle) # 1.5 is a factor to make the robot turn faster, you can adjust it as needed
            peripheral.Dribble(True)
        if BallFlag and GetPos()[1] > 70:
            peripheral.Dribble(True)
            logger.info("Ball is in possession, start shotting.")
            # chassis.GoV(0,Pos2Angle(GetPos(), [0,90]),100)
            # for _ in range(20):
            #     Pos2Pos([0,80,0],False)
            # Move2Path([80,0,Pos2Angle(GetPos(), [0,90])],False)
            for _ in range(20):
                if not [x,y] == [1207, 1207]:
                    break
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
        elif BallFlag:
            peripheral.Dribble(True)
            logger.info("Ball is not in possession, moving chassis.")
            chassis.GoA(0,0,70)
        # if BallFlag and AbsBallPos() == [1207, 1207] and GetPos()[1] < 80:
        #     peripheral.ShootBall()
        # Defence()
        # Pos2Pos([0, 40, 30])
        # logger.debug(Bits.get_motor_encoder())
    except KeyboardInterrupt:
        chassis.stop()
        peripheral.StopDribble()
        break
#     # print(chassis.Compass())
#     # Pos2Pos([0,0,30])
#     # Move2Path([[0,0,0],[40,40,0],[40,-40,0]],0)
#     # print(compass())
#     # print(GetBallPos())
    

# while True:
#     try:
#         Move2Path([[0,0,0],[30,70,90]],0)
#     except KeyboardInterrupt:
#         chassis.stop()
#         peripheral.StopDribble()
#         break
# cache = GetPos()

# while(1):
#     time.sleep(0.1)
#     cache2 = GetPos()
#     logger.debug("Error X: %s,Error Y: %s" % (int(cache[0] - cache2[0]),int(cache[1] - cache2[1])))
#     logger.debug(" X: %s, Y: %s" % (int(cache2[0]),int(cache2[1])))
#     cache = cache2

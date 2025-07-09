#### HEADER ####
from ReasonData import QkJson, Positions
from kits import *
import signal
#### HEADER ####
logger.info("Starting Xelerator")

while True:
    # Stop the chassis
    try:
        # peripheral.DribbleBall()
        # Lockballmove()
        # Offence()
        # OHMYBACK()
        Slipsideshot()
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
    
# cache = GetPos()

# while(1):
#     time.sleep(0.1)
#     cache2 = GetPos()
#     logger.debug("Error X: %s,Error Y: %s" % (int(cache[0] - cache2[0]),int(cache[1] - cache2[1])))
#     logger.debug(" X: %s, Y: %s" % (int(cache2[0]),int(cache2[1])))
#     cache = cache2

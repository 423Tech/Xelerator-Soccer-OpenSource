#### HEADER ####
from ReasonData import QkJson, Positions
from kits import *
import signal
#### HEADER ####
logger.info("Starting Xelerator")

while True:
    # Stop the chassis
    try:
        Defence()
    except KeyboardInterrupt:
        chassis.stop()
        break
    # print(chassis.Compass())
    # Pos2Pos([0,0,30])
    # Move2Path([[0,0,0],[40,40,0],[40,-40,0]],0)
    # print(compass())
    # print(GetBallPos())
    



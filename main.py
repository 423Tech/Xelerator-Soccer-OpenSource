#### HEADER ####
from ReasonData import QkJson, Positions
from kits import *
import signal
from OD import *
from Defence_link import *
#### HEADER ####
logger.info("Starting Xelerator")
while True:
    try:
        # Pos2Pos([0,0,0],True)
        print(AbsBallPos())
        print(AbsChassisAngle())
    except KeyboardInterrupt:
        chassis.stop()
        peripheral.StopDribble()
        break
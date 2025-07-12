#### HEADER ####
from ReasonData import QkJson, Positions
from kits import *
from OD import *
import signal
from Defence_link import *
from Defence_Follow_panning import*
from Defence_Follow_ratio import*

#### HEADER ####
logger.info("Starting Xelerator")

while True:
    # Stop the chassis
    try:
        print(CEnemyPos())
    except KeyboardInterrupt:
        chassis.stop()
        peripheral.StopDribble()
        break

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

Role()

while True:
    if Bits.GetKey():
        break
    time.sleep(0.01)

while True:
    try:
        DefenceLink(1)
    except KeyboardInterrupt:
        chassis.stop()
        peripheral.StopDribble()
        break

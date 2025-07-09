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
        # Slipsideshot([0,0],[0,70])
        LockDoor()
        logger.debug(Bits.get_motor_encoder())
    except KeyboardInterrupt:
        chassis.stop()
        peripheral.StopDribble()
        break

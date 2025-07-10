#### HEADER ####
from ReasonData import QkJson, Positions
from kits import *
from OD import *
import signal
#### HEADER ####
logger.info("Starting Xelerator")

while True:
    # Stop the chassis
    try:
        # peripheral.DribbleBall()
        # Lockballmove()
        # Offence()
        # Defence()
        Role()
        # OHMYBACK()
        # Slipsideshot([0,0],[0,90])
        # MacaoShot(30,90,100)
        # Pos2Pos([0,70,400])
        # LockDoor()
        # logger.debug(Bits.get_motor_encoder())
    except KeyboardInterrupt:
        chassis.stop()
        peripheral.StopDribble()
        break

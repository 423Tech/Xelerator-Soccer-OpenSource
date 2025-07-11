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
        # peripheral.DribbleBall()
        # Lockballmove()
        # Offence()
<<<<<<< HEAD
        FollowPRatio(0)
        # FollowPPanning()
        # OD()
        # OffDenfence()
        # FollowPPanning(0)
        # DefenceLink(0)
=======
        # FollowPRatio()?
        OD()
        # DefenceLink()
>>>>>>> 8c40b55 (1234)
        # OHMYBACK()
        # logger.debug(Bits.get_motor_encoder())
    except KeyboardInterrupt:
        chassis.stop()
        peripheral.StopDribble()
        break

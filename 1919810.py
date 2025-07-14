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

def KeyEvent():
    KeyCount = 0
    LastPressed = False
    while True:
        if LastPressed == True:
            if Bits.GetKey():
                KeyCount = KeyCount + 1
            else:
                LastPressed = False
        else:
            if Bits.GetKey():
                LastPressed = True
                KeyCount = KeyCount + 1

KeyEventThread = threading.Thread(target=KeyEvent)
KeyEventThread.daemon = True
KeyEventThread.start()


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

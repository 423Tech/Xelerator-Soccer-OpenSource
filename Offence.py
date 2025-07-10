from kits import *

while True:
    try:
        Lockballslip()
        print(GetBallPos())
        time.sleep(.03)
    except KeyboardInterrupt:
        print("Exiting...")
        chassis.stop()
        break
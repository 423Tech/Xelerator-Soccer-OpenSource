from LunaPre import *

while(1):
    try:
        print(Positions().AbsRoboPosition())
        chassis.AbsMoveVetor(0,50,0)
    except KeyboardInterrupt:
        chassis.stop()
        break
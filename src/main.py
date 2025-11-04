from LunaPre import chassis
import time


for i in range(10):
    chassis.AbsMoveVetor(100,0,0)
    time.sleep(0.2)

for i in range(10):
    chassis.AbsMoveVetor(0,-100,0)
    time.sleep(0.2)

for i in range(10):
    chassis.AbsMoveVetor(-100,0,0)
    time.sleep(0.2)

for i in range(10):
    chassis.AbsMoveVetor(0,100,0)
    time.sleep(0.2)

chassis.stop()
import sensor,image,lcd,math,time,pyb
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,lidar
from pyb import UART

def supermove(iMovingAngle:int, AdditionAngle:int, iTime:int, iSpeed:int):
    for a in range(0,AdditionAngle,AdditionAngle/iTime):
        car.z_move(iMovingAngle+a, AdditionAngle+a,iSpeed)

while(key.read()==0):
    pass

while(1):
    supermove(0,200,10,100)

# RoboCAT - By: 423T - 2025/3/26
import sensor,image,lcd,math,time,pyb
from pyb import UART
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led
import binascii
import framebuf
delay.ms(2000)

from level5 import *

#TODO



lcd.init()
lcd.set_backlight(60)
# clock = time.clock()
# set_motor.PID(2.5,0.3,1.3)          #设置电机PID参数
fborder=2
bborder=4
lborder=2
rborder=2
bbdh=0
lbdh=0
rbdh=0
fx=0
fy=0
bx=0
by=0


# From config.py | RCJ2025032600PROD

def getadc():
    global irl,irf,irr,irb,dhl,dhb,dhr,bx,by
    b = GetBallPos()
    bx = b[0]
    by = b[1]
    d = GetDists()
    irf = d[0]/100
    irl = d[1]/100
    irb = d[2]/100
    irr = d[3]/100


def dribble_ball(status):      #盘球
    if status==1:
       set_io.out(13,1)
       set_io.out(14,0)
    elif status==-1:
       set_io.out(13,0)
       set_io.out(14,1)
    else:
       set_io.out(13,0)
       set_io.out(14,0)

def read_dribbling_current():   #盘球电流
        return set_adc.read(13)

def kick_ball(status):           #弹射
    if status==1:
        set_io.out(1,1)
    else:
        set_io.out(1,0)

def motor_test():
    set_motor.RPM(100,0,0,0)
    delay.s(1)
    set_motor.RPM(0,100,0,0)
    delay.s(1)
    set_motor.RPM(0,0,100,0)
    delay.s(1)
    set_motor.RPM(0,0,0,100)
    delay.s(1)
    set_motor.RPM(0,0,0,0)
    delay.s(1)

def go4(x,y,z,w):           #x  z
    set_motor.RPM(x,y,z,w)  #y  w

def go_v(x,y):          #向量 -y x
    go4(y,x,x,y)          #-x y

def go_x(x):            #X方向
    car.cross(90,x,5,5)

def go_y(y):            #Y方向
    car.straight(0,y,5,5)

def go_z(z):            #俯视顺时针转
    go4(z,z,-z,-z)

def move(x,y):    #xy方向移动
    spd=math.sqrt(x**2+y**2)
    go_v(int(spd*math.sin(math.atan2(y,x)-math.radians(45))),int(spd*math.cos(math.atan2(y,x)-math.radians(45))))
#    print("spdx=%d,spdy=%d"%(int(spd*math.cos(math.atan2(y,x)-math.radians(45))),int(spd*math.sin(math.atan2(y,x)-math.radians(45)))))

def wait(s):
    delay.ms(int(s*1000))

def sound(f,d):
    beep.frequency(f)
    delay.ms(d)
    beep.frequency(0)

def turn_to(degree):
    set_led.out(3,1)
    car.turn(degree,4,30,10,1)
    set_led.out(3,0)

def go_back():
    set_led.out(2,1)
    turn_to(0)
    if(irb<30):
        go_y((30-irb)*10)
    elif(irb<40):
        if(abs(irl-irr)>30):
            go_x((irr-irl)*10)
        else:
            go_z(0)
    elif(abs(irl-irr)>30):
        move((irr-irl)*10,-irb*10)
    else:
        go_y(-irb*6)
    set_led.out(2,0)

def offense():
    if(fy>160):
        if(fx>150 and fx<170):
            dribble_ball(1)
            if(irl<50):
                car.straight(30,1000,5,10)
            elif(irr<50):
                car.straight(330,1000,5,10)
            else:
                go_y(1000)
            sound(1222,222)
            dribble_ball(-1)
            kick_ball(1)
            go_y(0)
            sound(888,188)
            dribble_ball(0)
            kick_ball(0)
        elif(fx<=150):
            if(irb<44):
                go_x(-300)
            else:
                go_v(0,-300)
        elif(fx>=170):
            if(irb<44):
                go_x(300)
            else:
                go_v(-300,0)
    else:
        move((fx-160)*6,(240-fy)*4)

def defense():
    if(by>80):
        if(bx>75 and bx<150):
            go_y(0)
        elif(bx<=75):
            go_x(150)
        elif(bx>=150):
            go_x(-150)
    else:
        move((160-bx)*7,(by-240)*4)

def follow():
    turn_to(0)
    if(fx>0 or fy>0):
        if(irf<=44):
            if(fx<=150 and irl>lborder):
                go_x(-150)
            elif(fx>=170 and irr>rborder):
                go_x(150)
            elif(dhl>lbdh and dhr>rbdh and dhb>bbdh):
                go_y(88)
            else:
                go_z(0)
        elif(irl<=lborder or irr<=rborder):
            if(fx<=150 or fx>=170 and fy>160):
                go_y(0)
            elif(fx<=150 or fx>=170):
                go_y(150)
            else:
                offense()
        else:
            offense()
    else:
        if(irb<=44):
            if(bx>=150 and irl>lborder):
                go_x(-150)
            elif(bx<=75 and irr>rborder):
                go_x(150)
            else:
                go_z(0)
        elif(irl<=lborder or irr<=rborder):
            if(bx<=75 or bx>=150 and by>130):
                go_y(0)
            elif(bx<=75 or bx>=150):
                go_y(-160)
            else:
                defense()
        else:
            defense()

def screen():
    img = image.Image(160,120,sensor.RGB565,copy_to_fb=True)
#    for i in range(6):
#        img.draw_string(i*50,192,"%4d"% (set_adc.read(i+1)),color=(255,0,255),scale=2)
#    for i in range(6):
#        img.draw_string(i*50,208,"%4d"% (set_adc.read(i+7)),color=(255,0,255),scale=2)
    img.draw_string(0,222,"cmp%3d %.1fV %3dfps"% (compass.read(),set_adc.read(14)*11*3.3/1024+0.3,clock.fps()),color=(0,0,255),scale=2)
    img.draw_string(0,190,"f%3d b%3d l%3d r%3d"% (irf,irb,irl,irr),color=(0,0,255),scale=2)
    img.draw_string(0,0,"fx%3dfy%3dbx%3dby%3d"% (fx,fy,bx,by),color=(255,0,0),scale=2)
    img.draw_string(0,206,"dh l:%3d b:%3d r:%3d"% (dhl,dhb,dhr),color=(0,0,255),scale=2)
    lcd.display(img.rotation_corr(zoom = 0.5))
#    lcd.display(img)


while(key.read()==0):
    # clock.tick()
#    omniview()
    screen()
#lcd.clear()
lcd.set_backlight(0)
#while(1):motor_test()
#while(1):
#    spd=300
#    go_x(spd)
#    wait(1)
#    go_y(spd)
#    wait(1)
#    go_v(0,-spd)
#    wait(1)
#    car.stop()
#    wait(1)
#while(1):
#    dribble_ball(0)
#    kick_ball(0)
#    wait(1)
#    dribble_ball(1)
#    kick_ball(1)
#    wait(1)
#主程序
while(True):
    # clock.tick()
    # omniview()
    if fx==0 and fy==0 and bx<13 and by<13:
        go_back()
    else:
        follow()
    # AutoObstacle()






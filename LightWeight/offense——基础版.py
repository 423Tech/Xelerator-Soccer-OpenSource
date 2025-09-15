import sensor,image,lcd,math,time,pyb
from pyb import UART
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,eyes
import binascii
import framebuf
lcd.init()
lcd.set_backlight(100)
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_auto_exposure(1)
sensor.set_auto_gain(0)
sensor.set_auto_whitebal(0)
sensor.set_saturation(3)
sensor.set_contrast(3)
sensor.set_hmirror(1)
sensor.set_vflip(1)
clock = time.clock()
fborder=16
bborder=14
lborder=12
rborder=12
fbdh=760
bbdh=770
lbdh=840
rbdh=810
ball=12
fx=0
fy=0
bx=0
by=0
AcReDis=0
uart3_Eyes_Max_Num = 0
uart3_Eyes_Max_Value = 0
uart5_Eyes_Max_Num = 0
uart5_Eyes_Max_Value = 0
car.set_speed_PID(3,2,1)
speed = 100
aim_angle = 0
set_motor.ratio(21)
ExposureUS = 60000
GainDB = 1
def getadc():
    global irl,irf,irr,irb,dhf,dhb,dhl,dhr
    irl = set_adc.read(6)/3.5
    irf = set_adc.read(7)/3.5
    irr = set_adc.read(4)/3.5
    irb = set_adc.read(5)/3.5
    dhl = set_adc.read(11)
    dhr = set_adc.read(9)
    dhf = set_adc.read(12)
    dhb = set_adc.read(10)
def dribble_ball(status):
    if status==1:
       set_io.out(13,1)
       set_io.out(14,0)
    elif status==-1:
       set_io.out(13,0)
       set_io.out(14,1)
    else:
       set_io.out(13,0)
       set_io.out(14,0)
def read_dribbling_current():
        return set_adc.read(13)
def kick_ball(status):
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
def go4(x,y,z,w):
    set_motor.RPM(x,y,z,w)
def go_v(x,y):
    go4(y,x,x,y)
def go_x(x):
    go_v(-x,x)
def go_y(y):
    go_v(y,y)
def go_z(z):
    go4(z,z,-z,-z)
def move(x,y):
    spd=math.sqrt(x**2+y**2)
    go_v(int(spd*math.sin(math.atan2(y,x)-math.radians(45))),int(spd*math.cos(math.atan2(y,x)-math.radians(45))))
def wait(s):
    delay.ms(int(s*1000))
def sound(f,d):
    beep.frequency(f)
    delay.ms(d)
    beep.frequency(0)
def turn_to(degree,bias):
    set_led.out(3,1)
    while(degree>=360):
        degree = degree-360
    while(degree<0):
        degree = degree+360
    dlt = compass.read()-degree
    while(abs(dlt)>bias):
        if(dlt>bias):
            if(dlt>180):
                go_z(10+(360-dlt)*2)
            else:
                go_z(-10-dlt*2)
        elif(dlt<-bias):
            if(dlt<-180):
                go_z(10+(360+dlt)*2)
            else:
                go_z(-10-dlt*2)
        dlt = compass.read()-degree
    go_z(0)
    set_led.out(3,0)
def go_back_defense():
    turn_to(0,10)
    set_led.out(2,1)
    spdx=0
    spdy=0
    if(irb>36):
        spdy=-irb*13
    elif(irb<25):
        spdy=(36-irb)*15
    else:
        spdy=0
    if(abs(irl-irr)<10):
        spdx=0
    else:
        spdx=(irr-irl)*30
    move(spdx,spdy)
    set_led.out(2,0)
def follow():
    if(fx>bx):
        if(irf<=34):
            if(fy>4 and irl>lborder):
                go_x(-300)
            elif(fy<4 and irr>rborder):
                go_x(300)
            elif(fy==4 and dhf>fbdh and dhl>lbdh and dhr>rbdh and dhb>bbdh):
                if(irr>irl):
                    go_x(100)
                    delay.s(0.3)
                    offense()
                elif(irl>irf):
                    go_x(-100)
                    delay.s(0.3)
                    offense()
            else:
                spdx=0
                spdy=0
                if(irb>30):
                    spdy=-irb*7
                elif(irb<20):
                    spdy=(30-irb)*10
                else:
                    spdy=0
                if(abs(irl-irr)<30):
                    spdx=0
                else:
                    spdx=(irr-irl)*10
                move(spdx,spdy)
        elif(irl<=lborder):
            if(fy==7):
                go_y(0)
            elif(fy>4):
                go_y(300)
            else:
                offense()
        elif(irr<=rborder):
            if(fy==1):
                go_y(0)
            if(fy<4):
                go_y(300)
            else:
                offense()
        else:
            offense()
    else:
        spdx=0
        spdy=0
        if(irb>30):
            spdy=-irb*7
        elif(irb<20):
            spdy=(30-irb)*10
        else:
            spdy=0
        if(abs(irl-irr)<30):
            spdx=0
        else:
            spdx=(irr-irl)*10
        move(spdx,spdy)
def IAvFx():
    global Averagefx,FoBAvFx
    a = int(fx)
    FxA1 = a
    wait(0.001)
    FxA2 = a
    Averagefx = int((FxA2-FxA1)/2)
    if (Averagefx > 0):
        FoBAvFx = 1
    elif(Averagefx <0):
        FoBAvFx = 2
    else:
        FoBAvFx = 0
def defense_follow(i):
    if(fy==4):
        go_y(i)
    elif(fy==3):
        go_x(300)
    elif(fy==5):
        go_x(-300)
def defense_Robot():
    IAvFx()
    if (bx > 50):
        if (fx < 2400):
            go_back()
        if (2400<= fx <3000):
            defense_follow(100)
        elif(3000 <= fx <3500):
                if (FoBAvFx == 1):
                    defense_follow(80)
                if (FoBAvFx == 2):
                    defense_follow(-80)
                if (FoBAvFx == 0):
                    defense_follow(0)
        elif(3500<= fx <4000):
                defense_follow(0)
        else:
            go_back()
    elif(bx <= 50):
        defense_follow(80)
def defense():
    if(bx>500):
        if(by==4):
            go_y(0)
        elif(by==3):
            go_x(-300)
        elif(by==5):
            go_x(300)
        else:
            go_y(-300)
    else:
        spd=int(bx/3-1500)
        rad=math.radians((4-by)*30)
        move(spd*math.sin(rad),spd*math.cos(rad))
def follow_ball():
    if(fy==1 or fy==7):
        go_y(-300)
    elif(fy==3 or fy==2):
        go_x(100)
    elif(fy==5 or fy==6):
        go_x(-100)
    else:
        go_y(400)
        dribble_ball(1)

def go_back_defense():
    turn_to(0,10)
    set_led.out(2,1)
    spx=0
    spy=0
    if(irb>36):
        spy=-irb*30
    elif(irb<25):
        spy=(36-irb)*15
    else:
        spy=0
    if(abs(irl-irr)<10):
        spx=0
    else:
        spx=(irr-irl)*30
    move(spx,spy)
    set_led.out(2,0)

def search_ball():
    spdx=0
    spdy=0
    if(fy==4):
        spdx = 0
        spdy = 1000
    elif(fy>4):
        dribble_ball(0)
        spdx=-800
        if fx > 2900:
            spdy = 0
        else:
            spdy =700
    else:
        dribble_ball(0)
        spdx=800
        if fx > 2900:
            spdy = 0
        else:
            spdy = 700
    move(spdx,spdy)

def defense_robot():
    turn_to(0,15)
    set_led.out(2,1)
    spdx=0
    spdy=0
    if irf >= 30:
        if( fx > 100):
            if(lborder > irl):
                spdx = 250
            elif(rborder > irr):
                spdx = -250
            else:
                if(irb<=34):
                    spdy=(34-irb)*20
                    search_ball()
                else:
                    spdy=0
                    search_ball()
                if(abs(irl-irr)<20):
                    search_ball()
                else:
                    spdx=(irr-irl)*30
                    search_ball()
        else:
            spdx = 0
            spdy = 0
            go_back_defense()
    else:
        spdx = 0
        spdy = 0
        go_back_defense()
    move(spdx,spdy)
    set_led.out(2,0)
    ###################################################3


def follow_ballxc():
    if(fx<2850):
        if(fy==1 or fy==7):
            car.straight(0,-100)
        elif(fy==3):
            car.z_move(0,45,50)
        elif(fy==2):
            car.straight(0,-50)
        elif(fy==5):
            car.z_move(0,315,50)
        elif(fy==6):
            car.straight(0,-50)
        else:
            car.straight(0,50)
    else:
        go_z(0)
def offense():
    if(fx>2000):
        if(fx>3000 and 3<=fy<=5):
            dribble_ball(1)
            if(irr<=48):
                go_x(-300)
            elif(irl<=48):
                go_x(300)
            else:
                go_y(1000)
                delay.ms(50)
                go_y(0)
                omniview()
        else:
            follow_ball()
    else:follow_ball()
def omniview():
    global fx,fy,bx,by,dianliu
    fx = eyes.value(3)
    fy = eyes.ch(3)
    bx = eyes.value(5)
    by = eyes.ch(5)
    dianliu = set_adc.read(13)
while(1):
    img = image.Image(160,128,sensor.RGB565,copy_to_fb=True)
    uart3_Eyes_Max_Num = eyes.ch(3)
    uart3_Eyes_Max_Value = eyes.value(3)
    uart5_Eyes_Max_Num = eyes.ch(5)
    uart5_Eyes_Max_Value = eyes.value(5)
    omniview()
    img.draw_string(60,0,"by:%d" % (eyes.value(5)),color=(0,255,255),scale=1)
    img.draw_string(60,10,"bx:%d" % (eyes.ch(5)),color=(0,255,255),scale=1)
    img.draw_string(60,20,"compass:%d" % (compass.read()),color=(255,255,0),scale=1)
    img.draw_string(60,30,"vbat:%.1fV" % (set_adc.read(14)*3.3*11/1024),color=(255,255,0),scale=1)
    img.draw_string(60,40,"fx:%d"%(eyes.value(3)),color=(0,255,255),scale=1)
    img.draw_string(60,50,"fy:%d"%(eyes.ch(3)),color=(0,255,255),scale=1)
    img.draw_string(60,60,"dianliu:%d"%(set_adc.read(13)),color=(0,255,255),scale=1)
    img.draw_string(80,70,"ADC4:%d"%(set_adc.read(4)/3.5),color=(0,255,255),scale=1)
    img.draw_string(80,80,"ADC5:%d"%(set_adc.read(5)/3.5),color=(0,255,255),scale=1)
    img.draw_string(80,90,"ADC6:%d"%(set_adc.read(6)/3.5),color=(0,255,255),scale=1)
    img.draw_string(80,100,"ADC7:%d"%(set_adc.read(7)/3.5),color=(0,255,255),scale=1)
    lcd.display(img)
    getadc()
    if(key.read()==1):
        delay.ms(500)
        break

while(1):
    getadc()
    omniview()
    defense_robot()


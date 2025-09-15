import sensor,image,lcd,math,time,pyb
from pyb import UART
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,eyes
import binascii
import framebuf
lcd.init()
lcd.set_backlight(100)
sensor.set_auto_exposure(1)
sensor.set_saturation(3)
sensor.set_contrast(3)
sensor.set_hmirror(1)
sensor.set_vflip(1)
sensor.set_auto_exposure(1)
sensor.reset()
sensor.set_pixformat(sensor.RGB565)
sensor.set_framesize(sensor.QVGA)
sensor.set_auto_gain(0)
sensor.set_auto_whitebal(0)
sensor.set_vflip(1)
clock = time.clock()
threshold_index = 0
door_thresholds = [(46, 100, -128, 0, 89, 45),
                   (37, 100, -128, 29, 127, 43),
                   (85, 100, -128, 27, 75, 33),
                   (30, 100, -128, 53, 127, 46)]
door_ROI=(0,16,320,224)
area = 0
clock = time.clock()
fborder=30
bborder=30
lborder=14
rborder=14
fbdh=760
bbdh=770
lbdh=840
rbdh=810
ball=12
fx=0
fy=0
bx=0
by=0
irl=0
irb=0
irr=06
irf=0
AcReDis=0
get_ball = 0
area = 0
def omniview():
    global fx,fy,bx,by,dianliu
    fx = eyes.value(3)
    fy = eyes.ch(3)
    bx = eyes.value(5)
    by = eyes.ch(5)
    dianliu = set_adc.read(13)
def camera():
    area = 0
    global door_thresholds,threshold_index
    img = sensor.snapshot()
    for blob in img.find_blobs([door_thresholds[threshold_index]], pixels_threshold=200, area_threshold=200, merge=True):
        if blob.elongation() > 0.5:
            img.draw_edges(blob.min_corners(), color=(255,0,0))
            img.draw_line(blob.major_axis_line(), color=(0,255,0))
            img.draw_line(blob.minor_axis_line(), color=(0,0,255))
        img.draw_rectangle(blob.rect())
        img.draw_cross(blob.cx(), blob.cy())
        img.draw_keypoints([(blob.cx(), blob.cy(), int(math.degrees(blob.rotation())))], size=20)
        x, y, w, h = blob.rect()
        area1 = w * h
        wait(0.01)
        area2 = w * h
        area =int(area1+area2/800)
uart3_Eyes_Max_Num = 0
uart3_Eyes_Max_Value = 0
uart5_Eyes_Max_Num = 0
uart5_Eyes_Max_Value = 0
car.set_speed_PID(0.9,0.8,1)
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
def omniview():
    global fx,fy,bx,by,dianliu
    fx = eyes.value(3)
    fy = eyes.ch(3)
    bx = eyes.value(5)
    by = eyes.ch(5)
    dianliu = set_adc.read(13)
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
def go_back():
    if(irb>=64):
        car.z_move(0,180,-500)
    else:
        if(irr<90):
            car.z_move(0,90,300)
        if(irl<90):
            car.z_move(0,270,300)
        else:
            go_z(0)
def follow():
    if(fx>bx):
        if(irf<=30):
            if(fy>4 and irl>lborder):
                car.z_move(0,270,300)
            elif(fy<4 and irr>rborder):
                car.z_move(0,90,300)
            elif(fy==4 and dhf>fbdh and dhl>lbdh and dhr>rbdh and dhb>bbdh):
                go_y(88)
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
                car.z_move(0,0,300)
            else:
                offense()
        elif(irr<=rborder):
            if(fy==1):
                go_y(0)
            if(fy<4):
                car.z_move(0,0,300)
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
def follow_ball():
    if(fy==1 or fy==7):
        car.straight(0,-300)
    elif(fy==3 or fy==2):
        car.z_move(0,45,100)
    elif(fy==5 or fy==6):
        car.z_move(0,315,100)
    else:
        car.z_move(0,0,100)
        dribble_ball(1)
def control_ball():
    global get_ball
    dian1 = set_adc.read(13)
    wait(0.01)
    dian2 = set_adc.read(13)
    wait(0.01)
    dian3 = set_adc.read(13)
    dian_a = int((dian1 + dian2 + dian3)/3)
    if dian_a > 100:
        get_ball = 1
    else:
        get_ball = 0
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
def defense_robot2():
    turn_to(0,10)
    set_led.out(2,1)
    spdx=0
    spdy=0
    if irb < 90:
        if( fx > 50):
            spdy =int((fx-800)/2)
            if(lborder <= irl <= 46 or irr > 75):
                if(irb<=14):
                    spdy=(14 - irb)*10
                    search_ball()
                else:
                    spdy=0
                    search_ball()
            elif(rborder <= irr <= 46 or irl > 75):
                if(irb<=14):
                    spdy=(14 - irb)*10
                    search_ball()
                else:
                    spdy=0
                    search_ball()
            elif(lborder > irl):
                spdx = 250
            elif(rborder > irr):
                spdx = -250
            elif(75>=irl>46 or 75>=irr>46 ):
                if(irb<=34):
                    spdy=(34-irb)*15
                    search_ball()
                else:
                    spdy=0
                    search_ball()
                if(abs(irl-irr)<20):
                    spdx=0
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

def search_ball():
    spdx=0
    spdy=0
    if(fy==4):
        spdx=0
        dribble_ball(1)
        if fx > 2900:
            spdy = 0
        else:
            spdy =int(abs(2900-fx)/3)
    elif(fy>4):
        dribble_ball(0)
        spdx=-800
        if fx > 2900:
            spdy = 0
        else:
            spdy =int(abs(2900-fx)/5)
    else:
        dribble_ball(0)
        spdx=800
        if fx > 2900:
            spdy = 0
        else:
            spdy =int(abs(2900-fx)/5)
    move(spdx,spdy)

def defense_robot():
    turn_to(0,15)
    set_led.out(2,1)
    spdx=0
    spdy=0
    if  irf > 30 :
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





def offense():
    if(fx>2000):
        if(fx>3050 and 3<=fy<=5):
            dribble_ball(1)
            if(irr<=65):
                car.z_move(0,90,400)
            elif(irl<=65):
                car.z_move(0,270,400)
            else:
                kick_ball(1)
                go_y(0)
                kick_ball(0)
                omniview()
        else:
            follow_ball()
    else:
        follow_ball()

def face(h,l):
    global angle
    #h = 240
    #l = 187
    if irl >irr:
        x=(h-irb)/(irl - 0.4*l)
        angle = int(math.atan(x)/3.1415926*180)-360
    elif irr >irl:
        x=(h-irb)/(irr - 0.4*l)
        angle = int(math.atan(x)/3.1415926*180)
    else:
        angle = 0
  #########################################################################

def circle_around_ball(a,anglee):
    speed = 30
    r = 7.5
    # R = 10cm
    angle = 175
    if r <= 0:
        return
    if angle <= 0:
        return
    angle_rad = math.radians(angle)
    linear_speed_inside = speed * r
    linear_speed_outside = speed * r
    x_speedsin= int(linear_speed_inside* math.sin(angle_rad))
    y_speedcos= int(linear_speed_outside* math.cos(angle_rad))
    z_speedsin= int(linear_speed_inside * math.sin(angle_rad))
    w_speedcos= int(linear_speed_outside* math.cos(angle_rad))
    x = x_speedsin
    y = y_speedcos
    z =- z_speedsin
    w =- w_speedcos
    if (a == 1):
        go4(x,y,z,w)
    elif( a == -1 ):
        go4(z,w,x,y)
    else:
        go4(0,0,0,0)
    time = (anglee / angle)*0.81035
    wait(time)
    #time = length / speed
    #wait(time)
    go4(0, 0, 0, 0)
#circle_around_ball(1,90)

def Osearch_ball():
    if fy == 4:
        go4(0,0,0,0)
    elif fy == 3:
        go4(175,175,-175,-175)
    elif fy == 2:
        go4(215,215,-215,-215)
    elif fy == 1:
        go4(350,350,-350,-350)
    elif fy == 5:
        go4(-175,-175,175,175)
    elif fy == 6:
        go4(-215,-215,215,215)
    elif fy == 7:
        go4(-350,-350,350,350)
    else:
        go_back_defense()

def Lsearch_ball():
    turn_to(0,10)
    if fy == 4:
        vy = int((3010-fx)/10)
        move(0,vy)
    elif fy < 4 :
        move(100,0)
    elif 4 < fy <=7:
        move(-100,0)
    else:
        go_back_defense()


  #########################################################################
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
    img.draw_string(80,110,"dhf:%d"%(set_adc.read(12)),color=(0,255,255),scale=1)
    lcd.display(img)
    if(key.read()==1):
        delay.ms(500)
        break
while(1):
    getadc()
    omniview()
    defense_robot()

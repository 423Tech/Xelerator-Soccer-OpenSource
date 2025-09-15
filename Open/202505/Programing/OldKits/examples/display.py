import sensor,image,lcd,math,time,pyb
from pyb import UART
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,lidar
lcd.init()
lcd.set_backlight(100)
aim_angle = 0
speed=0
set_motor.ratio(21)
car.set_speed_PID(3,2,1)
car.set_soft_starter(500)
car.set_soft_stop(500)
car.set_move_fix(1.5,3)
car.set_turn_fix(3,1,1,200)
uartb = UART(5,115200)
uartf = UART(2,115200)
def getadc():
	global irl,irf,irr,irb,comp
	irl = int(set_adc.read(11)/1.5)
	irf = int(set_adc.read(12)/1.5)
	irr = int(set_adc.read(9)/1.5)
	irb = int(set_adc.read(10)/1.5)
	comp = compass.read()
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
		set_io.out(6,1)
	else:
		set_io.out(6,0)
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
	car.cross(90,x)
def go_y(y):
	car.straight(0,y)
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
def turn_to(degree,speed,bias):
	while(degree>=360):
		degree=degree-360
	while(degree<0):
		degree=degree+360
	while(True):
		delta=compass.read()-degree
		if(delta>bias):
			if(delta>180):
				go_z(speed)
			else:
				go_z(-speed)
		elif(delta<-bias):
			if(delta<-180):
				go_z(-speed)
			else:
				go_z(speed)
		else:
			go_z(0)
			break
def go_back():
	set_led.out(2,1)
	turn_to(0,100,10)
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
				car.straight(30,1000)
			elif(irr<50):
				car.straight(330,1000)
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
def isnum(s):
	try:
		x=int(s)
		return x
	except:
		return 400
def omniview():
	global fx,fy,bx,by
	if uartf.any()>=60:
		data=str(uartf.read())
		print(data)
		temp=data[data.index('rx')+2:data.index('ry',data.index('rx'))]
		fx=isnum(temp)
		temp=data[data.index('ry',data.index('rx'))+2:data.index('bx',data.index('ry',data.index('rx')))]
		fy=isnum(temp)
	if uartb.any()>=60:
		data=str(uartb.read())
		temp=data[data.index('rx')+2:data.index('ry',data.index('rx'))]
		bx=isnum(temp)
		temp=data[data.index('ry',data.index('rx'))+2:data.index('bx',data.index('ry',data.index('rx')))]
		by=isnum(temp)
	getadc()
i=0
fx=0
fy=0
bx=0
by=0
comp=0
while(key.read()==0):
	img = image.Image(160,128,sensor.RGB565,copy_to_fb=True)
	omniview()
	for i in range(1,15):
		img.draw_string(0,(i-1)*8,"ADC%d:%4d" % (i,set_adc.read(i)),color=(255,0,0),scale=1)
	img.draw_string(80,0,"comp:%3d" % (compass.read()),color=(0,255,255),scale=1)
	img.draw_string(80,8,"vbat:%.1fV" % (set_adc.read(14)*3.3*11/1024),color=(255,255,0),scale=1)
	img.draw_string(100,16,"fx:%4d" % (fx),color=(0,255,0),scale=1)
	img.draw_string(100,24,"fy:%4d" % (fy),color=(0,255,0),scale=1)
	img.draw_string(100,32,"bx:%4d" % (bx),color=(0,255,0),scale=1)
	img.draw_string(100,40,"by:%4d" % (by),color=(0,255,0),scale=1)
	img.draw_string(100,48,"irf:%3d" % (irf),color=(0,255,0),scale=1)
	img.draw_string(100,56,"irb:%3d" % (irb),color=(0,255,0),scale=1)
	img.draw_string(100,64,"irl:%3d" % (irl),color=(0,255,0),scale=1)
	img.draw_string(100,72,"irr:%3d" % (irr),color=(0,255,0),scale=1)
	lcd.display(img)
while(True):
	omniview()
	a=int((220-fy)*1.5)
	b=int((fx-160)*0.5)
	go4(a+b,a+b,a-b,a-b)
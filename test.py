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
i = 0
test_count = 0
while(1):
	img = image.Image(160,128,sensor.RGB565,copy_to_fb=True)
	lidar_buff=lidar.read()
	print(lidar_buff)
	for i in range(1,15):
		img.draw_string(0,(i-1)*8,"ADC%d:%d" % (i,set_adc.read(i)),color=(255,0,0),scale=1)
	img.draw_string(60,20,"compass:%d" % (compass.read()),color=(255,255,0),scale=1)
	img.draw_string(60,30,"vbat:%.1fV" % (set_adc.read(14)*3.3*11/1024),color=(255,255,0),scale=1)
	lcd.display(img)
	print(test_count)
	test_count = test_count +1
	if(test_count > 100000):
		test_count = 0
speed=200
ytime = 2000
xtime = 1500
while(1):
	car.straight_time(aim_angle,speed,ytime)
	delay.ms(500)
	aim_angle = aim_angle + 90
	car.turn(aim_angle)
	car.straight_time(aim_angle,speed,xtime)
	delay.ms(500)
	aim_angle = aim_angle + 90
	car.turn(aim_angle)
	car.straight_time(aim_angle,speed,ytime)
	delay.ms(500)
	aim_angle = aim_angle + 90
	car.turn(aim_angle)
	car.straight_time(aim_angle,speed,xtime)
	delay.ms(500)
	aim_angle = aim_angle + 90
	car.turn(aim_angle)
	if aim_angle>=360:
		aim_angle=aim_angle-360
import image,math,time,pyb,ujson
from pyb import UART
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led,lcd
try:
	with open('/data.json', "r") as File:
		Data = ujson.load(File)
		BoardType = Data['BoardType']
		ExposureUS = Data['ExposureUS']
		GainDB = Data['GainDB']
except Exception as e:
	print("读取 JSON 文件时出错:", e)
clock = time.clock()
CameraCenterX = 160
FetchedBallY = 65
iFrontIRPort = 6
iBackIRPort = 4
iLeftIRPort = 5
iRightIRPort = 7
DribblerPort = 13
RailGunPort = 1
iRearCamUARTPort = 5
iLeftCamUARTPort = 0
iRightCamUARTPort = 3
iBackCamUARTPort = 7
iCamBusUARTPort = 5
CarTurningSpeed = 50
DribbleWhenFetching = 0
AutoFetchBasicSpeed = 80
AutoOrbitInnerSpeed = 30
AutoOrbitOuterSpeed = 130
RPM50Velocity = 0.016089
CarMovingSpeed = 50
CoverToStart = False
iGlobalPIDK = 2
iFieldWidth = 114514
iFieldHeight = 1919810
iTof0 = 0
iTof1 = 0
iTof2 = 0
iTof3 = 0
lTofK = [1,1,1,1]
lTofB = [0,0,0,0]
lBallX = [0,0,0,0]
lBallY = [0,0,0,0]
lAbsDis = [0,0,0,0]
lAbsDisK = [1,1,1,1]
lAbsDisB = [0,0,0,0]
def MotorTest():
	for i in range(1,5,1):
		set_motor.out(i,1000)
		delay.s(1)
		set_motor.out(i,0)
		delay.s(1)
def GoY(Speed):
	set_motor.RPM(Speed,Speed,Speed,Speed)
def GoX(Speed):
	set_motor.RPM(Speed,-Speed,-Speed,Speed)
def GoV(iSpeedX,iSpeedY,iFacingAngle):
	global iGlobalPIDK
	iCMP = compass.read()
	iSpeedU = iSpeedX + iSpeedY
	iSpeedV = iSpeedY - iSpeedX
	iDeltaAngle = iCMP-iFacingAngle
	if iDeltaAngle > 180:
		iDeltaAngle = iDeltaAngle - 360
	set_motor.RPM(iSpeedU - iDeltaAngle * iGlobalPIDK,iSpeedV - iDeltaAngle * iGlobalPIDK,iSpeedV + iDeltaAngle * iGlobalPIDK,iSpeedU + iDeltaAngle * iGlobalPIDK)
def TurnTo(Angle):
	global CarTurningSpeed
	car.turn(Angle,1,CarTurningSpeed,1,100)
def Sound(Frequency,Time):
	beep.frequency(int(Frequency))
	delay.ms(Time)
	beep.frequency(0)
def LoadNotes(Filename):
	Notes = []
	try:
		with open(Filename, "r") as file:
			for Line in file:
				if Line.strip():
					Parts = Line.strip().split(",")
					Frequency = float(Parts[0])
					Duration = int(Parts[1])
					Notes.append((Frequency, Duration))
	except Exception as e:
		print("加载音符时出错：", e)
	return Notes
def Play(Filename):
	Notes = LoadNotes(Filename)
	for Note in Notes:
		Sound(Note[0],Note[1])
def GetADC():
	global iFrontIRPort,iBackIRPort,iLeftIRPort,iRightIRPort,iTof0,iTof1,iTof2,iTof3
	iTof0 = set_adc.read(iFrontIRPort) * lTofK[0] + lTofB[0]
	iTof1 = set_adc.read(iLeftIRPort) * lTofK[1] + lTofB[1]
	iTof2 = set_adc.read(iBackIRPort) * lTofK[2] + lTofB[2]
	iTof3 = set_adc.read(iRightIRPort) * lTofK[3] + lTofB[3]
def GetIO(IONumber):
	if set_io.read(IONumber,0)==1:
		return 1
	else:
		return 0
def getUART(Port):
	UARTDevice = UART(Port,115200)
	while(1):
		if UARTDevice.any():
			Data = str(UARTDevice.read())
			return Data
			break
def sendUART(iPort,sData):
	UARTDevice = UART(iPort,115200)
	UARTDevice.write(sData)
def Dribbler(State):
	global DribblerPort
	if State==1:
		set_io.out(DribblerPort,1)
	elif State==0:
		set_io.out(DribblerPort,0)
def RailGun(State):
	global RailGunPort
	if State == 1:
		set_io.out(RailGunPort,1)
		delay.ms(50)
		set_io.out(RailGunPort,0)
def RCReceiver():
	global iMaixCamUARTPort
	Dribbler(1)
	while(1):
		Data = getUART(iMaixCamUARTPort)
		try:
			X = int(Data[Data.index('x')+1:Data.index('y')])
			Y = int(Data[Data.index('y')+1:Data.index('speed')])
			Speed = int(Data[Data.index('speed')+5:Data.index('end')])
		except:
			continue
		if X != 0 and Y != 0:
			X = X / math.sqrt(X ** 2 + Y ** 2) * Speed
			Y = Y / math.sqrt(X ** 2 + Y ** 2) * Speed
			GoV(int(3*X),int(3*Y))
			if Speed == 160:
				RailGun(1)
		else:
			print('Stopped')
			car.stop()
def LCDDisplay():
	RearView()
	Img.draw_string(10,10,"Test:%d" % (114514),color=(255,255,0),scale=2)
	lcd.display(Img.rotation_corr(zoom=0.5))
def TurnToBall():
	global CarTurningSpeed
	RearView()
	if BX<0:
		CarTurningSpeed=-CarTurningSpeed
	while(1):
		set_motor.RPM(CarTurningSpeed,CarTurningSpeed,-CarTurningSpeed,-CarTurningSpeed)
		RearView()
		if BX>-10 and BX<10 and BY!=0:
			car.stop()
			break
def AutoFetch():
	global DribbleWhenFetching,AutoFetchBasicSpeed,FetchedBallY
	Dribbler(DribbleWhenFetching)
	TurnToBall()
	while(1):
		RearView()
		SpeedL = AutoFetchBasicSpeed + BX
		SpeedR = AutoFetchBasicSpeed - BX
		set_motor.RPM(SpeedL,SpeedL,SpeedR,SpeedR)
		if BX>-10 and BX<10 and BY>FetchedBallY-10 and BY<FetchedBallY+10:
			car.stop()
			break
def AutoOrbitTo(Angle):
	global AutoOrbitInnerSpeed,AutoOrbitOuterSpeed
	while(1):
		RearView()
		if BX<-30 or BX>30:
			TurnToBall()
		if BY<115:
			set_motor.RPM(-50,-50,-50,-50)
			delay.ms(20)
		if BY>130:
			set_motor.RPM(50,50,50,50)
			delay.ms(20)
		if Angle>compass.read()-2 and Angle<compass.read()+2:
			car.stop()
			TurnToBall()
			break
		set_motor.RPM(AutoOrbitInnerSpeed,-AutoOrbitOuterSpeed,-AutoOrbitInnerSpeed,AutoOrbitOuterSpeed)
def GoDistance(Angle,Distance):
	global RPM50Velocity
	Time = Distance/RPM50Velocity
	timer.start(10)
	while(timer.read(10)<Time):
		car.straight(Angle,50,1,5)
	car.stop()
	timer.clear(10)
def VelocityMeasurement():
	global RPM50Velocity
	TurnTo(0)
	while(1):
		GetADC()
		if DB<25:
			GoY(50)
			print(1)
		elif DB>35:
			GoY(-50)
			print(0)
		else:
			break
	timer.start(10)
	while(1):
		GetADC()
		car.straight(0,50,1,5)
		if 40<=DF<=50:
			print(3)
			break
	Time = timer.read(10)
	Speed = 142/Time
	car.stop()
	img=sensor.snapshot()
	img.draw_string(10,10,"Speed:%.6f" % (Speed),color=(255,255,0),scale=2)
	lcd.display(img.rotation_corr(zoom = 0.5))
	print(Speed)
def readCam():
	global iRearCamUARTPort,lBallX,lBallY,lAbsDis,lAbsDisK,lAbsDisB
	sRearData = getUART(iRearCamUARTPort)
	lBallX[0] = int(sRearData[sRearData.index('bx')+2:sRearData.index('by')]) * lAbsDisK[0] + lAbsDisB[0]
	lBallY[0] = int(sRearData[sRearData.index('by')+2:sRearData.index('ad')])
	lAbsDis[0] = int(sRearData[sRearData.index('ad')+2:sRearData.index('end')])
	sRightData = getUART(iRearCamUARTPort)
	lBallX[3] = int(sRightData[sRightData.index('bx')+2:sRightData.index('by')]) * lAbsDisK[3] + lAbsDisB[3]
	lBallY[3] = int(sRightData[sRightData.index('by')+2:sRightData.index('ad')])
	lAbsDis[3] = int(sRightData[sRightData.index('ad')+2:sRightData.index('end')])
	sBackData = getUART(iRearCamUARTPort)
	lBallX[2] = int(sBackData[sBackData.index('bx')+2:sBackData.index('by')]) * lAbsDisK[2] + lAbsDisB[2]
	lBallY[2] = int(sBackData[sBackData.index('by')+2:sBackData.index('ad')])
	lAbsDis[2] = int(sBackData[sBackData.index('ad')+2:sBackData.index('end')])
def GetPos():
	global iFieldWidth,iFieldHeight,lBallX,lBallY,lAbsDis
	readCam()
	Y = (lAbsDis[0] + (iFieldHeight-lAbsDis[2]))/2
	X = lBallX
def VGD(Angle,Aim):
	while(1):
		GetDistance()
		print(VDF)
		if VDF>Aim:
			car.straight(Angle,50,2,5)
		elif VDF<Aim:
			car.straight(Angle,-50,2,5)
		else:
			GetDistance()
			if VDF-5<=Aim<=VDF+5:
				break
			else:
				continue
while(1):
	if key.read()==1:
		break
while(1):
	GoV(200,150,0)
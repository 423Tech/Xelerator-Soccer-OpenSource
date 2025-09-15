import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
import numpy as np
import math
import multiprocessing as mp
import time
from collections import Counter
import serial
import subprocess
import cv2

#oLidarLaunchProcess = subprocess.Popen(['ros2', 'launch', 'ydlidar', 'ydlidar_launch.py'], stdout=subprocess.stdout, stderr=subprocess.stdout, start_new_session=False,shell=True)

oSerial = serial.Serial(
        port='/dev/serial0',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.01
    )

lCamPorts = [0,2,4,6]
lCams = []

tGreenHSV = (40, 80, 100, 255, 0, 255)
tOrangeLAB = (0, 255, 140, 190, 150, 190)
tOrangeHSV = (5, 10, 100, 255, 220, 255)
tBlueLAB = []
tYellowLAB = []

lPerspectiveMatrix = []
lPixelToCMK = []
lPixelToCMHorizontalB = []
lPixelToCMVerticalB = []

for i in range(4):
    NumpyData = np.load('/root/CalibrationData' + str(lCamPorts[i]) + '.npz')
    aPerspectiveMatrix = NumpyData['matrix']
    lPerspectiveMatrix.append(aPerspectiveMatrix)
    fPixelToCMK = NumpyData['p2c'][0]
    lPixelToCMK.append(fPixelToCMK)
    fPixelToCMHorizontalB = NumpyData['p2c'][1]
    lPixelToCMHorizontalB.append(fPixelToCMHorizontalB)
    fPixelToCMVerticalB = NumpyData['p2c'][2]
    lPixelToCMVerticalB.append(fPixelToCMVerticalB)


def GetUptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])
    return int(uptime_seconds)


class YDLidarParser(Node):
    def __init__(self,oQueue):
        super().__init__('ydlidar_parser')

        oQos = QoSProfile(
            reliability=QoSReliabilityPolicy.BEST_EFFORT,
            history=QoSHistoryPolicy.KEEP_LAST,
            depth=10,
            durability=QoSDurabilityPolicy.VOLATILE
        )
        
        self.subscription = self.create_subscription(
            LaserScan,
            '/scan',
            self.scanCallback,
            qos_profile=oQos)
        
        self.get_logger().info('YDLidar X3解析器已启动，等待数据...')
        
    def scanCallback(self, msg):
        lRanges = []

        fScanTime = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        fAngleMin = msg.angle_min
        fAngleMax = msg.angle_max
        fAngleIncrement = msg.angle_increment
        fRangeMin = msg.range_min
        fRangeMax = msg.range_max
        aRanges = msg.ranges
        iNumRanges = len(aRanges)
        for i in range(iNumRanges):
            iAngle = fAngleMin + i * fAngleIncrement
            lRanges.append((math.degrees(iAngle)+180, aRanges[i]))

        oQueue.put(lRanges)

def sendUART(oDevice, sData):
    oDevice.write(sData.encode('utf-8'))

def receiveUART(oDevice):
    while not oDevice.in_waiting:
        pass
    sData = oDevice.read(100)
    return sData.decode('utf-8')

def findMode(List):
    Count = Counter(List)
    return Count.most_common(1)


def getLineStandardEquation(tLine):

    x1, y1, x2, y2 = tLine
    
    A = y2 - y1
    B = x1 - x2
    C = x2*y1 - x1*y2

    return A, B, C

def getLineDistance(tLine, tPoint=(0,0)):
    fA, fB, fC = getLineStandardEquation(tLine)
    fDistance = (fA * tPoint[0] + fB * tPoint[1] + fC) / math.sqrt(fA**2 + fB**2)

    return fDistance

def getLineTheta(tLine):
    if tLine[0] == tLine[2]:
        return 90
    fSlope = (tLine[3] - tLine[1]) / (tLine[2] - tLine[0])
    if fSlope > 0:
        iTheta = math.atan(fSlope)
    else:
        iTheta = math.atan(fSlope) + math.pi
    return math.degrees(iTheta)


def roundThresholdJudger(iValue, iRound, iMiddleValue, iOffset):
    # 确保iValue在[0, iRound)范围内
    iValue = iValue % iRound
    
    # 计算范围的下界和上界
    iLowerThreshold = (iMiddleValue - iOffset) % iRound
    iUpperThreshold = (iMiddleValue + iOffset) % iRound
    
    # 如果不跨界
    if iLowerThreshold <= iUpperThreshold:
        return iLowerThreshold <= iValue <= iUpperThreshold
    # 如果跨界（例如，对于角度：350°到10°）
    else:
        return iValue >= iLowerThreshold or iValue <= iUpperThreshold

def parseLidarProcess(lRanges):
    rclpy.init(domain_id=99)
    oLidarParser = YDLidarParser(lRanges)
    rclpy.spin(oLidarParser)

def lidarPositioningProcesss(oQueue,oFrontDist,oRightDist,oBackDist,oLeftDist,oZeroDist,oLidarProcessGetDataStatus):
    iStep = 2
    iCompass = -1

    FrameCount = 0
    LastTime = time.time()
    
    while(1):
        lRanges = oQueue.get()
        lLines = []
        lPoints = []
        for tElement in lRanges:
            if 0 < tElement[1] < 2.5:
                fX = tElement[1] * math.sin(math.radians(tElement[0]))
                fY = tElement[1] * math.cos(math.radians(tElement[0]))
                lPoints.append((fX, fY, tElement[0]))
        
        if lPoints:
            for i in range(0,len(lPoints),iStep):
                if i + 1 < len(lPoints):
                    tLine = (lPoints[i][0], lPoints[i][1], lPoints[i+1][0], lPoints[i+1][1])
                    iTheta = getLineTheta(tLine)
                    fLidarAVGTheta = (lPoints[i][2] + lPoints[i+1][2]) / 2
                    fDistance = getLineDistance(tLine)
                    lLines.append((lPoints[i][0], lPoints[i][1], lPoints[i+1][0], lPoints[i+1][1], fDistance, iTheta, fLidarAVGTheta))

            FrameCount += 1
            CurrentTime = time.time()
            if CurrentTime - LastTime >= 1.0:
                print(f"FPS: {FrameCount}")
                FrameCount = 0
                LastTime = CurrentTime

            
            iCompass = oCompass.value
            iCompassFull = iCompass

            if iCompass == -1 or iCompass == 999:
                continue

            
            
            if iCompass > 180:
                iCompass = iCompass - 180

            lHorizontalLines = []
            lVerticalLines = []

            if lLines:
                oZeroDist.value = int(lLines[0][4] * 1000)
                for tLine in lLines:
                    if roundThresholdJudger(tLine[5], 180, iCompass, 20):
                        lHorizontalLines.append(tLine)
                    elif roundThresholdJudger(tLine[5], 180, iCompass + 90, 20):
                        lVerticalLines.append(tLine)
                    
                print(iCompass,len(lHorizontalLines),len(lVerticalLines))
                lDistances = [[],[],[],[]]
                lDistance = [0,0,0,0]
            
                if lHorizontalLines and lVerticalLines:
                    for tLine in lHorizontalLines:
                        if roundThresholdJudger(tLine[6], 360, -(iCompassFull), 90):
                            fDistance = round(tLine[4], 3)
                            lDistances[0].append(fDistance)
                        elif roundThresholdJudger(tLine[6], 360, -(iCompassFull + 180), 90):
                            fDistance = round(tLine[4], 3)
                            lDistances[2].append(fDistance)
                    for tLine in lVerticalLines:
                        if roundThresholdJudger(tLine[6], 360, -(iCompassFull + 90), 90):
                            fDistance = round(tLine[4], 3)
                            lDistances[1].append(fDistance)
                        elif roundThresholdJudger(tLine[6], 360, -(iCompassFull + 270), 90):
                            fDistance = round(tLine[4], 3)
                            lDistances[3].append(fDistance)
                            
                    for i in range(4):
                        # print(i)
                        # print(lDistances[i],len(lDistances[i]))
                        if len(lDistances[i]) > 5:
                            lDistances[i].sort()
                            iNum = int(len(lDistances[i])/100*85)
                            lDistance[i] = int(lDistances[i][iNum] * 1000)
                        else:
                            lDistance[i] = 0

                    oFrontDist.value = lDistance[0]
                    oRightDist.value = lDistance[1]
                    oBackDist.value = lDistance[2]
                    oLeftDist.value = lDistance[3]
#
                    print(lDistance[0],lDistance[1],lDistance[2],lDistance[3])
                    
                    oLidarProcessGetDataStatus.value = True
                    sData = 'som' + 'fd' + str(oFrontDist.value) + 'rd' + str(oRightDist.value) + 'bd' + str(oBackDist.value) + 'ld' + str(oLeftDist.value) + 'eom'
                    sendUART(oSerial,sData)
                    print('LidarSent')
                    oCompass.value = -1
                    
        


def readCompassProcess(oCompass):
    while(1):
        if oSerial.in_waiting:
            sData = oSerial.read(100).decode('utf-8')
            oBallProcessGetDataStatus.value = False
            oLidarProcessGetDataStatus.value = False
            print(sData)
            try:
                oCompass.value = int(sData[sData.index('cmp')+3:sData.index('end',sData.index('cmp'))])
                if oCompass.value == 999:
                    while oBallProcessGetDataStatus.value == False:
                        print('waitingballreply')
                        oSerial.reset_input_buffer()
                        time.sleep(0.01)
                    
                else:
                    while oLidarProcessGetDataStatus.value == False:
                        print('waitinglidarreply')
                        oSerial.reset_input_buffer()
                        time.sleep(0.01)
            except:
                print(2)
                continue
        else:
            oCompass.value = -1

def applyPerspectiveTransform(X, Y, Matrix):
    Point = np.array([X, Y, 1], dtype=np.float64)
    Transformed = Matrix @ Point
    Transformed /= Transformed[2]
    return int(Transformed[0]), int(Transformed[1])

def findBlobs(Frame, tThreshold, iFormat = 2, ROI = None, iMinPixelCount = 5):
    if iFormat == 1:
        Frame = cv2.cvtColor(Frame,cv2.COLOR_BGR2LAB)
    
    elif iFormat == 2:
        Frame = cv2.cvtColor(Frame,cv2.COLOR_BGR2HSV)

    lLowerThreshod = tThreshold[0], tThreshold[2], tThreshold[4]
    lUpperThreshold = tThreshold[1], tThreshold[3], tThreshold[5]
    
    
    
    Mask = cv2.inRange(Frame, np.array(lLowerThreshod), np.array(lUpperThreshold))
    
    # Kernel = np.ones((5, 5), np.uint8)
    # Mask = cv2.erode(Mask, Kernel, iterations=1)
    # Mask = cv2.dilate(Mask, Kernel, iterations=2)

    lConters, _ = cv2.findContours(Mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    lBlobs = []
    for oConter in lConters:
        iArea = cv2.contourArea(oConter)
        if iArea >= iMinPixelCount:
            iX, iY, iW, iH = cv2.boundingRect(oConter)
            iCX = int(iX + iW / 2) 
            iCY = int(iY + iH / 2)
            if ROI is not None and (iCX < ROI[0] or iCX > ROI[0] + ROI[2]) or (iCY < ROI[1] or iCY > ROI[1] + ROI[3]):
                continue
            lBlobs.append((iX, iY, iW, iH, iCX, iCY))
    return lBlobs

def camTest():
    lCams = camInit([0,2,4,6],320,240,3,0,32,64)
    time.sleep(2)
    lFrames = readCam(lCams)
    for oCam in lCams:
        oCam.release()

def imageResize(Frame, fScale=1, iXOffset=0, iYOffset=0):
    iOriginalHeight = Frame.shape[0]
    iOriginalWidth = Frame.shape[1]
    
    iResizedHeight = int(iOriginalHeight * fScale)
    iResizedWidth = int(iOriginalWidth * fScale)
    
    ResizedFrame = cv2.resize(Frame, (iResizedWidth, iResizedHeight))
    
    Canvas = np.zeros((iOriginalHeight, iOriginalWidth, 3), dtype=np.uint8)
    
    iResizedY = (iOriginalHeight - iResizedHeight) // 2
    iResizedX = (iOriginalWidth - iResizedWidth) // 2
    
    iStartY = max(0, iResizedY + iYOffset)
    iEndY = min(iOriginalHeight, iResizedY + iYOffset + iResizedHeight)
    
    iStartX = max(0, iResizedX + iXOffset)
    iEndX = min(iOriginalWidth, iResizedX + iXOffset + iResizedWidth)
    
    iFrameStartY = max(0, -iYOffset if iResizedY + iYOffset < 0 else 0)
    iFrameEndY = iResizedHeight - max(0, (iResizedY + iYOffset + iResizedHeight) - iOriginalHeight)
    
    iFrameStartX = max(0, -iXOffset if iResizedX + iXOffset < 0 else 0)
    iFrameEndX = iResizedWidth - max(0, (iResizedX + iXOffset + iResizedWidth) - iOriginalWidth)
    
    Canvas[iStartY:iEndY, iStartX:iEndX] = ResizedFrame[iFrameStartY:iFrameEndY, iFrameStartX:iFrameEndX]
    
    return Canvas

def imageCrop(Frame, lPoints, bBlackSide=False):
    Mask = np.zeros(Frame.shape[:2], dtype=np.uint8)
    aPoints = np.array(lPoints)
    cv2.fillPoly(Mask, [aPoints], (255))
    
    Result = cv2.bitwise_and(Frame, Frame, mask=Mask)
    
    if not bBlackSide:
        iX, iY, iW, iH = cv2.boundingRect(aPoints)
        Result = Result[iY:iY+iH, iX:iX+iW]
    
    return Result

def camInit(lCamPorts=lCamPorts, iWidth=320, iHeight=240, iAutoExposure=1, iBrightness=0, iContrast=32, iSaturation=64):
    lCams = []
    lAvailablePorts = []
    for iPort in lCamPorts:
        oCam = cv2.VideoCapture(iPort)
        if oCam.isOpened():
            oCam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            oCam.set(cv2.CAP_PROP_FRAME_WIDTH, iWidth)
            oCam.set(cv2.CAP_PROP_FRAME_HEIGHT, iHeight)
            oCam.set(cv2.CAP_PROP_AUTO_EXPOSURE, iAutoExposure)
            oCam.set(cv2.CAP_PROP_AUTO_WB,1)
            oCam.set(cv2.CAP_PROP_EXPOSURE,50)
            # oCam.set(cv2.CAP_PROP_WHITE_BALANCE_BLUE_U,4000)
            oCam.set(cv2.CAP_PROP_BRIGHTNESS, iBrightness)
            oCam.set(cv2.CAP_PROP_CONTRAST, iContrast)
            oCam.set(cv2.CAP_PROP_SATURATION, iSaturation)
            lCams.append(oCam)
            lAvailablePorts.append(iPort)
        else:
            print(f"Failed to open camera at port {iPort}")
    print(f"Available cameras at ports: {lAvailablePorts}")
    return lCams

def findMaxBlob(lBlobs):
    iMaxSize=0
    for oBlob in lBlobs:
        if oBlob[2]*oBlob[3] > iMaxSize:
            oMaxBlob=oBlob
            iMaxSize = oBlob[2] * oBlob[3]
    return oMaxBlob


def readCam(lCams, iCam = None, fScale = 1, iXOffset = 0, iYOffset = 0):
    lFrames = []
    if iCam == None:
        for oCam in lCams:
            Status,Frame = oCam.read()
            # Frame = imageResize(Frame,fScale,iXOffset,iYOffset)
            # print(Status)
            lFrames.append(Frame)
        return lFrames
    else:
        _,Frame = lCams[iCam].read()
        Frame = imageResize(Frame,fScale,iXOffset,iYOffset)
        return Frame

def findBlobProcess(lCam, iCam, tThreshold, ROI, iBX, iBY, iXOffset=0, iYOffset=0):
    global t0
    while(1):
        # print(1)
        Frame = readCam(lCams,iCam)
        Frame = imageResize(Frame,1,iXOffset=iXOffset,iYOffset=iYOffset)
        lBlobs = findBlobs(Frame,tThreshold=tThreshold,ROI = ROI)
        if lBlobs:
            oMaxBlob = findMaxBlob(lBlobs)
            cv2.circle(Frame, (oMaxBlob[4], oMaxBlob[1] + oMaxBlob[3]), 2, (0,255,0), 2)
            iX = oMaxBlob[4]
            iY = oMaxBlob[1] + oMaxBlob[3]
            
            iX,iY = applyPerspectiveTransform(iX,iY,lPerspectiveMatrix[iCam])
            iX = int(lPixelToCMK[iCam] * iX + lPixelToCMHorizontalB[iCam])
            iY = int(-lPixelToCMK[iCam] * iY + lPixelToCMVerticalB[iCam])

            iBX.value = iX
            iBY.value = iY
        else:
            iBX.value = 0
            iBY.value = 0
        time.sleep(0.005)
        # cv2.putText(Frame, f"FPS: {1.0/(time.time()-t0):.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2); t0 = time.time()
        # if True:
        #     cv2.imshow('Camera' + str(iCam), Frame)
        #     key = cv2.waitKey(1) & 0xFF
        #     if key == ord('q'):
        #         break

def integrateBallPos(oFrontBallX,oFrontBallY,oRightBallX,oRightBallY,oBackBallX,oBackBallY,oLeftBallX,oLeftBallY,oCompass,oBallProcessGetDataStatus):
    while(1):
        if oFrontBallY.value != 0:
            iX = oFrontBallX.value
            iY = oFrontBallY.value
        elif oRightBallY.value != 0:
            iY = -oRightBallX.value
            iX = oRightBallY.value
        elif oBackBallY.value != 0:
            iX = -oBackBallX.value
            iY = -oBackBallY.value
        elif oLeftBallY.value != 0:
            iY = oLeftBallX.value
            iX = -oLeftBallY.value
        else:
            iX = 0
            iY = 0

        if oCompass.value == 999:
            oBallProcessGetDataStatus.value = True
            sData = 'som' + 'bx' + str(iX) + 'by' + str(iY) + 'eom'
            sendUART(oSerial,sData)
            print('BallPosSent')
            oCompass.value = -1

        time.sleep(0.005)

oQueue = mp.Queue(maxsize=1)
oCompass = mp.Value('i',0)
oLidarProcessGetDataStatus = mp.Value('b',False)
oBallProcessGetDataStatus = mp.Value('b',False)
oFrontDist = mp.Value('i',0)
oRightDist = mp.Value('i',0)
oBackDist = mp.Value('i',0)
oLeftDist = mp.Value('i',0)
oZeroDist = mp.Value('i',0)

oFrontBallX = mp.Value('i',0)
oFrontBallY = mp.Value('i',0)
oRightBallX = mp.Value('i',0)
oRightBallY = mp.Value('i',0)
oBackBallX = mp.Value('i',0)
oBackBallY = mp.Value('i',0)
oLeftBallX = mp.Value('i',0)
oLeftBallY = mp.Value('i',0)
                    
print(GetUptime())

camTest()

lCams = camInit(iWidth=640, iHeight=480)
t0 = time.time()

oParseLidarProcess = mp.Process(target=parseLidarProcess, args=(oQueue,))
oParseLidarProcess.start()
oLidarPositioningProcess = mp.Process(target=lidarPositioningProcesss, args=(oQueue,oFrontDist,oRightDist,oBackDist,oLeftDist,oZeroDist,oLidarProcessGetDataStatus))
oLidarPositioningProcess.start()

oFrontFindBlobProcess = mp.Process(target = findBlobProcess,args=(lCams,0,tOrangeHSV,(80,0,480,480),oFrontBallX,oFrontBallY,0,0))
oFrontFindBlobProcess.start()
oRightFindBlobProcess = mp.Process(target = findBlobProcess,args=(lCams,1,tOrangeHSV,(80,0,480,480),oRightBallX,oRightBallY,0,0))
oRightFindBlobProcess.start()
oBackFindBlobProcess = mp.Process(target = findBlobProcess,args=(lCams,2,tOrangeHSV,(80,0,480,480),oBackBallX,oBackBallY,0,0))
oBackFindBlobProcess.start()
oRightFindBlobProcess = mp.Process(target = findBlobProcess,args=(lCams,3,tOrangeHSV,(80,0,480,480),oLeftBallX,oLeftBallY,0,0))
oRightFindBlobProcess.start()
oIntegrateBallPosProcess = mp.Process(target = integrateBallPos,args=(oFrontBallX,oFrontBallY,oRightBallX,oRightBallY,oBackBallX,oBackBallY,oLeftBallX,oLeftBallY,oCompass,oBallProcessGetDataStatus))
oIntegrateBallPosProcess.start()


oReadCompassProcess = mp.Process(target=readCompassProcess, args=(oCompass,))
oReadCompassProcess.start()

while(1):
    time.sleep(114514)
                    


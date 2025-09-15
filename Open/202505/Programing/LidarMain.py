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

oSerial = serial.Serial(
        port='/dev/serial0',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=0.01
    )



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

oQueue = mp.Queue(maxsize=1)
oCompass = mp.Value('i',0)
oFrontDist = mp.Value('i',0)
oRightDist = mp.Value('i',0)
oBackDist = mp.Value('i',0)
oLeftDist = mp.Value('i',0)

def parseLidarProcess(lRanges):
    rclpy.init()
    oLidarParser = YDLidarParser(lRanges)
    rclpy.spin(oLidarParser)

def lidarPositioningProcesss(oQueue,oFrontDist,oRightDist,oBackDist,oLeftDist):
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

            if iCompass == -1:
                continue
            
            if iCompass > 180:
                iCompass = iCompass - 180

            lHorizontalLines = []
            lVerticalLines = []

            if lLines:
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
                    sData = 'som' + 'fd' + str(oFrontDist.value) + 'rd' + str(oRightDist.value) + 'bd' + str(oBackDist.value) + 'ld' + str(oLeftDist.value) + 'eom'
                    sendUART(oSerial,sData)
        


def readCompassProcess(oCompass):
    while(1):
        if oSerial.in_waiting:
            sData = oSerial.read(100).decode('utf-8')
            print(sData)
            try:
                print(1)
                oCompass.value = int(sData[sData.index('cmp')+3:sData.index('end',sData.index('cmp'))])
            except:
                print(2)
                continue
            time.sleep(0.1)
            

        else:
            oCompass.value = -1
        



                    
if __name__ == "__main__":
	oParseLidarProcess = mp.Process(target=parseLidarProcess, args=(oQueue,))
	oParseLidarProcess.start()
	
	oLidarPositioningProcess = mp.Process(target=lidarPositioningProcesss, args=(oQueue,oFrontDist,oRightDist,oBackDist,oLeftDist))
	oLidarPositioningProcess.start()

	oReadCompassProcess = mp.Process(target=readCompassProcess, args=(oCompass,))
	oReadCompassProcess.start()

	while(1):
		time.sleep(114514)
                    


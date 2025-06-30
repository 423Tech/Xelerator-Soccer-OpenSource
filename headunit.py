import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
import threading
import math
import queue
import time

def GetLineStandardEquation(Line):

    x1, y1, x2, y2 = Line
    
    A = y2 - y1
    B = x1 - x2
    C = x2*y1 - x1*y2

    return A, B, C

def GetLineDistance(Line, Point=(0,0)):
    A, B, C = GetLineStandardEquation(Line)
    Distance = (A * Point[0] + B * Point[1] + C) / math.sqrt(A**2 + B**2)

    return Distance

def GetLineTheta(Line):
    if Line[0] == Line[2]:
        return 90
    
    Slope = (Line[3] - Line[1]) / (Line[2] - Line[0])

    if Slope > 0:
        Theta = math.atan(Slope)
    else:
        Theta = math.atan(Slope) + math.pi
    
    return math.degrees(Theta)

def RoundThresholdJudger(Value, Round, MiddleValue, Offset):
    Value = Value % Round
    
    LowerThreshold = (MiddleValue - Offset) % Round
    UpperThreshold = (MiddleValue + Offset) % Round
    
    if LowerThreshold <= UpperThreshold:
        return LowerThreshold <= Value <= UpperThreshold

    else:
        return Value >= LowerThreshold or Value <= UpperThreshold




class YDLidarParser(Node):
    def __init__(self,Queue):
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

        ScanTime = msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        AngleMin = msg.angle_min
        AngleMax = msg.angle_max
        AngleIncrement = msg.angle_increment
        RangeMin = msg.range_min
        RangeMax = msg.range_max
        Ranges = msg.ranges
        NumRanges = len(Ranges)
        for i in range(NumRanges):
            Angle = AngleMin + i * AngleIncrement
            lRanges.append((math.degrees(Angle)+180, Ranges[i]))

        Queue.put(lRanges)

class Lidar:
    def __init__(self,GetYaw):
        self.GetYaw = GetYaw

        self.DomainID = 99

        self.LidarDists = [0,0,0,0]
        self.Pos = [0,0,0]

        self.LidarQueue = queue.Queue()

        self.ParseLidarThread = threading.Thread(target=self.ParseLidar)
        self.ParseLidarThread.daemon = True
        self.ParseLidarThread.start()

    
    def ParseLidar(self):
        rclpy.init(domain_id=self.DomainID)
        LidarParser = YDLidarParser(self.LidarQueue)
        rclpy.spin(LidarParser)
    
    def LidarPositioning(self):
        Step = 2

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
    

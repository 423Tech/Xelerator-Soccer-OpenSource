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
    def __init__(self, Queue):
        self.Queue = Queue
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

        self.Queue.put(lRanges)

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

        self.LidarPositioningThread = threading.Thread(target=self.LidarPositioning)
        self.LidarPositioningThread.daemon = True
        self.LidarPositioningThread.start()

    
    def ParseLidar(self):
        rclpy.init(domain_id=self.DomainID)
        LidarParser = YDLidarParser(self.LidarQueue)
        rclpy.spin(LidarParser)
    
    def LidarPositioning(self):
        Step = 2

        FrameCount = 0
        LastTime = time.time()
        
        while(1):
            Ranges = self.LidarQueue.get()
            Lines = []
            Points = []
            for Element in Ranges:
                if 0 < Element[1] < 2.5:
                    X = Element[1] * math.sin(math.radians(Element[0]))
                    Y = Element[1] * math.cos(math.radians(Element[0]))
                    Points.append((X, Y, Element[0]))
            
            if Points:
                for i in range(0,len(Points),Step):
                    if i + 1 < len(Points):
                        Line = (Points[i][0], Points[i][1], Points[i+1][0], Points[i+1][1])
                        Theta = GetLineTheta(Line)
                        LidarAVGTheta = (Points[i][2] + Points[i+1][2]) / 2
                        Distance = GetLineDistance(Line)
                        Lines.append((Points[i][0], Points[i][1], Points[i+1][0], Points[i+1][1], Distance, Theta, LidarAVGTheta))

                FrameCount += 1
                CurrentTime = time.time()
                if CurrentTime - LastTime >= 1.0:
                    print(f"FPS: {FrameCount}")
                    FrameCount = 0
                    LastTime = CurrentTime

                Compass = self.GetYaw()
                CompassFull = Compass

                if Compass > 180:
                    Compass = Compass - 180

                HorizontalLines = []
                VerticalLines = []

                if Lines:
                    for Line in Lines:
                        if RoundThresholdJudger(Line[5], 180, Compass, 20):
                            HorizontalLines.append(Line)
                        elif RoundThresholdJudger(Line[5], 180, Compass + 90, 20):
                            VerticalLines.append(Line)
                        
                    print(Compass,len(HorizontalLines),len(VerticalLines))
                    Distances = [[],[],[],[]]
                    Distance = [0,0,0,0]
                
                    if HorizontalLines and VerticalLines:
                        for Line in HorizontalLines:
                            if RoundThresholdJudger(Line[6], 360, -(CompassFull), 90):
                                Distance = round(Line[4], 3)
                                Distances[0].append(Distance)
                            elif RoundThresholdJudger(Line[6], 360, -(CompassFull + 180), 90):
                                Distance = round(Line[4], 3)
                                Distances[2].append(Distance)
                        for Line in VerticalLines:
                            if RoundThresholdJudger(Line[6], 360, -(CompassFull + 90), 90):
                                Distance = round(Line[4], 3)
                                Distances[1].append(Distance)
                            elif RoundThresholdJudger(Line[6], 360, -(CompassFull + 270), 90):
                                Distance = round(Line[4], 3)
                                Distances[3].append(Distance)
                                
                        for i in range(4):
                            if len(Distances[i]) > 5:
                                Distances[i].sort()
                                iNum = int(len(Distances[i])/100*85)
                                Distance[i] = int(Distances[i][iNum] * 1000)
                            else:
                                Distance[i] = 0

                    print(Distance[0],Distance[1],Distance[2],Distance[3])
                        
    

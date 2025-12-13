#ROS2 libs
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
from rclpy.signals import SignalHandlerOptions

from ReasonData import Settings, logger, DATA_DIR
import time, math, serial, queue, threading

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



class ROSLidarParser(Node):
    def __init__(self, Queue):
        '''
        解析sllidar_ros2的雷达数据
        '''
        self.dirDistance = []
        self.Queue = Queue
        super().__init__('sllidar_node')

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
        
        
    def scanCallback(self, msg):
        self.dirDistance = []
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
            self.dirDistance.append(((math.degrees(Angle)+180) % 360, Ranges[i]))
        self.Queue.put(self.dirDistance)

class Lidar:
    def __init__(self,GetYaw=None):
        self.GetYaw = GetYaw
        self.domainID = Settings.Ports.LidarID

        self.dirNormalizedDistance = [0,0,0,0]

        self.dirLidarQueue = queue.Queue()

        self.ParseLidarThread = threading.Thread(target=self.ParseLidar)
        self.ParseLidarThread.daemon = True
        self.ParseLidarThread.start()

        self.LidarPositioningThread = threading.Thread(target=self.LidarNormalize)
        self.LidarPositioningThread.daemon = True
        self.LidarPositioningThread.start()

    def ParseLidar(self):
        rclpy.init(domain_id=self.domainID,signal_handler_options=SignalHandlerOptions(0))
        Parser = ROSLidarParser(self.dirLidarQueue)
        rclpy.spin(Parser)
    
    def LidarNormalize(self):
        step = 2
        frameCount = 0
        lastTime = time.time()
        
        try:
            while(1):
                Ranges = self.dirLidarQueue.get()
                lines = []
                points = []
                for Element in Ranges:
                    if 0 < Element[1] < 2.5:
                        X = Element[1] * math.sin(math.radians(Element[0]))
                        Y = Element[1] * math.cos(math.radians(Element[0]))
                        points.append((X, Y, Element[0]))
                
                if points:
                    for i in range(0,len(points),step):
                        if i + 1 < len(points):
                            Line = (points[i][0], points[i][1], points[i+1][0], points[i+1][1])
                            Theta = GetLineTheta(Line)
                            LidarAVGTheta = (points[i][2] + points[i+1][2]) / 2
                            Distance = GetLineDistance(Line)
                            lines.append((points[i][0], points[i][1], points[i+1][0], points[i+1][1], Distance, Theta, LidarAVGTheta))

                    frameCount += 1
                    CurrentTime = time.time()
                    if CurrentTime - lastTime >= 1.0:
                        if Settings.Debug.FullLog:
                            logger.debug(f"FPS: {frameCount}")
                        frameCount = 0
                        lastTime = CurrentTime

                    Compass = self.GetYaw()
                    CompassFull = Compass

                    if Compass > 180:
                        Compass = Compass - 180

                    HorizontalLines = []
                    VerticalLines = []

                    if lines:
                        for Line in lines:
                            if RoundThresholdJudger(Line[5], 180, Compass, 20):
                                HorizontalLines.append(Line)
                            elif RoundThresholdJudger(Line[5], 180, Compass + 90, 20):
                                VerticalLines.append(Line)
                            
                        # print(Compass,len(HorizontalLines),len(VerticalLines))
                        Distances = [[],[],[],[]]
                        LidarDists = [0,0,0,0]
                    
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
                                    import numpy
                                    LidarDists[i] = int(numpy.nan_to_num(Distances[i][iNum]) * 1000)
                                else:
                                    LidarDists[i] = 0

                        self.dirNormalizedDistance = LidarDists
        except Exception as e:
            self.LidarNormalize()

    def GetDists(self):
        return self.dirNormalizedDistance

class LidarWithoutYaw:
    def __init__(self,GetYaw):
        self.GetYaw = GetYaw
        self.domainID = Settings.Ports.LidarID

        self.dirNormalizedDistance = [0,0,0,0]

        self.dirLidarQueue = queue.Queue()

        self.ParseLidarThread = threading.Thread(target=self.ParseLidar)
        self.ParseLidarThread.daemon = True
        self.ParseLidarThread.start()

        self.LidarPositioningThread = threading.Thread(target=self.LidarPosition)
        self.LidarPositioningThread.daemon = True
        self.LidarPositioningThread.start()

    def ParseLidar(self):
        rclpy.init(domain_id=self.domainID,signal_handler_options=SignalHandlerOptions(0))
        Parser = ROSLidarParser(self.dirLidarQueue)
        rclpy.spin(Parser)
    
    def LidarPosition(self):
        Ranges = self.dirLidarQueue.get()
        # TODO

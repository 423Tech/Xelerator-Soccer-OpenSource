import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
from rclpy.signals import SignalHandlerOptions
import threading
import math
import queue
import time
import signal
import cv2
import numpy as np



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
        
        # self.get_logger().info('YDLidar X3解析器已启动，等待数据...')
        
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

#        print(lRanges)

        self.Queue.put(lRanges)

class Lidar:
    def __init__(self,GetYaw):
        self.GetYaw = GetYaw

        self.DomainID = 99

        self.LidarDists = [0,0,0,0]

        self.LidarQueue = queue.Queue()

        self.ParseLidarThread = threading.Thread(target=self.ParseLidar)
        self.ParseLidarThread.daemon = True
        self.ParseLidarThread.start()

        self.LidarPositioningThread = threading.Thread(target=self.LidarPositioning)
        self.LidarPositioningThread.daemon = True
        self.LidarPositioningThread.start()


    
    def ParseLidar(self):
        rclpy.init(domain_id=self.DomainID,signal_handler_options=SignalHandlerOptions(0))
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
                                LidarDists[i] = int(Distances[i][iNum] * 1000)
                            else:
                                LidarDists[i] = 0

                    self.LidarDists = LidarDists

    def GetDists(self):
        return self.LidarDists

class ArisCam:
    def __init__(self,GetYaw=None):
        self.GetYaw = GetYaw

        self.CamPorts = [0,2,4,6]

        self.Cams = []
        self.Frames = []

        self.PerspectiveMatrices = []
        self.P2CK = []
        self.P2CHB = []
        self.P2CVB = []

        self.InitCam(self.CamPorts)

        self.ReadCamsThread = threading.Thread(target=self.ReadCams)
        self.ReadCamsThread.daemon = True
        self.ReadCamsThread.start()

        for i in range(4):
            NumpyData = np.load('/root/CalibrationData' + str(self.CamPorts[i]) + '.npz')
            PerspectiveMatrix = NumpyData['matrix']
            self.PerspectiveMatrices.append(PerspectiveMatrix)
            P2CK = NumpyData['p2c'][0]
            self.P2CK.append(P2CK)
            P2CHB = NumpyData['p2c'][1]
            self.P2CHB.append(P2CHB)
            P2CVB = NumpyData['p2c'][2]
            self.P2CVB.append(P2CVB)

    def InitCam(self,CamPorts,Width=320, Height=240, AutoExposure=3, Exposure=130, Brightness=0, Contrast=32, Saturation=64):
        for Port in CamPorts:
            Cam = cv2.VideoCapture(Port,cv2.CAP_V4L2)
            Cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
            Cam.set(cv2.CAP_PROP_FRAME_WIDTH, Width)
            Cam.set(cv2.CAP_PROP_FRAME_HEIGHT, Height)
            Cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, AutoExposure)
            Cam.set(cv2.CAP_PROP_EXPOSURE, Exposure)
            Cam.set(cv2.CAP_PROP_BRIGHTNESS, Brightness)
            Cam.set(cv2.CAP_PROP_CONTRAST, Contrast)
            Cam.set(cv2.CAP_PROP_SATURATION, Saturation)
            self.Cams.append(Cam)
    
    def ReadCams(self):
        FrameCount = 0
        LastTime = time.time()
        while True:
            Frames = []
            for Cam in self.Cams:
                Frame = Cam.read()[1]
                Frames.append(Frame)
            self.Frames = Frames
            # print(1)
            FrameCount += 1
            CurrentTime = time.time()
            if CurrentTime - LastTime >= 1.0:
                # print(f"FPS: {FrameCount}")
                FrameCount = 0
                LastTime = CurrentTime
    
    def ApplyPerspectiveTransform(X, Y, Matrix):
        Point = np.array([X, Y, 1], dtype=np.float64)
        Transformed = Matrix @ Point
        Transformed /= Transformed[2]
        return int(Transformed[0]), int(Transformed[1])

    def Pixel2CM(self,X,Y,CamIndex):
        P2CK = self.P2CK[CamIndex]
        P2CHB = self.P2CHB[CamIndex]
        P2CVB = self.P2CVB[CamIndex]

        X, Y = self.ApplyPerspectiveTransform(X, Y, self.PerspectiveMatrices[CamIndex])

        X = int(self.P2CK[CamIndex][0] * X + self.P2CHB[CamIndex][0])
        Y = int(-self.P2CK[CamIndex][1] * Y + self.P2CVB[CamIndex][1])

        return X, Y
    
    def FindBlobs(Frame, Threshold, Format = 2, ROI = None, MinPixelCount = 5):
        if Format == 1:
            Frame = cv2.cvtColor(Frame,cv2.COLOR_BGR2LAB)

        elif Format == 2:
            Frame = cv2.cvtColor(Frame,cv2.COLOR_BGR2HSV)

        LowerThreshold = Threshold[0], Threshold[2], Threshold[4]
        UpperThreshold = Threshold[1], Threshold[3], Threshold[5]



        Mask = cv2.inRange(Frame, np.array(LowerThreshold), np.array(UpperThreshold))

        # Kernel = np.ones((5, 5), np.uint8)
        # Mask = cv2.erode(Mask, Kernel, iterations=1)
        # Mask = cv2.dilate(Mask, Kernel, iterations=2)

        Conters, _ = cv2.findContours(Mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        Blobs = []
        for Conter in Conters:
            Area = cv2.contourArea(Conter)
            if Area >= MinPixelCount:
                X, Y, W, H = cv2.boundingRect(Conter)
                CX = int(X + W / 2) 
                CY = int(Y + H / 2)
                if ROI is not None and (CX < ROI[0] or CX > ROI[0] + ROI[2]) or (CY < ROI[1] or CY > ROI[1] + ROI[3]):
                    continue
                Blobs.append((X, Y, W, H, CX, CY))
        return Blobs



    


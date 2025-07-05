#ROS2 libs
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
from rclpy.signals import SignalHandlerOptions
from hailo_platform import VDevice, HailoSchedulingAlgorithm

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

class ArisuIntelligence:
    def __init__(self,GetPos=None):
        self.GetPos = GetPos

        self.CamPorts = [0,2,4,6]

        self.Cams = []
        self.Frames = []
        self.Videos = []

        self.StopRecord = 0

        self.HailoParams = VDevice.create_params()
        self.HailoParams.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN

        self.PerspectiveMatrices = []
        self.P2CK = []
        self.P2CHB = []
        self.P2CVB = []

        self.OrangeThreshold = (5, 15, 128, 255, 150, 255)
        self.BallPos = [0,0]

        self.InitCam(self.CamPorts)

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

        self.ReadCamsThread = threading.Thread(target=self.ReadCams)
        self.ReadCamsThread.daemon = True
        self.ReadCamsThread.start()

        time.sleep(3)

        self.VideoRecordThread = threading.Thread(target=self.VideoRecord)
        self.VideoRecordThread.daemon = True
        self.VideoRecordThread.start()

        # self.FindBallThread = threading.Thread(target=self.FindBall)
        # self.FindBallThread.daemon = True
        # self.FindBallThread.start()

        self.YOLOProcessThread = threading.Thread(target=self.YOLOProcess)
        self.YOLOProcessThread.daemon = True
        self.YOLOProcessThread.start()


    def InitVideo(self):
        Videos = []
        for i in range(4):
            Time = int(time.time())
            Video = cv2.VideoWriter('./Records/' + str(i) + '/' + str(Time) + '.mp4', cv2.VideoWriter_fourcc(*'avc1'), 30, (640, 480))
            Videos.append(Video)
        self.Videos = Videos
    
    def CloseVideo(self):
        for Video in self.Videos:
            Video.release()
        self.Videos = []
    
    def VideoRecord(self):
        while True:
            if not self.Videos:
                self.InitVideo()
            elif int(time.time()) % 30 == 0:
                self.CloseVideo()
            
            for i in range(4):
                if self.Videos:
                    Frame = self.Frames[i]
                    if Frame is not None:
                        self.Videos[i].write(Frame)
            time.sleep(0.03)
    
    def YOLOProcess(self):
        with VDevice(self.HailoParams) as Hat:
            InferModel = Hat.create_infer_model('/xel/ArisuIntelligence.hef')
            InferModel.set_batch_size(4)
            with InferModel.configure() as ConfiguredInferModel:
                while True:
                    Bindings = ConfiguredInferModel.create_bindings()
                    Frames = []
                    
                    for i in range(4):
                        Frame = self.Frames[i]
                        if Frame is not None:
                            Frame = self.Resize(Frame, (640, 640))
                            Frame = cv2.cvtColor(Frame, cv2.COLOR_BGR2RGB)
                            Frames.append(Frame)
                    
                    InputBuffer = np.stack(Frames, axis=0)
                    InputBuffer = InputBuffer.transpose(0, 3, 1, 2)
                    InputBuffer = InputBuffer.astype(np.uint8)

                    Bindings.input().set_buffer(InputBuffer)

                    ConfiguredInferModel.run([Bindings])
                    
                    OutputBuffer = Bindings.output().get_buffer()
                    print(OutputBuffer.shape)
                



    def InitCam(self,CamPorts,Width=640, Height=480, AutoExposure=1, Exposure=157, Brightness=0, Contrast=32, Saturation=64):
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
    
    def ApplyPerspectiveTransform(self,X, Y, Matrix):
        Point = np.array([X, Y, 1], dtype=np.float64)
        Transformed = Matrix @ Point
        Transformed /= Transformed[2]
        return int(Transformed[0]), int(Transformed[1])

    def Pixel2CM(self,X,Y,CamIndex):
        P2CK = self.P2CK[CamIndex]
        P2CHB = self.P2CHB[CamIndex]
        P2CVB = self.P2CVB[CamIndex]

        X, Y = self.ApplyPerspectiveTransform(X, Y, self.PerspectiveMatrices[CamIndex])

        X = int(self.P2CK[CamIndex] * X + self.P2CHB[CamIndex])
        Y = int(-self.P2CK[CamIndex] * Y + self.P2CVB[CamIndex])

        return X, Y

    def Resize(Frame, TargetSize=(640, 640)):
        Height, Width = Frame.shape[:2]
        TargetHeight, TargetWidth = TargetSize
        
        Scale = min(TargetWidth/Width, TargetHeight/Height)
        
        NewWidth = int(Width * Scale)
        NewHeight = int(Height * Scale)
        
        ResizedImage = cv2.resize(Frame, (NewWidth, NewHeight))
        
        PaddedImage = np.zeros((TargetHeight, TargetWidth, 3), dtype=np.uint8)
        
        YOffset = (TargetHeight - NewHeight) // 2
        XOffset = (TargetWidth - NewWidth) // 2
        
        PaddedImage[YOffset:YOffset+NewHeight, XOffset:XOffset+NewWidth] = ResizedImage
        
        return PaddedImage
    
    def CM2Pixel(self, X, Y, CamIndex):
        P2CK = self.P2CK[CamIndex]
        P2CHB = self.P2CHB[CamIndex]
        P2CVB = self.P2CVB[CamIndex]

        X = (X - P2CHB) / P2CK
        Y = -(Y - P2CVB) / P2CK

        X, Y = self.ApplyPerspectiveTransform(X, Y, np.linalg.inv(self.PerspectiveMatrices[CamIndex]))

        return int(X), int(Y)

    def Resize(Frame, TargetSize=(640, 640)):
        Height, Width = Frame.shape[:2]
        TargetHeight, TargetWidth = TargetSize
        
        Scale = min(TargetWidth/Width, TargetHeight/Height)
        
        NewWidth = int(Width * Scale)
        NewHeight = int(Height * Scale)
        
        ResizedImage = cv2.resize(Frame, (NewWidth, NewHeight))
        
        PaddedImage = np.zeros((TargetHeight, TargetWidth, 3), dtype=np.uint8)
        
        YOffset = (TargetHeight - NewHeight) // 2
        XOffset = (TargetWidth - NewWidth) // 2
        
        PaddedImage[YOffset:YOffset+NewHeight, XOffset:XOffset+NewWidth] = ResizedImage
        
        return PaddedImage
    
    def FindMaxBlob(self, Blobs):
        MaxSize=0
        for Blob in Blobs:
            if Blob[2]*Blob[3] > MaxSize:
                MaxBlob=Blob
                MaxSize = Blob[2] * Blob[3]
        return MaxBlob

    def FindBlobs(self, Frame, Threshold, Format = 2, ROI = None, MinPixelCount = 5):
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
                if ROI is not None and ((CX < ROI[0] or CX > ROI[0] + ROI[2]) or (CY < ROI[1] or CY > ROI[1] + ROI[3])):
                    continue
                Blobs.append((X, Y, W, H, CX, CY))
        return Blobs
    
    def FindBall(self):
        while True:
            Balls = []
            for i in range(4):
                Blobs = []
                Frame = self.Frames[i]
                Blobs = self.FindBlobs(Frame, self.OrangeThreshold)
                # print(Blobs)
            
                if Blobs:
                    MaxBlob = self.FindMaxBlob(Blobs)
                    X = MaxBlob[4]
                    Y = MaxBlob[1] + MaxBlob[3]
                    X, Y = self.Pixel2CM(X, Y, i)
                    Balls.append((X, Y, i))
            
            if Balls:
                X = Balls[0][0]
                Y = Balls[0][1]
                CamIndex = Balls[0][2]
                if CamIndex == 0:
                    BX = X
                    BY = Y
                elif CamIndex == 1:
                    BY = -X
                    BX = Y
                elif CamIndex == 2:
                    BX = -X
                    BY = -Y
                elif CamIndex == 3:
                    BY = X
                    BX = -Y
            else:
                BX = 0
                BY = 0


            self.BallPos = [BX, BY]
            time.sleep(0.03)
    
    def GetBallPos(self):
        return self.BallPos
    
    def BinaryObjectDetection(self):
        Frame = self.Frames[0]
        Pos = [self.GetPos()[0], self.GetPos()[1]]
        Yaw = self.GetPos()[2]
        DistToCorner = int(math.sqrt((Pos[0] - 10) ** 2 + (Pos[1] - 13) ** 2))
        VisionAngle = math.degrees(math.atan2(Pos[0] - 10, Pos[1] - 13))
        Theta = VisionAngle - Yaw
        VisionCornerX = int(DistToCorner * math.sin(math.radians(Theta)))
        VisionCornerY = int(DistToCorner * math.cos(math.radians(Theta)))
        VisionCornerX, VisionCornerY = self.CM2Pixel(VisionCornerX, VisionCornerY, 0)
        print(VisionCornerX, VisionCornerY)






    




    


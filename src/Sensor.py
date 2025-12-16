#ROS2 libs
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
from rclpy.signals import SignalHandlerOptions

from ReasonData import Settings, logger
import time, math, queue, threading, os, signal, subprocess

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
    def start_sllidar_driver(self):
        """
        使用 subprocess.Popen 启动 sllidar_ros2 驱动
        """
        
        # 1. 设置 ROS 2 环境
        # 这一步至关重要，因为 'ros2' 命令只有在环境被 source 后才能找到。
        # 假设您的 ROS 2 安装在 /opt/ros/humble/setup.bash (请替换为您的版本)
        # 并且您的工作空间 (colcon workspace) 在 ~/ros2_ws/install/setup.bash
        
        # 确保您知道您的 ROS 2 环境路径
        # ros2_setup_path = '/opt/ros/humble/setup.bash' 
        workspace_setup_path = os.path.expanduser('~/.bashrc') # 假设路径
        
        # 构建要在 shell 中执行的完整命令
        command = [
            '/bin/bash', 
            '-c', 
            f'"source {workspace_setup_path} && export ROS_DOMAIN_ID=99 && ros2 launch sllidar_ros2 sllidar_s1_launch.py"'
        ]
        
        print(f"Starting ROS 2 launch command: {' '.join(command)}")

        # 2. 启动进程
        # shell=False (推荐): 安全地直接执行命令
        # preexec_fn=os.setsid: 启动一个独立于 Python 进程的新会话，方便后续统一关闭
        try:
            self.process = subprocess.Popen(
                command,
                preexec_fn=os.setsid,  # 创建新进程组，方便统一终止
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT
            )
            print(f"ROS 2 driver started with PID: {self.process.pid}")
            return self.process
        except FileNotFoundError:
            print("Error: /bin/bash not found. Check your system path.")
            return None
        except Exception as e:
            print(f"An error occurred while launching ROS 2 driver: {e}")
            return None

    def stop_process_group(self,process):
        """
        通过发送 SIGINT/SIGTERM 信号来终止整个进程组 (包括子进程)
        """
        if process is None or process.poll() is not None:
            print("Process is already stopped or was not started.")
            return
            
        try:
            # 终止整个进程组
            os.killpg(os.getpgid(process.pid), signal.SIGINT)
            print(f"Sent SIGINT to process group {os.getpgid(process.pid)}. Waiting for termination...")
            process.wait(timeout=5) # 等待进程优雅关闭
        except ProcessLookupError:
            print("Process or process group not found.")
        except subprocess.TimeoutExpired:
            print("Process did not terminate gracefully. Sending SIGKILL...")
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)
            
        print("ROS 2 driver process stopped.")


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

        # self.LidarPositioningThread = threading.Thread(target=self.start_sllidar_driver)
        # self.LidarPositioningThread.daemon = True
        # self.LidarPositioningThread.start()


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
    
    def GetFullData(self):
        return self.dirLidarQueue.get()
    
    # def __exit__(self):
    #     self.stop_process_group(self.lidar_service)

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


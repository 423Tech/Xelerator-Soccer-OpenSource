#ROS2 libs
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, QoSReliabilityPolicy, QoSHistoryPolicy, QoSDurabilityPolicy
from rclpy.signals import SignalHandlerOptions

from ReasonData import Settings, logger, LOG_FILE, Preference, DATA_DIR, ROS_ENV
from pathlib import Path
import time, math, queue, threading, os, signal, subprocess

# import open3d as o3d
# import numpy as np

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
    def start_sllidar_driver(self, enforce_settings: bool = True, bashrc: str = ROS_ENV):
        """
        使用 subprocess.Popen 启动 sllidar_ros2 驱动并将输出重定向到统一的项目 log 目录
        如果 enforce_settings=True，则强制使用 Settings 中的配置（LidarID、LidarType）
        返回 Popen 对象并更新 self.lidar_process / self.lidar_log_files / self.current_launch / self.current_domain
        """
        bashrc = os.path.expanduser(bashrc)

        # Read values from Settings (live) when enforcing
        if enforce_settings:
            try:
                domain = int(Preference().read('Ports', 'LidarID'))
            except Exception:
                domain = 99
            try:
                lidar_type = Preference().read('RoboInfo', 'LidarType')
            except Exception:
                lidar_type = getattr(Settings.RoboInfo, 'LidarType', 's2')
            if str(lidar_type).lower() == 's1':
                launch_file = 'sllidar_s1_launch.py'
            else:
                launch_file = 'sllidar_s2_launch.py'
        else:
            # fallback to current attributes
            domain = getattr(self, 'domainID', Settings.Ports.LidarID)
            launch_file = getattr(self, 'current_launch', 'sllidar_s2_launch.py')

        cmd = f'source {bashrc} && export ROS_DOMAIN_ID={domain} && exec ros2 launch sllidar_ros2 {launch_file}'

        # place logs into ReasonData data directory under logs/sllidar
        log_dir = Path(DATA_DIR) / 'logs' / 'sllidar'
        os.makedirs(str(log_dir), exist_ok=True)
        # filename: <launch_without_ext>_d<domain>.out/.err
        out_path = str(log_dir / f'{launch_file.replace(".py","")}_d{domain}.out')
        err_path = str(log_dir / f'{launch_file.replace(".py","")}_d{domain}.err')

        print(f"Starting ROS2 launch (domain={domain}, launch={launch_file}): {cmd}")

        try:
            out = open(out_path, 'ab')
            err = open(err_path, 'ab')
            p = subprocess.Popen(
                ['/bin/bash', '-lc', cmd],
                preexec_fn=os.setsid,
                stdout=out,
                stderr=err
            )
            print(f"ROS 2 driver started with PID: {p.pid}, stdout->{out_path}, stderr->{err_path}")
            self.lidar_log_files = (out, err)
            self.lidar_process = p
            self.current_launch = launch_file
            self.current_domain = domain
            return p
        except FileNotFoundError:
            print("Error: /bin/bash not found. Check your system path.")
            return None
        except Exception as e:
            print(f"An error occurred while launching ROS 2 driver: {e}")
            raise e

    def stop_process_group(self, process):
        """
        通过发送 SIGINT/SIGTERM 信号来终止整个进程组 (包括子进程)
        """
        if process is None or process.poll() is not None:
            print("Process is already stopped or was not started.")
            return

        try:
            os.killpg(os.getpgid(process.pid), signal.SIGINT)
            print(f"Sent SIGINT to process group {os.getpgid(process.pid)}. Waiting for termination...")
            process.wait(timeout=5)
        except ProcessLookupError:
            print("Process or process group not found.")
        except subprocess.TimeoutExpired:
            print("Process did not terminate gracefully. Sending SIGKILL...")
            os.killpg(os.getpgid(process.pid), signal.SIGKILL)

        print("ROS 2 driver process stopped.")

    def stop(self):
        """Stop the sllidar driver and close log files"""
        if hasattr(self, 'lidar_process') and self.lidar_process is not None:
            self.stop_process_group(self.lidar_process)
            self.lidar_process = None
        if hasattr(self, 'lidar_log_files'):
            try:
                for f in self.lidar_log_files:
                    try:
                        f.flush()
                        f.close()
                    except Exception:
                        pass
            except Exception:
                pass

    def __del__(self):
        # 尽量在对象销毁时清理外部进程
        self.stop()


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

        # 自动启动 sllidar 驱动（强制基于 Settings）
        try:
            self.lidar_process = None
            self.lidar_log_files = None
            # initialize current settings values
            try:
                self.domainID = int(Preference().read('Ports', 'LidarID'))
            except Exception:
                self.domainID = int(Settings.Ports.LidarID)
            self.current_launch = None
            self.current_domain = None

            p = self.start_sllidar_driver(enforce_settings=True)
            if p is None:
                logger.error("Warning: failed to start sllidar driver")

            # start settings watcher thread to update on config changes
            self._watcher_thread = threading.Thread(target=self._settings_watcher)
            self._watcher_thread.daemon = True
            self._watcher_thread.start()
        except Exception as e:
            raise(f"Exception while starting sllidar driver: {e}")



    def ParseLidar(self):
        try:
            logger.info(f"Initializing ROS parser with domain_id={self.domainID}")
            rclpy.init(domain_id=self.domainID, signal_handler_options=SignalHandlerOptions(0))
            Parser = ROSLidarParser(self.dirLidarQueue)
            rclpy.spin(Parser)
        except Exception as e:
            logger.error(f"ParseLidar exception: {e}")
    
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

    def _settings_watcher(self):
        """Background thread: watch config (via Preference) and restart lidar driver / parser if LidarID or LidarType changes."""
        while True:
            # read fresh Preference each loop so that external changes are seen
            try:
                desired_domain = int(Preference().read('Ports', 'LidarID'))
            except Exception:
                desired_domain = self.domainID
            try:
                desired_type = Preference().read('RoboInfo', 'LidarType')
                desired_launch = 'sllidar_s1_launch.py' if str(desired_type).lower() == 's1' else 'sllidar_s2_launch.py'
            except Exception:
                desired_launch = self.current_launch

            if (self.current_domain != desired_domain) or (self.current_launch != desired_launch):
                logger.info(f"Lidar settings changed: domain {self.current_domain}->{desired_domain}, launch {self.current_launch}->{desired_launch}")
                # restart lidar driver to apply new settings
                try:
                    self.stop()
                except Exception:
                    pass
                try:
                    p = self.start_sllidar_driver(enforce_settings=True)
                    if p is None:
                        logger.warning("Failed to restart sllidar driver after settings change")
                except Exception as e:
                    logger.error(f"Error restarting sllidar driver: {e}")

                # if domain changed, restart ROS parser as well
                if self.domainID != desired_domain:
                    try:
                        rclpy.shutdown()
                    except Exception:
                        pass
                    self.domainID = desired_domain
                    try:
                        self.ParseLidarThread = threading.Thread(target=self.ParseLidar)
                        self.ParseLidarThread.daemon = True
                        self.ParseLidarThread.start()
                    except Exception as e:
                        logger.error(f"Failed to restart ParseLidarThread: {e}")

            time.sleep(5)
    
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


# class NexusPosition:
#     def __init__(self):
#         pass

#     def create_rectangular_map(length=Settings.Bounds.Long, width=Settings.Bounds.Short, resolution=0.02):
#         """
#         创建一个长方形场地的地图点云（仅四条边）
#         :param length: 场地长度（X方向）
#         :param width:  场地宽度（Y方向）
#         :param resolution: 点间距（米）
#         :return: Open3D PointCloud
#         """
#         points = []

#         # 底边 y=0
#         x_bottom = np.arange(0, length + resolution, resolution)
#         points.extend([(x, 0.0, 0.0) for x in x_bottom])

#         # 顶边 y=width
#         x_top = np.arange(0, length + resolution, resolution)
#         points.extend([(x, width, 0.0) for x in x_top])

#         # 左边 x=0
#         y_left = np.arange(0, width + resolution, resolution)
#         points.extend([(0.0, y, 0.0) for y in y_left])

#         # 右边 x=length
#         y_right = np.arange(0, width + resolution, resolution)
#         points.extend([(length, y, 0.0) for y in y_right])

#         map_pcd = o3d.geometry.PointCloud()
#         map_pcd.points = o3d.utility.Vector3dVector(np.array(points))
#         return map_pcd
#     def polar_to_open3d_pointcloud(polar_data, max_dist=5.0):
#         """
#         将 [(angle_deg, distance), ...] 转换为 Open3D 点云
#         :param polar_data: list of (angle, distance)
#         :param max_dist: 过滤掉太远的点（如 >5m）
#         :return: Open3D PointCloud
#         """
#         points = []
#         for angle_deg, dist in polar_data:
#             if dist < 0.1 or dist > max_dist:  # 过滤无效点
#                 continue
#             angle_rad = np.radians(angle_deg)
#             x = dist * np.cos(angle_rad)
#             y = dist * np.sin(angle_rad)
#             points.append([x, y, 0.0])  # z=0

#         pcd = o3d.geometry.PointCloud()
#         pcd.points = o3d.utility.Vector3dVector(np.array(points))
#         return pcd

#     def localize_with_icp(scan_pcd, map_pcd, initial_guess=np.eye(4)):
#         """
#         使用 ICP 将 scan 对齐到 map
#         :param scan_pcd: 当前扫描点云
#         :param map_pcd: 全局地图点云
#         :param initial_guess: 初始位姿猜测（4x4 变换矩阵）
#         :return: 最终变换矩阵 T (4x4)
#         """
#         # 可选：下采样加速
#         scan_down = scan_pcd.voxel_down_sample(voxel_size=0.02)
#         map_down = map_pcd.voxel_down_sample(voxel_size=0.02)

#         # 设置 ICP 参数
#         threshold = 0.1  # 匹配距离阈值（米）
#         reg = o3d.pipelines.registration.registration_icp(
#             source=scan_down,
#             target=map_down,
#             max_correspondence_distance=threshold,
#             init=initial_guess,
#             estimation_method=o3d.pipelines.registration.TransformationEstimationPointToPoint(),
#             criteria=o3d.pipelines.registration.ICPConvergenceCriteria(max_iteration=50)
#         )
#         return reg.transformation

#     def extract_pose_from_transform(self,T):
#         """
#         从 4x4 变换矩阵中提取 x, y, yaw
#         :param T: 4x4 SE(3) 变换矩阵
#         :return: (x, y, yaw_radians)
#         """
#         x = T[0, 3]
#         y = T[1, 3]
        
#         # 从旋转矩阵提取 yaw（绕 Z 轴）
#         yaw = np.arctan2(T[1, 0], T[0, 0])
        
#         # 归一化到 [0, 2π)
#         if yaw < 0:
#             yaw += 2 * np.pi
            
#         return x, y, yaw

#     def N_AbsRoboPosition(self):
#         '''
#         Get the [Absolute] Position of the Robot using Lidar Full Data
#         获取[机器人几何中心]相对于[场地几何中心]的位置 [x_forward,y_left,yaw]
#         #### Args:
#             None

#         #### Returns:
#             RobotPosition: [x, y, yaw] | absolute position and heading
#         #### Note:
#             `0xfff` stand for `No Position`
#             Uses lidar.GetFullData() to detect field boundaries
#         '''
#         import numpy as np
#         # 1. 创建地图
#         map_pcd = self.create_rectangular_map(length=3.0, width=2.0)

#         # 2. 模拟一次激光扫描（假设机器人在 (1.0, 1.0)，朝向 45°）
#         true_x, true_y, true_yaw = 1.0, 1.0, np.radians(45)
#         angles = np.linspace(-135, 135, 360)  # RPLIDAR 视野
#         distances = []

#         for ang in angles:
#             rad = np.radians(ang)
#             # 射线与四条墙求交，取最近交点（简化版）
#             d1 = (0 - true_x) / np.cos(rad) if np.cos(rad) != 0 else np.inf
#             d2 = (3.0 - true_x) / np.cos(rad) if np.cos(rad) != 0 else np.inf
#             d3 = (0 - true_y) / np.sin(rad) if np.sin(rad) != 0 else np.inf
#             d4 = (2.0 - true_y) / np.sin(rad) if np.sin(rad) != 0 else np.inf
            
#             candidates = []
#             for d in [d1, d2, d3, d4]:
#                 if d > 0:
#                     x_hit = true_x + d * np.cos(rad)
#                     y_hit = true_y + d * np.sin(rad)
#                     if 0 <= x_hit <= 3.0 and 0 <= y_hit <= 2.0:
#                         candidates.append(d)
            
#             dist = min(candidates) if candidates else 5.0
#             distances.append(dist)

#         polar_data = list(zip(angles, distances))
#         scan_pcd = self.polar_to_open3d_pointcloud(polar_data)

#         # 3. 执行 ICP（使用上一帧作为初值，这里用 identity）
#         T = self.localize_with_icp(scan_pcd, map_pcd, initial_guess=np.eye(4))

#         # 4. 提取位姿
#         x, y, yaw = self.extract_pose_from_transform(T)
#         print(f"Estimated: x={x:.2f}, y={y:.2f}, yaw={np.degrees(yaw):.1f}°")
#         print(f"True:      x={true_x}, y={true_y}, yaw={np.degrees(true_yaw):.1f}°")


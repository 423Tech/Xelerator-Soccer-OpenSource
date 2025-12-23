import math, time, threading

# import numpy as np
# import open3d as o3d

from ReasonData import logger, Settings
cfg = Settings

from headunit import ArisuIntelligence
vision = ArisuIntelligence()

# from Vision import UnitedVision
# vision = UnitedVision()

from Sensor import Lidar
from chassis import Car,Peripherals # Universal-Movement-Standard
if cfg.RoboInfo.Bit == "AB":
    from utils.ArisuBits import ArisBit
    Bits = ArisBit()
    lidar = Lidar(Bits.GetYaw)
    chassis = Car(Bits.SetMotor,Bits.GetYaw,Bits.get_motor_encoder)
    compass = Bits.GetYaw
    peripheral = Peripherals(Bits.SetIO)
    Odometer = None
    logger.info("Arisu Bit loaded.")
elif cfg.RoboInfo.Bit == "IL":
    from utils.IceLoongBits import IceLoongBits
    Bits = IceLoongBits()
    lidar = Lidar(Bits.GetYaw)
    peripheral = Peripherals(Bits.SetIO) #TODO
    chassis = Car(Bits.SetRpmFour,Bits.GetYaw)
    compass = Bits.GetYaw
    Odometer = Bits.Odometer #TODO add odometer support
    logger.info("IceLoongBits Bit loaded.")
# elif cfg.RoboInfo.Bit == "3Q":
#     logger.info("3Q Bit loaded.")
#     # peripheral = Peripherals(Bits.SetIO) #TODO
#     logger.info("RoboMaster Bit loaded.")
else:
    logger.error("None Bit Model Fetched.")
    raise ImportError("None Bits Model Set.")

class Positions:
    def __init__(self):
        # Values for Setup Position System
        self.LidarPos = [0xfff,0xfff,0xfff]
        self.ballPos = [0xfff,0xfff]
        self.BallDistance = 0xfff
        # Values for log system
        self.WarnedLidarCount = 0
        # Values for Adjust the scale of Position System
        self.LidarScale = 10
        self.BoundsScale = 1
        # Values for timer
        self.WaitTime = 1
        # Values for configs
        self.FullLog = cfg.Debug.FullLog

    class Calculate:
        def Local2Angle(lAimPos:list[int,int]) -> int:
            '''
            lAimPos 一个坐标 示例：[0,0]
            '''
            iAimX = lAimPos[0]
            iAimY = lAimPos[1]
            iLocX,iLocY = Positions.AbsRoboPosition()[0]
            iDeltaX = iAimX - iLocX
            iDeltaY = iAimY - iLocY
            try:
                iDeltaAngle = -math.degrees(math.atan(iDeltaX/iDeltaY))
            except:
                if iDeltaX > 0:
                    iDeltaAngle = -90
                else:
                    iDeltaAngle = 90
            return int(iDeltaAngle)
        
        def Pos2Angle(lInputPos:list[int,int],lAimPos:list[int,int]) -> int:
            '''
            lInputPos 输入坐标
            lAimPos 目标坐标 示例：[0,0]
            '''
            iAimX = lAimPos[0]
            iAimY = lAimPos[1]
            iLocX = lInputPos[0]
            iLocY = lInputPos[1]
            iDeltaX = iAimX - iLocX
            iDeltaY = iAimY - iLocY
            iDeltaAngle = math.degrees(math.atan2(iDeltaY,iDeltaX))
            return int(iDeltaAngle)

    # ********* BASIC FUNCTIONS ********
    def Relative_Ball_Position(self):
        '''
        Get the [Relative] Position of the ball
        获取[球]相对于[机器几何中心]的位置
        #### Args:
        
        #### Returns:
            BallPos: [0,0]
        #### Note:
            `0xfff` stand for `NoBallFounded`
            `0xddd` stand for `CatchBall`
        '''
        # 20251017 already changed X,Y dimension    
        self.ballPos = vision.GetBallPos()
        if self.ballPos == [0,0]:
            self.ballPosOut = [0xfff,0xfff]
        elif abs(self.ballPos[1]-cfg.ExpectedVals.CatchVal[1]) <= cfg.ExpectedVals.ErrorRange/4 and abs(self.ballPos[0]-cfg.ExpectedVals.CatchVal[0]) <= cfg.ExpectedVals.ErrorRange/4:
            self.ballPosOut = [0xddd,0xddd]
        else:
            self.ballPosOut = self.ballPos
        logger.debug("[Relative] Ball Position: %s"%self.ballPos)
        logger.info("[Relative] Ball Position Output: %s"%self.ballPosOut)
        return self.ballPosOut

    def direct_distance(self):
        '''
        Get the [Direct] Distance From the bound to the Bound
        获取四面墙的距离 
        TODO 维修四边分离
        #### Args:

        #### Returns:
            RobotPosition: [0,0]
        #### Note:
            `0xfff` stand for `NoPosition`
        '''
        self.BoundsDistance = lidar.GetDists()
        logger.debug("Lidar Raw Data: %s"%self.BoundsDistance)
        if self.BoundsDistance == [0, 0, 0, 0]:
            self.WarnedLidarCount +=1
            time.sleep(self.WaitTime) # wait 1 second for starting lidar
            logger.warning("Lidar Not Started! Retry for %s time in %s second"%(self.WarnedLidarCount,self.WaitTime))
            if self.WarnedLidarCount >= cfg.ExpectedVals.MaxWarnCount:
                logger.error("No Lidar Data Recieved! Please Check Lidar Modules!")
                raise RuntimeError("No Lidar Data Recieved! Please Check Lidar Modules!")
            return [0xfff,0xfff,0xfff,0xfff]
        else:
            if self.WarnedLidarCount:
                self.WarnedLidarCount = 0
            else:
                pass
            logger.success("Lidar System Started!Read [Direct] Robot Distance: %s"%self.BoundsDistance)
        logger.info("Read [Direct] Robot Distance: %s"%self.BoundsDistance)
        return self.BoundsDistance

    def AbsRoboPosition(self,lower:bool|None = False):
        '''
        Get the [Absolute] Position of the Robot
        获取[机器人几何中心]相对于[场地几何中心]的位置 [x_forward,y_left,yaw]
        #### Args:
            lower: `bool`, choose to using lower data

        #### Returns:
            RobotPosition: [0,0]
        #### Note:
            `0xfff` stand for `No Position`
        '''
        if not lower:# if use lidar datas
            _distance = self.direct_distance()
            if (_distance[0]+_distance[2]) < (cfg.Bounds.Long)*self.LidarScale*self.BoundsScale:
                if _distance[0] > _distance[2]:
                    Y = cfg.Bounds.Long*self.LidarScale/2 - _distance[0]
                else:
                    Y = _distance[2] - cfg.Bounds.Long*self.LidarScale/2
            else:
                Y = ((cfg.Bounds.Long*self.LidarScale/2 - _distance[0]) + (_distance[2] - cfg.Bounds.Long*self.LidarScale/2))/2
            if _distance[1]+_distance[3] < (cfg.Bounds.Short - 50)*self.LidarScale*self.BoundsScale:
                if _distance[1] > _distance[3]:
                    X = -(cfg.Bounds.Short*self.LidarScale/2 - _distance[1])
                else:
                    X = -(_distance[3] - cfg.Bounds.Short*self.LidarScale/2)
            else:
                X = -((cfg.Bounds.Short*self.LidarScale/2 - _distance[1]) + (_distance[3] - cfg.Bounds.Short*self.LidarScale/2))/2
            self.LidarPos = [Y/10,X/10,compass()]
            logger.info("[Absolute] Robot Position: %s"%self.LidarPos)
            # 20251216 already changed X_forward,Y_left dimension  [tested]
            return [Y/10,X/10,compass()]
        elif Bits.Odometer is not None:# if use odometer datas
            # TODO finish lower Positions
            pass

    # class NexusPosition:
    #     def __init__(self):
    #         pass

    #     def create_rectangular_map(length=cfg.Bounds.Long, width=cfg.Bounds.Short, resolution=0.02):
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



    def AbsChassisPos(self):
        '''
        获取[对方机器人]相对于[场地几何中心]的位置 [[x_forward,y_left],[x_forward,y_left],[x_forward,y_left]]
        ##### retrun a list of the absloute position of all chassis
        #### Returns:
            OutputDistanceList: [c1,c2]
                c1: 
                    chassis X Position
                    chassis Y Position
                    chassis height
                    chassis weidth
        '''
        # 20251017 already changed X,Y dimension
        ChassisRawList = vision.GetChassisPos()
        SelfX,SelfY,SelfZ = self.AbsRoboPosition()
        OutputDistanceList = []
        for c in ChassisRawList:
            cDistance = math.sqrt(c[0]**2 + c[1]**2)
            if c[1] == 0:
                ChassisRltAngle = 0
            try:
                ChassisRltAngle =  -int(math.degrees(math.atan2(c[0],c[1])) - 90)
            except ZeroDivisionError:
                ChassisRltAngle =  0
            ChassisAngleAngle = ChassisRltAngle + SelfZ
            if ChassisAngleAngle > 360:
                ChassisAbsAngle = ChassisAngleAngle - 360
            else:
                ChassisAbsAngle = ChassisAngleAngle
            AbsChassisCache = [
                cDistance * math.sin(math.radians(ChassisAbsAngle)) + SelfY,
                cDistance * math.cos(math.radians(ChassisAbsAngle)) + SelfX,
                c[2],
                c[3]
                ]
            OutputDistanceList.append(AbsChassisCache)
        return OutputDistanceList

    # ********* UPPER FUNCTIONS ********
    def RelBallAngle(self):
        '''
        获取[球]相对于[机器几何中心]的角度
        retrun a relative angle of the ball
        ### Returns:
            ballangle: int | relative ball angle
        '''
        ballX,ballY = vision.GetBallPos()
        if ballY == 0:
            relBallAngle = 0
        try:
            if -int(math.degrees(math.atan2(ballY,ballX)) - 90) < 0:
                relBallAngle = -int(math.degrees(math.atan2(ballY,ballX)) - 90) + 360
            else:
                relBallAngle = -int(math.degrees(math.atan2(ballY,ballX)) - 90)
        except ZeroDivisionError:
            relBallAngle = 0
        return relBallAngle
    
    def AbsBallAngle(self):
        '''
        retrun a absolute angle of the ball
        #### Returns:
            BallAngle: int | absolute ball angle
        '''
        self.BallAngle = (self.RelBallAngle() + compass())%360
        return self.BallAngle

    def AbsBallDistance(self):
        '''
        获取[球]相对于[机器几何中心]的距离
        Get the [Absolute] Distance from Robot to Ball
        #### Returns:
            BallDistance: int | absolute Distance from Robot to Ball

        #### Note:
            `0xfff` stand for `NoBall`
            `0xddd` stand for `CatchBall`
        '''
        BallX, BallY = self.Relative_Ball_Position()
        x, y, _ = self.AbsRoboPosition()
        if [BallX, BallY] == [0xfff,0xfff]:
            self.BallDistance = 0xfff
        elif [BallX, BallY] == [0xddd,0xddd]:
            self.BallDistance = 0xddd
        else:
            self.BallDistance = math.sqrt((BallX - x) ** 2 + (BallY - y) ** 2)
        if self.FullLog:
            logger.debug("[Absolute] Ball Distance: %s"%self.LidarPos)
        return self.BallDistance

    def AbsBallPos(self):
        '''
        获取[球]相对于[场地几何中心]的距离
        Get the [Absolute] Position for the Ball in the Field
        #### Returns:
            BallPos: list | [0,0]

        #### Note:
            `0xfff` stand for `NoBall`
            `0xddd` stand for `CatchBall`
        '''
        ballX,ballY = vision.GetBallPos()
        if [ballX,ballY] == [0,0]:
            return [0xfff,0xfff]
        if [ballX,ballY] == cfg.ExpectedVals.CatchVal:
            return [0xddd,0xddd]
        else:
            SelfX,SelfY,SelfZ = self.AbsRoboPosition()
            ballDistance = math.sqrt(ballX**2 + ballY**2)
            if ballY == 0:
                ballRltAngle = 0
            try:
                ballRltAngle =  -int(math.degrees(math.atan2(ballY,ballX)) - 90)
            except ZeroDivisionError:
                ballRltAngle =  0
            ballAbsAngle = (ballRltAngle + SelfZ)%360
            if ballAbsAngle > 180:
                k = -1
            else:
                k = 1
            AbsBallPositon = [
                ballDistance * math.cos(math.radians(ballAbsAngle)) + SelfX,
                ballDistance * math.sin(math.radians(ballAbsAngle)) + SelfY
                ]
            # 20251017 already changed X,Y dimension
            return AbsBallPositon

    def RelChassisAngle(self):
        '''
        获取[球]相对于[机器人几何中心]的角度列表
        ##### retrun a list of the relative angle from the robot to the chassis
        #### Returns:
            [a1,a2,a3,etc]
        '''
        ChassisRawList = vision.GetChassisPos()
        ChassisAngleList = []
        for c in ChassisRawList:
            if c[1] == 0:
                return 0
            try:
                if -int(math.degrees(math.atan2(c[1],c[0])) - 90) < 0:
                    ChassisRltAngle = -int(math.degrees(math.atan2(c[1],c[0])) - 90) + 360
                else:
                    ChassisRltAngle = -int(math.degrees(math.atan2(c[1],c[0])) - 90)
                ChassisAngleList.append(ChassisRltAngle)
            except ZeroDivisionError:
                ChassisAngleList.append(0)
        return ChassisAngleList

    def AbsChassisAngle(self):
        '''
        获取[球]相对于[场地几何中心]的角度列表
        ##### retrun a list of the absolute angles of the chassis
        #### Returns:
            [a1,a2,a3,etc]
        '''
        OutputAngles = []
        CompassCache = compass()
        for i in self.RelChassisAngle():
            ChassisAngleCache = i + CompassCache
            if ChassisAngleCache > 360:
                OutputAngles.append(int(ChassisAngleCache)%360)
            else:
                OutputAngles.append(int(ChassisAngleCache))
        return OutputAngles


    def MoveToPosition(self, Position: list[int, int, int], Kp: float | None = None):
        selfPosition = self.AbsRoboPosition()
        dX = Position[0] - selfPosition[0]
        dY = Position[1] - selfPosition[1]
        dW = Position[2] - selfPosition[2]

        if abs(dX) < 5 and abs(dY) < 5 and abs(dW) < 5:
            chassis.stop()
            return [0, 0, 0]  # 已经到达目标位置
        else:
            chassis.AbsMoveVetor(dX, dY, dW)

    def Pos2Pos(self,AimPos:list, Speed:int | None = None) -> int:
        '''
        iFacingAngle 移动时面对的方向 0~360
        lAimPos 目标坐标位置 如[0,0] 距离越近速度越小
        # TODO 调整PID
        '''
        iLocX,iLocY,iLocZ = self.AbsRoboPosition()
        if iLocX < 0:
            kX = -1
        else:
            kX = 1
        if iLocY < 0:
            kY = -1
        else:
            kY = 1
        iAimX,iAimY,iAimZ = AimPos
        iDeltaX = (iAimX) - (iLocX)
        iDeltaY = (iAimY) - (iLocY)
        RestrictedX = Settings.Bounds.FarPos[0]
        RestrictedY = Settings.Bounds.FarPos[1]
        try:
            try:
                Slope = iDeltaX/iDeltaY
            except ZeroDivisionError:
                Slope = 1
            if Slope*RestrictedY > RestrictedX:
                iAimX = (RestrictedX - 3)*kX
            if Slope/RestrictedX > RestrictedY:
                iAimY = (RestrictedY - 3)*kY
        except:
            iAimX,iAimY,iAimZ = AimPos
        if iLocZ > 180:
            iDeltaZ = 360 - abs(iAimZ) - abs(iLocZ)
        else:
            iDeltaZ = (abs(iAimZ) - abs(iLocZ))
        iErrorRange = Settings.ExpectedVals.ErrorRange
        iMovedAngle = int(math.degrees(math.atan2(iDeltaY,iDeltaX)))
        if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY) and abs(iErrorRange) > iDeltaZ:
            chassis.stop()
            return True
        elif iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY) and not abs(iErrorRange) > abs(iDeltaZ):
            chassis.RelTurn(iDeltaZ)
        else:
            if Speed:
                chassis.AbsMoveAngle(AimPos[2],90-iMovedAngle,Speed)
            else:
                # chassis.AbsMoveAngle(AimPos[2],90-iMovedAngle,int((abs(iDeltaX)+abs(iDeltaY))*2.5)+5)
                chassis.AbsMoveVetor(iDeltaX,iDeltaY,AimPos[2])
            return False

    def Move2Path(self,Posistions:list[list[int,int,int],list[int,int,int]],iWaitMs:int,A2O:bool | None = False):
        iErrorRange = Settings.ExpectedVals.ErrorRange
        for i in Posistions:
            while (1):
                iAimX = i[0]
                iAimY = i[1]
                iAimZ = i[2]
                lLocal = self.AbsRoboPosition()
                iLocX = lLocal[0]
                iLocY = lLocal[1]
                iLocZ = lLocal[2]
                iDeltaX = iAimX - iLocX
                iDeltaY = iAimY - iLocY
                iDeltaZ = iAimZ - iLocZ
                if iErrorRange > abs(iDeltaX) and iErrorRange > abs(iDeltaY) and iErrorRange > abs(iDeltaZ):
                    if i == Posistions[-1]:
                        return True
                    else:
                        time.sleep(iWaitMs)
                        break
                else:
                    self.Pos2Pos(i)

    def Cover2Start(self):
        while 1:
            if 100 < lidar.GetDists()[0] <= 500:
                return True
            else:
                pass

    def referee2Start(self):
        pass

class Communication:
    def __init__(self):
        if cfg.Transimission.Method == "WIFI":
            from utils.ReasonBeacon import MisakaNetwork
            self.transimission = MisakaNetwork()
        elif cfg.Transimission.Method == "BLE":
            pass
        else:
            raise RuntimeError("None Transmission Method Selected!")
        self.BallFlag = [0,0]
        self.PeerPosition = [0xfff,0xfff]
        self.FullLog = cfg.Debug.FullLog

    # Communicate Functions
    def BallOwner(self):# function for judging whether catch the ball
        '''
        ### function for judging whether catch the ball
        #### no return value, this function will change the global variable `BallFlag`
        '''
        BallX, BallY = Positions.AbsBallPos()
        if [BallX,BallY] == [0xddd,0xddd]:
            self.BallFlag[0] = 1
        else:
            self.BallFlag[0] = 0
        if self.FullLog:
            logger.debug("BallFlag Satus: %s"%self.BallFlag)
        else:
            pass

    def SendStatusThreadFunc(self): # send role and the status of the ball
        '''
        ### Warning: This function will stuck the main thread
        ### use `Sendstatus()` instead
        '''
        while (1):
            SelfPosition = Positions.AbsRoboPosition()
            try:
                # make sure all the values are integer
                ball_self = int(self.BallFlag[0]) if isinstance(self.BallFlag[0], (int, float, str)) else 0
                pos_x = int(SelfPosition[0])
                pos_y = int(SelfPosition[1])
                msg = f"BS:{ball_self};PX:{pos_x};PY:{pos_y}"
                self.transimission.Send(msg)
                if self.FullLog:
                    logger.success(f"Sent message: {msg}")  # Debug message
            except Exception as e:
                logger.error(f"Send error: {e}")
                raise e
            time.sleep(0.03) # in case too fast

    def SendStatus(self):
        '''
        ### Function for starting Send Status Thread
        #### return `True` if the Thread is already started
        '''
        global SendstatusThreadFuncStarted
        if not SendstatusThreadFuncStarted:
            SendstatusThread = threading.Thread(target=self.SendStatusThreadFunc)
            SendstatusThread.daemon = True  # Set as a daemon thread, will auto finished after the main thread finished
            SendstatusThread.start()
            SendstatusThreadFuncStarted = True
        return True

    def PeerStatusThreadFunc(self):
        '''
        ### Warning: This function will stuck main thread
        ### use `Peerstatus()` instead
        '''
        while (1):
            MessageCache = self.transimission.MessageCache
            if MessageCache == None:
                if self.FullLog:
                    logger.warning("No Messages")
                time.sleep(1)
            if MessageCache:
                try:
                    # setup default val
                    self.PeerPosition = [0xfff,0xfff]
                    self.BallFlag[1] = 0
                    for part in MessageCache.split(";"):
                        if part.startswith("BS:"):
                            self.BallFlag[1] = int(part.split(":")[1])  # convert into int
                        if part.startswith("PX:"):
                            PeerPositionX = int(float(part.split(":")[1]))  # process float number
                        if part.startswith("PY:"):
                            PeerPositionY = int(float(part.split(":")[1]))  # process float number
                    self.PeerPosition = [PeerPositionX, PeerPositionY]
                except Exception as e:
                    self.BallFlag = [0, 0]
                    self.PeerPosition = [0xfff, 0xfff]
                    logger.error(f"Failed to parse message '{MessageCache}': {e}")
                MessageCache = None
            time.sleep(0.02)

    def PeerStatus(self):# Start the Prase Thread
        '''
        ### Function for starting Prase Status Thread
        #### return `True` if the Thread is already started
        #### This thread will update the BallFlag
        '''
        global PeerstatusThreadFuncStarted
        if not PeerstatusThreadFuncStarted:
            PeerstatusThread = threading.Thread(target=self.PeerStatusThreadFunc)
            PeerstatusThread.daemon = True  # 设置为守护线程，主线程结束时自动结束
            PeerstatusThread.start()
            PeerstatusThreadFuncStarted = True

    def StartConncetion(self):
        '''
        ### Function for starting Send&Prase Status Thread
        '''
        if not PeerstatusThreadFuncStarted and not SendstatusThreadFuncStarted:
            self.SendStatus()
            self.PeerStatus()
        else:
            pass


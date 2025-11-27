import math, time, threading

from utils.ReasonData import logger, Settings
cfg = Settings

# from Vision import Vision as V
# vision = V()

from headunit import ArisuIntelligence
vision = ArisuIntelligence()

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

    # ********* BASIC FUNCTIONS ********
    def Relative_Ball_Position(self):
        '''
        Get the [Relative] Position of the ball
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
        elif abs(self.ballPos[1]-cfg.ExpectedVals.CatchVal[1]) <= cfg.ExpectedVals.ErrorRange and abs(self.ballPos[0]-cfg.ExpectedVals.CatchVal[0]) <= cfg.ExpectedVals.ErrorRange:
            self.ballPosOut = [0xddd,0xddd]
        else:
            self.ballPosOut = self.ballPos
        logger.debug("[Relative] Ball Position: %s"%self.ballPos)
        logger.info("[Relative] Ball Position Output: %s"%self.ballPosOut)
        return self.ballPosOut

    def direct_distance(self):
        '''
        Get the [Direct] Distance From the bound to the Bound
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
            self.LidarPos = [X/10,Y/10,compass()]
            logger.info("[Absolute] Robot Position: %s"%self.LidarPos)
            # 20251126 already changed X_forward,Y_left dimension    
            return [X/10,Y/10,compass()]
        elif Bits.Odometer is not None:# if use odometer datas
            # TODO finish lower Positions
            pass

    def AbsChassisPos(self):
        '''
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
        Get the [Absolute] Distance from Robot to Ball
        #### Returns:
            BallDistance: int | absolute Distance from Robot to Ball

        #### Note:
            `0xfff` stand for `NoBall`
            `0xddd` stand for `CatchBall`
        '''
        BallX, BallY = self.Relative_Ball_Position()
        x, y, _ = self.GetPosition()
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
        Get the [Absolute] Position from Robot to Ball
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
            ballDistance * math.cos(math.radians(ballAbsAngle)) + SelfY,
            ballDistance * math.sin(math.radians(ballAbsAngle)) + SelfX
            ]
        # 20251017 already changed X,Y dimension
        return AbsBallPositon

    def RelChassisAngle(self):
        '''
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
    
    # def MoveToPosition(self,Position:list[int,int,int],Kp:float|None = None):
    #     '''
    #     Move the robot to the target Position [X,Y,W]
    #     #### Args:
    #         Position: list | [X,Y,W]
    #         Kp: float | Proportional Coefficient for Yaw Correction
    #     '''
    #     # PID 控制实现：对 X 与 Y 使用独立的 P 控制（可扩展为 PID），并对朝向使用现有的 Kp 进行修正
    #     TargetX = float(Position[0])
    #     TargetY = float(Position[1])
    #     FacingAngle = float(Position[2])

    #     # PID 参数（可根据 cfg 或传参调整）
    #     Kp_pos = cfg.Control.KpPos if hasattr(cfg, 'Control') and hasattr(cfg.Control, 'KpPos') else 0.8
    #     Ki_pos = cfg.Control.KiPos if hasattr(cfg, 'Control') and hasattr(cfg.Control, 'KiPos') else 0.0
    #     Kd_pos = cfg.Control.KdPos if hasattr(cfg, 'Control') and hasattr(cfg.Control, 'KdPos') else 0.0

    #     # 速度限制（像素或单位到 PWM 的映射由底层处理），最大速度取配置或默认
    #     MaxSpeed = cfg.ExpectedVals.MaxSpeedValue if hasattr(cfg.ExpectedVals, 'MaxSpeedValue') else 800

    #     # PID 状态
    #     err_x_int = 0.0
    #     err_y_int = 0.0
    #     prev_err_x = 0.0
    #     prev_err_y = 0.0

    #     timeout = cfg.Control.MoveTimeout if hasattr(cfg, 'Control') and hasattr(cfg.Control, 'MoveTimeout') else 5.0
    #     start_t = time.time()

    #     while True:
    #         SelfX, SelfY, SelfZ = self.AbsRoboPosition()
    #         # 距离目标的误差
    #         err_x = TargetX - SelfX
    #         err_y = TargetY - SelfY
    #         dist = math.hypot(err_x, err_y)

    #         # 结束条件：到达目标点（小于阈值）或超时
    #         if dist <= (cfg.Control.PosTolerance if hasattr(cfg.Control, 'PosTolerance') else 5.0):
    #             # 停止底盘
    #             chassis.stop()
    #             break
    #         if (time.time() - start_t) > timeout:
    #             chassis.stop()
    #             logger.warning("MoveToPosition timeout, dist remaining: %s", dist)
    #             break

    #         # 积分与微分
    #         dt = 0.03
    #         err_x_int += err_x * dt
    #         err_y_int += err_y * dt
    #         err_x_der = (err_x - prev_err_x) / dt
    #         err_y_der = (err_y - prev_err_y) / dt

    #         # PID 计算（得到沿机器人坐标系的 SpeedX, SpeedY）
    #         # 先把全局坐标误差转换为车体坐标（以当前朝向 SelfZ）
    #         yaw_rad = math.radians(SelfZ)
    #         # 旋转误差向量到车体坐标系
    #         body_err_x = math.cos(yaw_rad) * err_x + math.sin(yaw_rad) * err_y
    #         body_err_y = -math.sin(yaw_rad) * err_x + math.cos(yaw_rad) * err_y

    #         SpeedX = int(max(-MaxSpeed, min(MaxSpeed, Kp_pos * body_err_x + Ki_pos * err_x_int + Kd_pos * err_x_der)))
    #         SpeedY = int(max(-MaxSpeed, min(MaxSpeed, Kp_pos * body_err_y + Ki_pos * err_y_int + Kd_pos * err_y_der)))

    #         # Yaw 修正（保持朝向 FacingAngle，复用 chassis 的 Kp 逻辑）
    #         chassis.AbsMoveVetor(SpeedX, SpeedY, FacingAngle, Kp)

    #         prev_err_x = err_x
    #         prev_err_y = err_y
    #         time.sleep(dt)

    def MoveToPosition(self, Position: list[int, int, int], Kp: float | None = None):
        selfPosition = self.AbsRoboPosition()
        dX = Position[0] - selfPosition[0]
        dY = Position[1] - selfPosition[1]
        dW = Position[2] - selfPosition[2]
        if abs(dX) < 5 and abs(dY) < 5 and abs(dW) < 5:
            return [0, 0, 0]  # 已经到达目标位置
        else:
            chassis.AbsMoveVetor(dX, dY, dW)
        

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


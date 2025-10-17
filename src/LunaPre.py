import math
import time
import threading

from .utils.ReasonData import logger, Settings
cfg = Settings

from headunit import Lidar,ArisuIntelligence
Vision = ArisuIntelligence()
from chassis import Car,Peripherals # Universal-Movement-Standard
if cfg.RoboInfo.Bit == "AB":
    from utils.ArisuBits import ArisBit
    Bits = ArisBit()
    lidar = Lidar(Bits.GetYaw)
    chassis = Car(Bits.SetMotor,Bits.GetYaw)
    compass = Bits.GetYaw
    peripheral = Peripherals(Bits.SetIO)
    logger.info("Arisu Bit loaded.")
# elif cfg.RoboInfo.Bit") == "RM":
#     from utils.RobomasterBits import RobomasterBits
#     Bits = RobomasterBits()
#     lidar = Lidar(Bits.GetYaw)
#     chassis = Car(Bits.SetMotor,Bits.GetYaw)
#     compass = Bits.GetYaw
#     # peripheral = Peripherals(Bits.SetIO) #TODO
#     logger.info("RoboMaster Bits loaded.")
# elif cfg.RoboInfo.Bit") == "3Q":
#     logger.info("ZUES Bit loaded.")
#     # peripheral = Peripherals(Bits.SetIO) #TODO
#     logger.info("RoboMaster Bit loaded.")
else:
    logger.error("None Bit Model Fetched.")
    raise ImportError("None Bit Model Set.")

class Positions():
    def __init__(self):
        # Values for Setup Position System
        self.LidarPos = [0xfff,0xfff,0xfff]
        self.BallPos = [0xfff,0xfff]
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
    def RelBallPos(self):
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
        self.BallPos = Vision.GetBallPos()
        if self.BallPos == [0,0]:
            self.BallPos = [0xfff,0xfff]
        if abs(self.BallPos-cfg.ExpectedVals.CatchVal) <= cfg.ExpectedVals.ErrorRange:
            self.BallPos = [0xddd,0xddd]
        logger.info("[Relative] Ball Position: %s"%self.BallPos)
        return self.BallPos

    def DirDistance(self):
        '''
        Get the [Direct] Distance From the bound to the Bound
        #### Args:

        #### Returns:
            RobotPosition: [0,0]
        #### Note:
            `0xfff` stand for `NoPosition`
        '''
        self.BoundsDistance = lidar.GetDists()
        if self.BoundsDistance == [0,0,0,0]:
            self.WarnedLidarCount = self.WarnedLidarCount + 1
            time.sleep(self.WaitTime) # wait 1 second for starting lidar
            logger.warning("Lidar Not Started! Retry for %s time in %s second"%(self.WarnedLidarCount,self.WaitTime))
            if self.WarnedLidarCount > cfg.ExpectedVals.MaxWarnCount:
                logger.error("No Lidar Data Recieved! Please Check Lidar Modules!")
                raise RuntimeError("No Lidar Data Recieved! Please Check Lidar Modules!")
            return [0xfff,0xfff,compass()]
        else:
            if self.WarnedLidarCount:
                self.WarnedLidarCount = 0
                logger.success("Lidar System Started!Read [Direct] Robot Distance: %s"%self.BoundsDistance)
            else:
                pass
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
            _distance = self.DirDistance()
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
            # 20251017 already changed X,Y dimension    
            return [Y/10,X/10,compass()]
        else:
            # TODO finish lower Positions
            raise RuntimeError("You Choosed the Wrong Args!")

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
        ChassisRawList = Vision.GetChassisPos()
        SelfX,SelfY,SelfZ = Positions.AbsRoboPosition()
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
        ballX,ballY = Vision.GetBallPos()
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
        BallX, BallY = self.RelBallPos()
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
        ballX,ballY = Vision.GetBallPos()
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
        ChassisRawList = Vision.GetChassisPos()
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


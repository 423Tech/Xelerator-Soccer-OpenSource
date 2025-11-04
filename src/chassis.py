import math
from utils.ReasonData.config import Settings
import time

class Car:
    def __init__(self,SetMotorFunc,GetYaw=None,MotorEncoder=None):
        self.SetMotorFunc = SetMotorFunc
        self.GetYaw = GetYaw
        self.MotorEncoder = MotorEncoder
        self.Kp = 0.8
        self.cfg = Settings
        if self.cfg.Debug.Database:
            from utils.ReasonData.data import Outputs
            self.DataBase = Outputs()
        if self.cfg.Debug.FullLog:
            from utils.ReasonData import logger
            self.logger = logger
    
    def SetMotor(self,speedCache:list[int,int,int,int]):
        number = [self.cfg.Ports.LeftFront,self.cfg.Ports.LeftBack,self.cfg.Ports.RightFront,self.cfg.Ports.RightBack]
        speed = [0,0,0,0]
        for n in number:
            speed[n-1] = int(speedCache[n-1])
        if self.cfg.Debug.FullLog:
            if self.MotorEncoder:
                EncoderCache = self.MotorEncoder()
                Encoder =[0,0,0,0]
                for n in number:
                    Encoder[n-1] = int(EncoderCache[n-1])
                self.logger.debug("SetMotorVals: (%s, %s, %s, %s) | With feedbackVals %s" %
                                   (speed[0], speed[1], speed[2], speed[3],Encoder)
                                   )
            else:
                self.logger.debug("SetMotorVals: %s, %s, %s, %s" % (speed[0], speed[1], speed[2], speed[3]))
        self.SetMotorFunc(speed[0], speed[1], speed[2], speed[3])
    
    def SetKp(self,Kp):
        self.Kp = Kp
    
    def Compass(self):
        return self.GetYaw()

    def RelMoveVetor(self,SpeedX,SpeedY,SpeedZ):
        '''
        a vector movement (SpeedX,SpeedY,SpeedZ) without YawCorrect
        '''
        Speed1 = SpeedX + SpeedY + SpeedZ
        Speed2 = SpeedY - SpeedX + SpeedZ
        Speed3 = SpeedY - SpeedX - SpeedZ
        Speed4 = SpeedX + SpeedY - SpeedZ
        if self.cfg.Debug.FullLog:
            self.DataBase.SetOutput(Speed1,Speed2,Speed3,Speed4)
        output = [Speed1, Speed2, Speed3, Speed4]
        self.SetMotor(output)
    
    def AbsMoveAngle(self,FacingAngle,MovingAngle,Speed,Kp:float|None = None):
        '''
        angle movement (FacingAngle,MovingAngle,speed) with YawCorrect
        '''
        Yaw = self.GetYaw()
        rad = math.radians(MovingAngle+360-Yaw)
        SpeedX = int(math.sin(rad) * Speed)
        SpeedY = int(math.cos(rad) * Speed)
        self.AbsMoveVetor(SpeedX,SpeedY,FacingAngle,Kp)
        
    def AbsMoveVetor(self,SpeedX,SpeedY,FacingAngle,Kp:float|None = None):
        '''
        vector movement (SpeedX,SpeedY,SpeedZ) with YawCorrect
        '''
        Yaw = self.GetYaw()
        Error = Yaw - FacingAngle
        Error = (Error + 180) % 360 - 180  # Normalize to [-180, 180]
        if not Kp:
            Kp = self.Kp
        SpeedZ = - Error * Kp
        self.RelMoveVetor(SpeedX, SpeedY, SpeedZ)
    
    def RelXMove(self,Angle,Speed):
        self.RelMoveVetor(Angle,90,Speed)
   
    def RelYMove(self,Angle,Speed,Kp=None):
        self.AbsMoveAngle(Angle,0,Speed,Kp)

    def AbsTurn(self,Angle,Kp=None):
        if self.GetYaw is None:
            return False
        self.AbsMoveAngle(Angle,0,0,Kp)

    def RelTurn(self,Speed): #自转
        self.RelMoveVetor(0,0,Speed)
    
    def TurnTo(self,Angle,AimSpeed,Kp=None):
        while True:
            Error = self.GetYaw() - Angle
            Error = (Error + 180) % 360 - 180

            Speed = AimSpeed
            
            if Error < -5:
                self.RelTurn(Speed)
            elif Error > 5:
                self.RelTurn(-Speed)
            else:
                break
            time.sleep(0.03)
            
    def stop(self):
        self.SetMotor([0,0,0,0])


class Peripherals:
    def __init__(self,IOFunc):
        self.SetIO = IOFunc
        from utils.ReasonData import Settings
        self.cfg = Settings
        from utils.ReasonData import logger
        self.logger = logger
        self.SetIO(self.cfg.Ports.ElecMagnet,1)
        self.DribbleStatus = False

    def ShootBall(self):
        self.SetIO(self.cfg.Ports.ElecMagnet,0)
        time.sleep(0.3)
        self.SetIO(self.cfg.Ports.ElecMagnet,1)
        self.logger.info("Used ElecMagnet")

    def Dribble(self,Status:bool):
        if self.DribbleStatus == Status:
            pass
        else:
            if Status:
                self.SetIO(self.cfg.Ports.Dribble,1)
            else:
                self.SetIO(self.cfg.Ports.Dribble,0)
            self.DribbleStatus = Status
            self.logger.info("Dribble set to %s" % ("ON" if Status else "OFF"))
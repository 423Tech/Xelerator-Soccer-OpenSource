import math
from ReasonData.config import QkJson



class Car:
    def __init__(self,SetMotorFunc,GetYaw=None):
        self.SetMotorFunc = SetMotorFunc
        self.GetYaw = GetYaw

        self.Kp = 1
        
        self.cfg = QkJson()
        self.SaveData = self.cfg.read("Advanced","Database")
        if self.SaveData:
            from ReasonData.data import Outputs
            self.DataBase = Outputs()
        self.SaveLog = self.cfg.read("Advanced","logger")
        if self.SaveLog:
            from ReasonData import logger
            self.logger = logger
    
    def SetMotor(self,Speed1,Speed2,Speed3,Speed4):
        self.logger.debug("SetMotor: %s, %s, %s, %s" % (Speed1, Speed2, Speed3, Speed4))
        self.SetMotorFunc(int(Speed1), int(Speed2), int(Speed3), int(Speed4))
    
    def SetKp(self,Kp):
        self.Kp = Kp
    
    def Compass(self):
        return self.GetYaw() if self.GetYaw is not None else None

    def Go(self,SpeedX,SpeedY,SpeedZ):
        '''
        stand for a vector movement (SpeedX,SpeedY,SpeedZ)
        '''
        Speed1 = SpeedX + SpeedY + SpeedZ
        Speed2 = SpeedY - SpeedX + SpeedZ
        Speed3 = SpeedY - SpeedX - SpeedZ
        Speed4 = SpeedX + SpeedY - SpeedZ
        if self.SaveData:
            self.DataBase.SetOutput(Speed1,Speed2,Speed3,Speed4)
        self.SetMotor(Speed1, Speed2, Speed3, Speed4)
    
    def GoA(self,FacingAngle,MovingAngle,Speed):
        if self.GetYaw is None:
            return False
        Yaw = self.GetYaw()
        rad = math.radians(MovingAngle+360-Yaw)
        SpeedX = int(math.sin(rad) * Speed)
        SpeedY = int(math.cos(rad) * Speed)
        self.GoV(SpeedX,SpeedY,FacingAngle)

    def GoV(self,SpeedX,SpeedY,FacingAngle):
        '''
        stand for a vector movement (SpeedX,SpeedY,SpeedZ)
        '''
        if self.GetYaw is None:
            return False
        Yaw = self.GetYaw()
        Error = Yaw - FacingAngle
        Error = (Error + 180) % 360 - 180  # Normalize to [-180, 180]
        SpeedZ = - Error * self.Kp
        self.Go(SpeedX, SpeedY, SpeedZ)
    
    def GoX(self,Angle,Speed):
        if self.GetYaw is None:
            return False
        self.GoA(Angle,90,Speed)
   
    def GoY(self,Angle,Speed):
        if self.GetYaw is None:
            return False
        self.GoA(Angle,0,Speed)

    def GoZ(self,Angle):
        if self.GetYaw is None:
            return False
        self.GoA(Angle,0,0)

    def GoZspeed(self,Speed): #Macao
        Speed1 = Speed
        Speed2 = Speed
        Speed3 = - Speed
        Speed4 = - Speed
        if self.SaveData:
            self.DataBase.SetOutput(Speed1,Speed2,Speed3,Speed4)
        self.SetMotor(Speed1, Speed2, Speed3, Speed4)

    def stop(self):
        self.SetMotor(0,0,0,0)


class Peripherals:
    def __init__(self,IOFunc):
        self.SetIO = IOFunc
        from ReasonData import QkJson
        self.cfg = QkJson()
        from ReasonData import logger
        self.logger = logger
        self.ElecMagnetIO = self.cfg.read("Ports","ElecMagnet")
        self.DribbleIO = self.cfg.read("Ports","Dribble")

    def ShootBall(self):
        self.SetIO(self.ElecMagnetIO,0)
        self.SetIO(self.ElecMagnetIO,1)
        self.SetIO(self.ElecMagnetIO,0)
        self.logger.info("Used ElecMagnet")

    def DribbleBall(self):
        self.SetIO(self.DribbleIO,1)
        self.logger.info("Start Dribble")

    def StopDribble(self):
        self.SetIO(self.DribbleIO,0)
        self.logger.info("Stop Dribble")

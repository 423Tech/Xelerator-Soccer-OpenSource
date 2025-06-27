class Car:
    def __init__(self,MotorFunc,GetYaw=None):

        self.MotorFunc = MotorFunc
        self.GetYaw = GetYaw

        self.Kp = 0.5
    
        from ReasonData.config import QkJson
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
        self.MotorFunc(int(Speed1), int(Speed2), int(Speed3), int(Speed4))
        

    def SetKp(self,Kp):
        self.Kp = Kp
    
    # def GetYaw(self):
    #     return self.GetYawFunc()
    
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
    
    def GoA(self,FacingAngle,MovingAngle,Speed):
        if self.GetYaw is None:
            return False
    
    def GoX(self,Angle,Speed):
        if self.GetYaw is None:
            return False
   
    def GoY(self,Angle,Speed):
        if self.GetYaw is None:
            return False
    
    def GoZ(self,Angle):
        if self.GetYaw is None:
            return False
    

class ElecMagnet:
    def __init__(self,Shoot,DribbleIO):
        from ReasonData import QkJson
        self.cfg = QkJson()
        self.ElecMagnetIO = self.cfg.read("Ports","ElecMagnet")
        self.DribbleIO = self.cfg.read("Ports","DribbleIO")
        
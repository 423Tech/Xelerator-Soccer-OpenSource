class Car:
    def __init__(self,SetMotor,GetYaw=None):
        self.SetMotor = SetMotor
        self.GetYaw = GetYaw

        self.Kp = 0.5
    
    # def SetMotor(self,Speed1,Speed2,Speed3,Speed4):
    #     self.SetMotorFunc(int(Speed1), int(Speed2), int(Speed3), int(Speed4))
    
    def SetKp(self,Kp):
        self.Kp = Kp
    
    # def GetYaw(self):
    #     return self.GetYawFunc()
    
    def Go(self,SpeedX,SpeedY,SpeedZ):
        Speed1 = SpeedX + SpeedY + SpeedZ
        Speed2 = SpeedY - SpeedX + SpeedZ
        Speed3 = SpeedY - SpeedX - SpeedZ
        Speed4 = SpeedX + SpeedY - SpeedZ
        self.SetMotor(Speed1, Speed2, Speed3, Speed4)

    def GoV(self,SpeedX,SpeedY,FacingAngle):
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
    def __init__(self,GetYaw=None):
        from ReasonData import QkJson
        self.cfg = QkJson()
        self.ElecMagnetIO = self.cfg.read()
        self.GetYaw = GetYaw

        self.Kp = 0.5
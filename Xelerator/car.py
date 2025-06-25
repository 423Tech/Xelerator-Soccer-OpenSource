class Car:
    def __init__(self,SetMotorFunc,GetYawFunc=None):
        self.SetMotorFunc = SetMotorFunc
        self.GetYawFunc = GetYawFunc

        self.Kp = 2
    
    def SetMotor(self,Speed1,Speed2,Speed3,Speed4):
        self.SetMotorFunc(int(Speed1), int(Speed2), int(Speed3), int(Speed4))
    
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
        if self.GetYawFunc is None:
            return False
        Yaw = self.GetYawFunc()
        Error = FacingAngle - Yaw
        Error = (Error + 180) % 360 - 180  # Normalize to [-180, 180]
        SpeedZ = Error * self.Kp
        self.Go(SpeedX, SpeedY, SpeedZ)
    
    def GoA(self,FacingAngle,MovingAngle,Speed):
        if self.GetYawFunc is None:
            return False
    
    def GoX(self,Angle,Speed):
        if self.GetYawFunc is None:
            return False
   
    def GoY(self,Angle,Speed):
        if self.GetYawFunc is None:
            return False
    
    def GoZ(self,Angle):
        if self.GetYawFunc is None:
            return False
    

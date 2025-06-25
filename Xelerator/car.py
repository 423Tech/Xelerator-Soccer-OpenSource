class Car:
    def __init__(self,SetMotorFunc,GetYawFunc=None):
        self.SetMotorFunc = SetMotorFunc
        self.GetYawFunc = GetYawFunc
    
    def SetMotor(self,Speed1,Speed2,Speed3,Speed4):
        self.SetMotorFunc(int(Speed1), int(Speed2), int(Speed3), int(Speed4))
    
    def GetYaw(self):
        return self.GetYawFunc()
    
    def Go(self,SpeedX,SpeedY,SpeedZ):
        Speed1 = SpeedX + SpeedY + SpeedZ
        Speed2 = SpeedY - SpeedX + SpeedZ
        Speed3 = SpeedY - SpeedX - SpeedZ
        Speed4 = SpeedX + SpeedY - SpeedZ
        self.SetMotor(Speed1, Speed2, Speed3, Speed4)
    
    def GoA(self,FacingAngle,MovingAngle,Speed):
        if self.GetYaw is None:
            return False
    
    def GoV(self,SpeedX,SpeedY,FacingAngle):
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
    

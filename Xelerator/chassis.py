import math

class Car:
    def __init__(self,SetMotorFunc,GetYaw=None):
        self.SetMotorFunc = SetMotorFunc
        self.GetYaw = GetYaw

        self.Kp = 1
    
    def SetMotor(self,Speed1,Speed2,Speed3,Speed4):
        self.SetMotorFunc(int(Speed1), int(Speed2), int(Speed3), int(Speed4))
    
    def SetKp(self,Kp):
        self.Kp = Kp
    
    def Go(self,SpeedX,SpeedY,SpeedZ):
        Speed1 = SpeedX + SpeedY + SpeedZ
        Speed2 = SpeedY - SpeedX + SpeedZ
        Speed3 = SpeedY - SpeedX - SpeedZ
        Speed4 = SpeedX + SpeedY - SpeedZ
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
   
    def GoY(self,Angle,Speed):
        if self.GetYaw is None:
            return False
    
    def GoZ(self,Angle):
        if self.GetYaw is None:
            return False
    

class Car:
    def __init__(self,SetMotorFunc,GetYawFunc):
        self.SetMotorFunc = SetMotorFunc
        self.GetYawFunc = GetYawFunc
    
    def SetMotor(self,Speed1,Speed2,Speed3,Speed4):
        self.SetMotorFunc(int(Speed1), int(Speed2), int(Speed3), int(Speed4))
    
    def GetYaw(self):
        return self.GetYawFunc()
    
    def Go(self,SpeedX,SpeedY,SpeedZ):
        
    

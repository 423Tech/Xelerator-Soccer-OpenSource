from ReasonData import config

class command:
    def __init__(self):
        import serial
        self.ser = serial.Serial()
        self.ser.port = config().read("BASE","COM")
        self.ser.baudrate = 115200
        self.ser.bytesize = serial.EIGHTBITS
        self.ser.stopbits = serial.STOPBITS_ONE
        self.ser.parity = serial.PARITY_NONE
        self.ser.timeout = 0.2
        self.ser.write("command;".encode('utf-8'))
        if "ok" in self.ser.readall().decode('utf-8'):
            pass
        else:
            raise ConnectionRefusedError("Failed To Connect SDK,errorMsg: %s",self.ser.readall().decode('utf-8'))

    def send(self,command:str):
        self.ser.open()
        command += ';'
        self.ser.write(command.encode('utf-8'))
        recv = self.ser.readall().decode('utf-8')
        self.ser.close()
        return recv


class motor:
    def __init__(self):
        self.cmd = command()

    def RPM(self, w1:int, w2:int, w3:int, w4:int):
        recv = self.cmd.send("chassis wheel w1%s w2 %s w3 %s w4 %s",(w1,w2,w3,w4))
        return recv
    
class batt:
    def __init__(self):
        self.cmd = command()
    
    def get(self):
        return self.cmd("robot battery ?")
    
class pos:
    def __init__(self):
        self.cmd = command()

    def move(self, x:int, y:int):
        return self.cmd("chassis move x %s y %s",(x,y))
    
    def get(self):
        return self.cmd("chassis position ?")
    
class compass:
    def __init__(self):
        self.cmd = command()
    
    def get(self):
        #TODO GetAngle
        recv = self.cmd("chassis attitude ?")
        return recv
    
    


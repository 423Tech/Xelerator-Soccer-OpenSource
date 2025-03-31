from machine import UART,Pin

from MisakaNet import misakaNet
from QkConf import QkJson

cfg = QkJson()

while True:
    if cfg.read("model","type") == "Off":
        misakaNet.connectWIFI("MisakaNet","")
        misakaNet.sendData("192.168.4.1","10000","12345")    
        data = UART(1,baudrate = 115200,bits = 8,parity = None,stop = 1 ,tx = Pin(43),rx = Pin(44))
        print(data.read())
    elif cfg.read("model","type") == "Deff":
        misakaNet.startAP("MisakaNet","")
        dataNet = misakaNet.receiveData("192.168.4.2","10000","12345")
        data = UART(1,baudrate = 115200,bits = 8,parity = None,stop = 1 ,tx = Pin(21),rx = Pin(20))
        data.write(dataNet)

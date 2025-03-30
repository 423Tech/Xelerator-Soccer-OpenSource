import UART
import pin

from MisakaNet import misakaNet
from QkConf import QkJson

cfg = QkJson()

while True:
    if cfg.read("model","type") == "Off":
        misakaNet.startAP("MisakaNet","")
        data = UART(2, 115200, rx=3, tx=1)
    elif cfg.read("model","type") == "Deff":
        misakaNet.connectWIFI("MisakaNet","")
        data = UART(2, 115200, rx=20, tx=21)
    
    

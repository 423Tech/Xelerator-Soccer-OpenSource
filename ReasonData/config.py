import ujson
import os
from pathlib import Path

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
CONFIG_FILE = DATA_DIR / "config.json"
CACHE_FILE = DATA_DIR /  "cfg.cache.json"

class Preference:
    def __init__(self):
        data = {
                "RoboInfo": {
                    "number" : 1,
                    "type": "OP", # OffencePlayer/DefencePlayer
                    "Bit" : "AB",
                    "AI" : "Hailo", # Hailo/RDK
                },
                "Ports": {
                    "LowTigger?" : 0, 
                    "JudgePort": 1,
                    "ElecMagnet" : 3,
                    "Dribble" : 4,
                    "LidarID": 99,
                    "LeftFront" : 1,
                    "LeftBack" : 2,
                    "RightFront" : 3,
                    "RightBack" : 4,
                },
                "VisionVals": {
                    "Record" : False, # False to Disable Record video
                    "ExposeVal" : 100, # 0-255, 0: Auto, 1-255: Manual
                    "AutoExpose" : 0,  # 0: Manual, 1: Auto
                },
                "Bounds" : {
                    "ClsPos": [35,85,0], #Bound CheckPoint (Close to [0,0])
                    "FarPos": [75,95,0], #Bound CheckPoint (Far from [0,0])
                    "Short" : 200, # length of short side
                    "Long" : 260, # length of longer side
                },
                "CheckPoints" : {
                    "Home": [0,-70,0],
                },
                "ExpectedVals": {
                    "CatchVal" : [0,9], # Position when Robo Cathch the ball
                    "ErrorRange": 10,
                },
                "Transimission": {
                    "Type" : "Slave", # master to start AP/ slave to connect
                    "Method" : "WIFI", # WIFI/BLE
                },
                "BLE" : {
                    "MAC" : "NONE",
                    "REMOTE" : "NONE",
                },
                "WIFI" : {
                    "SelfIP" : "192.168.1.x",
                    "RemoteIP" : "192.168.1.x",
                    "Port" : 20001,
                    "SSID" : "MisakaNetwork",
                    "PWD" : "MisakaNetwork20001/",
                },
                "Debug": {
                    "DebugWifi": "RoboCup",
                    "DebugIP": "192.168.1.109",
                    "DebugPSWD": "12345",
                    "FullLog": True,
                    "Database": True,
                },
                "Advanced": {
                    "Cover2Start": False,
                }
            }
        try:
            os.stat(CONFIG_FILE)
        except:
            with open(CONFIG_FILE, "w") as f:
                ujson.dump(data, f)
        with open(CONFIG_FILE) as f:
            self.cfg = ujson.load(f)
            bUpdate = False
            for i in data:
                for c in data[i].keys():
                    try:
                        self.cfg[str(i)][str(c)]
                    except:
                        bUpdate = True
        if bUpdate:
            os.rename(CONFIG_FILE,CACHE_FILE)
            with open(CACHE_FILE, "r") as ca:
                self.cache = ujson.load(ca)
            with open(CONFIG_FILE, "w") as d:
                ujson.dump(data, d)
            with open(CONFIG_FILE, "r") as d:
                self.cfg = ujson.load(d)
            for i in data:
                for c in data[i].keys():
                    try:
                        vCache = self.cache[str(i)][str(c)]
                        self.cfg[str(i)][str(c)] = vCache
                        with open(CONFIG_FILE, "w") as d:
                            ujson.dump(self.cfg, d)
                    except:
                        pass
            os.remove(CACHE_FILE)

    def write(self, section: str, option: str, value: int) -> int:
        self.cfg[section][option] = value
        with open(CONFIG_FILE, "w") as f:
            ujson.dump(self.cfg, f)

    def read(self, section: str, option: str) -> int:
        try:
            return self.cfg[section][option]
        except KeyError:
            self.__init__()

import ujson
import os
from pathlib import Path

APP_DIR = Path(__file__).parent
DATA_DIR = APP_DIR / "data"
CONFIG_FILE = DATA_DIR / "config.json"
CACHE_FILE = DATA_DIR /  "cfg.cache.json"

class QkJson:
    def __init__(self):
        data = {
                "model": {
                    "number" : 1,
                    "name" : "None",
                    "type": "Offense",
                    "Bit" : "AB",
                },
                "Ports": {
                    "LowTigger" : 0,
                    "ElecMagnet" : 3,
                    "Dribble" : 4,
                },
                "Motors": {
                    "LeftFront" : 0,
                    "LeftBack" : 1,
                    "RightFront" : 2,
                    "RightBack" : 3,
                },
                "Vision": {
                    "Record" : False, # False to Disable Record video
                    "ExposeVal" : 100, # 0-255, 0: Auto, 1-255: Manual
                    "AutoExpose" : 0,  # 0: Manual, 1: Auto
                },
                "Border" : {
                    "0": [60,95],
                    "1": [40,85],
                },
                "Position" : {
                    "DomainID" : 88, # Lidar Domain ID
                    "ErrorRange": 15, # Error Range for Position
                    "Width": 200,
                    "Height": 260,
                    "Home": [0,-70,0],
                },
                "BLE" : {
                    "Type": "Slave",
                    "MAC" : "NONE",
                    "REMOTE" : "NONE",
                },
                "WIFI" : {
                    "SSID" : "None",
                    "PWD" : "",
                },
                "Advanced": {
                    "Cover2Start": False,
                    "logger": True,
                    "Database": True,
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

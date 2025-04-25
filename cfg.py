# config.py | RCJ Version 1.4.0(2025040800) Developer 423
import ujson
import os
CONFIG_FILE = "./cfg.json"
CACHE_FILE = "./cfg.cache.json"
class QkJson:
    def __init__(self):
        data = {
                "model": {
                    "number" : 1,
                    "type": "Off",
                },
                "Tofs": {
                    "On": True,
                    0: 1,
                    1: 2,
                    2: 3,
                    3: 4,
                    "K": 0.67,
                    "B": 4,
                    },
                "A2AOb": {
                    "ActiveRange": 30,
                    "IgnoreRange": 30,
                    "NumOfDist" : 4,
                    "LifeTime" : 3,
                },
                "Border" : {
                    "0": [60,95],
                    "1": [40,85],
                },
                "Position" : {
                    "ErrorRange": 20,
                    "Width": 180,
                    "Height": 240,
                    "Home": [0,-70],
                },
                "BLE" : {
                    "MAC" : "NONE",
                    "Type" : "Domain",
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
        with open(CONFIG_FILE) as d:
            self.cfg = ujson.load(d)
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
                        print(vCache)
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
        return self.cfg[section][option]

cfg = QkJson()

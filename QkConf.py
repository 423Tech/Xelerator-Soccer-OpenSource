# config.py | RCJ Version 1.0.2(2025032800) Developer 423
import ujson
import os

CONFIG_FILE = "./cfg.json"

class QkJson:
    def __init__(self):
        try:
            os.stat(CONFIG_FILE)
        except:
            data = {
                "model": {
                    "number" : 1,
                    "type": "Off",
                },
                "Tofs": {
                    0: 1,
                    1: 2,
                    2: 3,
                    3: 4,
                    },
                "A2AOb": {
                    "AvRange": 40,
                    "IgnrRange": 80,
                    "NumOfDist" : 4,
                    "LifeTime" : 4,
                },
                "Border" : {
                    "0": 20,
                    "1": 30,
                    "2": 20,
                    "3": 30,
                },
                "Position" : {
                    "home": [0,0],
                },
                "Advanced": {
                    "Luna": "False",
                },
                "Versions": {
                    "v": 0.1,
                }
            }
            with open(CONFIG_FILE, "w") as f:
                ujson.dump(data, f)
        with open(CONFIG_FILE) as f:
            self.cfg = ujson.load(f)

    def write(self, section: str, option: str, value: int) -> int:
        self.cfg[section][option] = value
        with open(CONFIG_FILE, "w") as f:
            ujson.dump(self.cfg, f)

    def read(self, section: str, option: str) -> int:
        return self.cfg[section][option]

if __name__ == "__main__":
    config = QkJson()
    config.read("model","type")
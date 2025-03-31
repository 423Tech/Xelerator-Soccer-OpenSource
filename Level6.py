# from models import set_adc

# # config.py | RCJ Version 1.0.2(2025032800) Developer 423
# import ujson
# import os

# CONFIG_FILE = "./cfg.json"

# class QkJson:
#     def __init__(self):
#         try:
#             os.stat(CONFIG_FILE)
#         except:
#             data = {
#                 "model": {
#                     "number" : 1,
#                     "type": "Off",
#                 },
#                 "Tofs": {
#                     0: 1,
#                     1: 2,
#                     2: 3,
#                     3: 4,
#                     "K": 6.7,
#                     "B": 40,
#                     },
#                 "A2AOb": {
#                     "ActiveRange": 40,
#                     "IgnoreRange": 80,
#                     "NumOfDist" : 4,
#                     "LifeTime" : 2,
#                 },
#                 "Border" : {
#                     "0": 20,
#                     "1": 30,
#                     "2": 20,
#                     "3": 30,
#                 },
#                 "Position" : {
#                     "Width": 1800,
#                     "Height": 2400,
#                 },
#                 "Versions": {
#                     "v": 0.1,
#                 }
#             }
#             with open(CONFIG_FILE, "w") as f:
#                 ujson.dump(data, f)
#         with open(CONFIG_FILE) as f:
#             self.cfg = ujson.load(f)

#     def write(self, section: str, option: str, value: int) -> int:
#         self.cfg[section][option] = value
#         with open(CONFIG_FILE, "w") as f:
#             ujson.dump(self.cfg, f)

#     def read(self, section: str, option: str) -> int:
#         return self.cfg[section][option]


# Cfg = QkJson()

# def getDists(Num: int) -> list[int,int,int]:
#     lDists = []
#     for i in range(Num):
#         # lDists.append(set_adc.read(i))
#         lDists.append(
#             int(set_adc.read(Cfg.read("Tofs",str(i)))*Cfg.read("Tofs","K")+Cfg.read("Tofs","B"))
#             )
#     return lDists

# def GetPos() -> list[int,int]:
#     Distance = getDists(4)
#     if Distance[0]+Distance[2] < Cfg.read("Position","Height") - 100:
#         if Distance[0] > Distance[2]:
#             Y = Cfg.read("Position","Height")/2 - Distance[0]
#         else:
#             Y = Cfg.read("Position","Height")/2 - Distance[2]
#     else:
#         Y = ((Cfg.read("Position","Height")/2 - Distance[0]) + (Cfg.read("Position","Height")/2 - Distance[2]))/2
#     if Distance[1]+Distance[3] < Cfg.read("Position","Width") - 100:
#         if Distance[0] > Distance[2]:
#             X = Cfg.read("Position","Width")/2 - Distance[1]
#         else:
#             X = Cfg.read("Position","Width")/2 - Distance[3]
#     else:
#         X = ((Cfg.read("Position","Width")/2 - Distance[1]) + (Cfg.read("Position","Width")/2 - Distance[3]))/2

#     return [X,Y]



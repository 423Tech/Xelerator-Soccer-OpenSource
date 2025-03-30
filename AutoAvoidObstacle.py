# A2O.py | RCJ Version 0.0.2(2025032800) Developer 423

import sensor,image,lcd,math,time,pyb
from pyb import UART
import delay,beep,timer,car,compass,key,set_adc,set_servo,set_pwm,set_io,set_motor,set_led
import binascii
import framebuf



clock = time.clock()

# config.py | RCJ Version 1.0.2(2025032800) Developer 423
import ujson
import os
CONFIG_FILE = "./config.json"
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

Cfg = QkJson()



def getadc():
    global iTof1,iTof0,iTof3,iTof2,dhl,dhb,dhr,bx,by
    bx = set_adc.read(11)
    by = set_adc.read(12)
    iTof0 = int(set_adc.read(Cfg.read("adcs","tof0"))/3.5)
    iTof1 = int(set_adc.read(Cfg.read("adcs","tof1"))/3.5)
    iTof2 = int(set_adc.read(Cfg.read("adcs","tof2"))/3.5)
    iTof3 = int(set_adc.read(Cfg.read("adcs","tof3"))/3.5)
    dhl = set_adc.read(Cfg.read("adcs","gs1"))
    dhb = set_adc.read(Cfg.read("adcs","gs2"))
    dhr = set_adc.read(Cfg.read("adcs","gs3"))


iNumOfDist = Cfg.read("A2AOb","NumOfDist")
iMaxLife = Cfg.read("A2AOb","LifeTime")
iMemoLife = iMaxLife
bLife = False
lBlockedMemo = []
lStatusOfDist = []

def getDists(Num: int) -> list[int,int,int]:
    lDists = []
    for i in range(Num):
        lDists.append(set_adc.read(i))
        # lDists.append(set_adc.read(Cfg.read("Tofs",str(i))))
    return lDists
    
def ObtDetect():
    global lBlockedMemo,lStatusOfDist,iMemoLife,bLife
    lDists = getDists(iNumOfDist)
    if len(lStatusOfDist) < iNumOfDist:
        for d in range(iNumOfDist):
            lStatusOfDist.append(True)
    for i in range(iNumOfDist):
        if lStatusOfDist[i] and lDists[i] <= Cfg.read("A2AOb","AvRange"):
            lStatusOfDist[i] = False
            iMemoLife = iMaxLife
            lBlockedMemo.append(i)
            if len(lBlockedMemo) > (iNumOfDist - 1):
                lStatusOfDist[lBlockedMemo[0]] = True
                lBlockedMemo.pop(0)
            bLife = False
        if not lStatusOfDist[i] and lDists[i] >= Cfg.read("A2AOb","IgnrRange")*2:
            bLife = True
        else:
            bLife = False
    if bLife:
        if len(lBlockedMemo) > 0 and iMemoLife > 0:
            iMemoLife = iMemoLife - 1
            if iMemoLife == 0:
                lStatusOfDist[lBlockedMemo[0]] = True
                lBlockedMemo.pop(0)
                iMemoLife = iMaxLife
        if len(lStatusOfDist) == 0:
            iMemoLife = iMaxLife
        bLife = False

    
def AvoidObt(iAimAngle: int) -> None:
    ObtDetect()
    lTrueAngles = []
    iPerAngle = 359/iNumOfDist
    for i in range(iNumOfDist):
        if lStatusOfDist[i]:
            lTrueAngles.append(i*iPerAngle)
    if len(lTrueAngles) == 1:
        iAoidAngle = 1*iPerAngle
        print(iAoidAngle)
        # car.straight(iAoidAngle,150,5,5)
        car.z_move(0,iAimAngle,200)
    if len(lTrueAngles) > 1:
        for a in lTrueAngles:
            if a == iAimAngle:
                # print("move to %s",iAimAngle)
                car.move(iAoidAngle,150,5,5)
    # print(len(lTrueAngles))


def screen():
    clock.tick()
    img = image.Image(160,120,sensor.RGB565,copy_to_fb=True)
    getadc()
    img.draw_string(88,0,"Tof0:%f"% (iTof0),color=(0,255,0),scale=1)
    img.draw_string(88,8,"Tof1:%f"% (iTof1),color=(0,255,0),scale=1)
    img.draw_string(88,16,"Tof2:%f"% (iTof2),color=(0,255,0),scale=1)
    img.draw_string(88,24,"Tof3:%f"% (iTof3),color=(0,255,0),scale=1)
    # img.draw_string(88,32,"dhf:%4d"% (dhf),color=(0,255,0),scale=1)
    # img.draw_string(88,40,"dhb:%4d"% (dhb),color=(0,255,0),scale=1)
    # img.draw_string(88,48,"dhl:%4d"% (dhl),color=(0,255,0),scale=1)
    # img.draw_string(88,56,"dhr:%4d"% (dhr),color=(0,255,0),scale=1)
    # img.draw_string(88,64,"fx :%4d"% (fx),color=(255,0,0),scale=1)
    # img.draw_string(88,72,"fy :%4d"% (fy),color=(255,0,0),scale=1)
    # img.draw_string(88,80,"bx :%4d"% (bx),color=(255,0,0),scale=1)
    # img.draw_string(88,88,"by :%4d"% (by),color=(255,0,0),scale=1)
    img.draw_string(88,96,"but:%1d%1d%1d%1d"% (set_io.read(7,0),set_io.read(8,0),set_io.read(9,0),set_io.read(10,0),),color=(255,0,255),scale=1)
    img.draw_string(88,104,"cmp:%4d"% (compass.read()),color=(0,255,255),scale=1)
    img.draw_string(88,112,"BAT:%.1fV"% (set_adc.read(14)*11*3.3/1024),color=(255,255,0),scale=1)
    img.draw_string(0,112,"FR:%4dfps"% (clock.fps()),color=(0,0,255),scale=1)
    lcd.display(img)

while(key.read() == 0):
    screen()

while(True):
    car.turn(0,4,30,10,1)
    AvoidObt()
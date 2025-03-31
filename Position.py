from models import set_adc
from QkConf import QkJson

Cfg = QkJson()

def getDists(Num: int) -> list[int,int,int]:
    lDists = []
    for i in range(Num):
        # lDists.append(set_adc.read(i))
        lDists.append(
            int(set_adc.read(Cfg.read("Tofs",str(i)))*Cfg.read("Tofs","K")+Cfg.read("Tofs","B"))
            )
    return lDists

def GetPos() -> list[int,int]:
    Distance = getDists(4)
    if Distance[0]+Distance[2] < Cfg.read("Position","Height") - 100:
        if Distance[0] > Distance[2]:
            Y = Cfg.read("Position","Height")/2 - Distance[0]
        else:
            Y = Cfg.read("Position","Height")/2 - Distance[2]
    else:
        Y = ((Cfg.read("Position","Height")/2 - Distance[0]) + (Cfg.read("Position","Height")/2 - Distance[2]))/2
    if Distance[1]+Distance[3] < Cfg.read("Position","Width") - 100:
        if Distance[0] > Distance[2]:
            X = Cfg.read("Position","Width")/2 - Distance[1]
        else:
            X = Cfg.read("Position","Width")/2 - Distance[3]
    else:
        X = ((Cfg.read("Position","Width")/2 - Distance[1]) + (Cfg.read("Position","Width")/2 - Distance[3]))/2

    return [X,Y]
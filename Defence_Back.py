from kits import *

def DefenceBack():
    bY = AbsBallPos()[1]
    PeerY = Peerstatus()[3][1]
    lPos = GetPos()
    iY = lPos[1]
    if bY <= 0:
        if  iY > PeerY:
            DBackPos = [20, -85, 0]
        else:
            DBackPos = [-20, -85, 0]
    else:
        DBackPos = [0, -85, 0]
    Pos2Pos(DBackPos, False, 200)
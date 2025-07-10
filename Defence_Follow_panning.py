from kits import *
def FollowPPanning():
    lPos = GetPos()
    iX= lPos[0]
    PeerX = Peerstatus()[3][0]
    if abs(iX) <= 60:
        defend_x = PeerX*0.6   
        Pos2Pos([defend_x, -85, 0], False,200)
    else:
        Pos2Pos([0, -85, 0], False,200)

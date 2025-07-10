from kits import *
def FollowPPanning():
    lPos = GetPos()
    iX= lPos[0]
    bX,bY= AbsBallPos()
    PeerX = Peerstatus()[3][0]
    if [bX,bY] == [1024,1024]:
        defend_x = 0
    else:
        if abs(iX) <= 60:
            defend_x = PeerX*0.57   
        else:
            defend_x = 0
            Pos2Pos([defend_x, -85, 0], False,200)

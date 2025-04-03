from Level6 import GetPos, Pos2Pos

def Move2Path(iFacingAngle:int,Posistions:list[list[int,int],list[int,int]]):
    for i in Posistions:
        while (1):
            lLocalX = GetPos()[0]
            lLocalY = GetPos()[1]
            if 10 > (i[0]-lLocalX)+(i[1]-lLocalY) > -10:
                break
            else:
                Pos2Pos(iFacingAngle=iFacingAngle,Posistions=i)
        
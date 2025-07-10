
from kits import *
#Math Mod
###################################################################################################

def Defence(): #bX有部分最好是改为AX（敌方坐标）
    """
    DP防守逻辑
    1. 默认在己方半场，横向跟随球，保持在禁区外防守。
    2. 球过中线到对方半场，解除区域限制，积极争抢球权。
    3. 获得球权后 切换为OP。
    4. 球丢失或出界，回撤至防守点。
    5. 绝不与OP重叠在同一进攻区域。
    """
    peripheral.StopDribble()
    Role()
    lBallPos = AbsBallPos()
    lPos = GetPos()
    iX, iY = lPos[0], lPos[1]
    bX, bY = lBallPos[0], lBallPos[1]
    HOMEPOS = [0, -80, 0]
    if peer_role == "DP" and role == "DP":
        HOMEPOS = [-20, -80, 0]
    else:
        pass
    GOAL_POS = [0, 90]
    BLOCK_DIST = 50
    print(role,peer_role)
    if ball_owner == 0 or peer_role == None:  # 我方未检测到球权
        Pos2Pos(HOMEPOS, False,200)
        print(1)
        return
    if bY > 0 :  
        print(2)
        if ball_owner == SelfIP:
            return   #变成攻方
        elif ball_owner == peer_id:
            defend_x = - Peerstatus()[3][0]   # 横向适当跟随( 是跟随谁 不确定)
            defend_y = -40 + Peerstatus()[3][1] * 0.5  # 等比前移
            defend_y = max(-100, min(0, defend_y))
        else:#我方失去球权
            defend_x = bX * 0.8   
            defend_y = -40 + bY * 0.5  # 等比前移
            defend_y = max(-100, min(0, defend_y))
        Pos2Pos([defend_x, defend_y, 0], False,200)
    else:
        print(3)
        ball_to_goal_dist = math.sqrt((bX - GOAL_POS[0])**2 + (bY - GOAL_POS[1])**2)
        if ball_owner == SelfIP:
            return Offence()  #变成攻方
        elif ball_owner == peer_id:
            defend_x = - Peerstatus()[3][0]   # 各自站左右半场
            defend_y = -90
        else:
            if ball_to_goal_dist < BLOCK_DIST: #离球门很近
                defend_x = (bX - GOAL_POS[0])/ abs(bY - GOAL_POS[1]) * abs(iY - GOAL_POS[1]) #在球和球门连线上
                defend_y = -90 
            else:
                defend_x =  bX 
                defend_y = -90          
        Pos2Pos([defend_x, defend_y, 0], False)

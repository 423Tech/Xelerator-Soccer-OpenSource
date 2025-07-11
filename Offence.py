from kits import *

def NormalShoot():
    BX, BY = GetBallPos()
    logger.debug("Current Position: %s" % [BX, BY])
    if BX == 0 and BY == 0:
        logger.info("Ball not found, stopping chassis.")
        # Pos2Pos([0, -85, 0], False)
        chassis.stop()
        peripheral.Dribble(False)
    elif -5 < BX < 5 and 0 < BY < 10:
        logger.info("Ball is in front")
        # BX, BY = GetBallPos()
        # if not -5 < BX < 5 and 0 < BY < 10:
        #     break
        peripheral.Dribble(True)
        for _ in range(20):
            X,Y,_ = GetPos()
            DeltaY = cfg.read("Position","Height")/2 - Y
            DeltaX = X
            Theta = math.atan2(DeltaY, DeltaX)
            Theta = math.degrees(Theta)
            Aim = 90 - Theta
            Compass = compass()
            Delta = abs(Aim - Compass)
        # while True:
        #     chassis.GoZ(Compass)
            if Delta > 60:
                chassis.Turn(Aim,25)
                break
            else:
                chassis.GoA(Aim,0,100,0.8)
            
            time.sleep(0.03)
        
        peripheral.ShootBall()
    else:
        peripheral.Dribble(True)
        LockBallSlip()



while True:
    try:
        # Lockballslip()
        NormalShoot()
        print(GetBallPos())
        time.sleep(.03)
    except KeyboardInterrupt:
        print("Exiting...")
        chassis.stop()
        break
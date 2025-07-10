from kits import *

def NormalShoot():
    BX, BY = GetBallPos()
    logger.debug("Current Position: %s" % [BX, BY])
    if BX == 0 and BY == 0:
        logger.info("Ball not found, stopping chassis.")
        Pos2Pos([0, -85, 0], False)
        peripheral.Dribble(False)
    elif -5 < BX < 5 and 0 < BY < 10:
        logger.info("Ball is in front")
        for _ in range(20):
            BX, BY = GetBallPos()
            if not -5 < BX < 5 and 0 < BY < 10:
                break
            X,Y,_ = GetPos()
            DeltaY = 100 - Y
            DeltaX = X
            Theta = math.atan2(DeltaY, DeltaX)
            Theta = math.degrees(Theta)
            Compass = -(90 - Theta)
            # while True:
            #     chassis.GoZ(Compass)
            chassis.GoY(Compass,50)
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
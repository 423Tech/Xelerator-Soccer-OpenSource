def GoV(iFacingAngle,iAimAngle,iSpeed):
    iGlobalPIDK = 2
    iCMP = compass.read()
    iSpeedX = int(math.sin(math.radians(iAimAngle)) * iSpeed)
    iSpeedY = int(math.cos(math.radians(iAimAngle)) * iSpeed)

    iSpeedU = iSpeedX + iSpeedY
    iSpeedV = iSpeedY - iSpeedX
    iDeltaAngle = iCMP-iFacingAngle
    if iDeltaAngle > 180:
        iDeltaAngle = iDeltaAngle - 360
    set_motor.RPM(iSpeedU - iDeltaAngle * iGlobalPIDK,iSpeedV - iDeltaAngle * iGlobalPIDK,iSpeedV + iDeltaAngle * iGlobalPIDK,iSpeedU + iDeltaAngle * iGlobalPIDK)

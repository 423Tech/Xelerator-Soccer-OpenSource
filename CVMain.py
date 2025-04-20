import cv2
import numpy as np
import time
import multiprocessing as mp

lCamPorts = [0,2,6,4]
lCams = []

tGreenHSV = []
tOrangeLAB = (0, 255, 140, 190, 150, 190)
tOrangeHSV = (5, 15, 100, 255, 180, 255)
tBlueLAB = []
tYellowLAB = []

lSRCPoints = []
lDSTPoints = []

# aPerspectiveMatrix = cv2.getPerspectiveTransform(lSRCPoints,lDSTPoints)

def findBlobs(Frame, tThreshold, iFormat = 2, ROI = None, iMinPixelCount = 1):
    if iFormat == 1:
        Frame = cv2.cvtColor(Frame,cv2.COLOR_BGR2LAB)
    
    elif iFormat == 2:
        Frame = cv2.cvtColor(Frame,cv2.COLOR_BGR2HSV)

    lLowerThreshod = tThreshold[0], tThreshold[2], tThreshold[4]
    lUpperThreshold = tThreshold[1], tThreshold[3], tThreshold[5]
    
    
    
    Mask = cv2.inRange(Frame, np.array(lLowerThreshod), np.array(lUpperThreshold))
    
    # Kernel = np.ones((5, 5), np.uint8)
    # Mask = cv2.erode(Mask, Kernel, iterations=1)
    # Mask = cv2.dilate(Mask, Kernel, iterations=2)

    lConters, _ = cv2.findContours(Mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    lBlobs = []
    for oConter in lConters:
        iArea = cv2.contourArea(oConter)
        if iArea >= iMinPixelCount:
            iX, iY, iW, iH = cv2.boundingRect(oConter)
            iCX = int(iX + iW / 2) 
            iCY = int(iY + iH / 2)
            if ROI is not None and (iCX < ROI[0] or iCX > ROI[0] + ROI[2]) or (iCY < ROI[1] or iCY > ROI[1] + ROI[3]):
                continue
            lBlobs.append((iX, iY, iW, iH, iCX, iCY))
    return lBlobs


    



def imageResize(Frame, fScale=1, iXOffset=0, iYOffset=0):
    iOriginalHeight = Frame.shape[0]
    iOriginalWidth = Frame.shape[1]
    
    iResizedHeight = int(iOriginalHeight * fScale)
    iResizedWidth = int(iOriginalWidth * fScale)
    
    ResizedFrame = cv2.resize(Frame, (iResizedWidth, iResizedHeight))
    
    Canvas = np.zeros((iOriginalHeight, iOriginalWidth, 3), dtype=np.uint8)
    
    iResizedY = (iOriginalHeight - iResizedHeight) // 2
    iResizedX = (iOriginalWidth - iResizedWidth) // 2
    
    iStartY = max(0, iResizedY + iYOffset)
    iEndY = min(iOriginalHeight, iResizedY + iYOffset + iResizedHeight)
    
    iStartX = max(0, iResizedX + iXOffset)
    iEndX = min(iOriginalWidth, iResizedX + iXOffset + iResizedWidth)
    
    iFrameStartY = max(0, -iYOffset if iResizedY + iYOffset < 0 else 0)
    iFrameEndY = iResizedHeight - max(0, (iResizedY + iYOffset + iResizedHeight) - iOriginalHeight)
    
    iFrameStartX = max(0, -iXOffset if iResizedX + iXOffset < 0 else 0)
    iFrameEndX = iResizedWidth - max(0, (iResizedX + iXOffset + iResizedWidth) - iOriginalWidth)
    
    Canvas[iStartY:iEndY, iStartX:iEndX] = ResizedFrame[iFrameStartY:iFrameEndY, iFrameStartX:iFrameEndX]
    
    return Canvas

def imageCrop(Frame, lPoints, bBlackSide=False):
    Mask = np.zeros(Frame.shape[:2], dtype=np.uint8)
    aPoints = np.array(lPoints)
    cv2.fillPoly(Mask, [aPoints], (255))
    
    Result = cv2.bitwise_and(Frame, Frame, mask=Mask)
    
    if not bBlackSide:
        iX, iY, iW, iH = cv2.boundingRect(aPoints)
        Result = Result[iY:iY+iH, iX:iX+iW]
    
    return Result

def camInit(lCamPorts=lCamPorts, iWidth=320, iHeight=240, iAutoExposure=1, iBrightness=0, iContrast=32, iSaturation=64):
    lCams = []
    lAvailablePorts = []
    for iPort in lCamPorts:
        oCam = cv2.VideoCapture(iPort)
        if oCam.isOpened():
            oCam.set(cv2.CAP_PROP_FRAME_WIDTH, iWidth)
            oCam.set(cv2.CAP_PROP_FRAME_HEIGHT, iHeight)
            oCam.set(cv2.CAP_PROP_AUTO_EXPOSURE, iAutoExposure)
            oCam.set(cv2.CAP_PROP_BRIGHTNESS, iBrightness)
            oCam.set(cv2.CAP_PROP_CONTRAST, iContrast)
            oCam.set(cv2.CAP_PROP_SATURATION, iSaturation)
            lCams.append(oCam)
            lAvailablePorts.append(iPort)
        else:
            print(f"Failed to open camera at port {iPort}")
    print(f"Available cameras at ports: {lAvailablePorts}")
    return lCams

def findMaxBlob(lBlobs):
    iMaxSize=0
    for oBlob in lBlobs:
        if oBlob[2]*oBlob[3] > iMaxSize:
            oMaxBlob=oBlob
            iMaxSize = oBlob[2] * oBlob[3]
    return oMaxBlob


def readCam(lCams, iCam = None, fScale = 1, iXOffset = 0, iYOffset = 0):
    lFrames = []
    if iCam == None:
        for oCam in lCams:
            Status,Frame = oCam.read()
            # Frame = imageResize(Frame,fScale,iXOffset,iYOffset)
            # print(Status)
            lFrames.append(Frame)
        return lFrames
    else:
        _,Frame = lCams[iCam].read()
        Frame = imageResize(Frame,fScale,iXOffset,iYOffset)
        return Frame

def findBlobProcess(lCam, iCam, tThreshold, ROI, iBX, iBY, iXOffset=0, iYOffset=0):
    global t0
    while(1):
        # print(1)
        Frame = readCam(lCams,iCam)
        lBlobs = findBlobs(Frame,tThreshold=tThreshold,ROI = ROI)
        if lBlobs:
            oMaxBlob = findMaxBlob(lBlobs)
            cv2.circle(Frame, (oMaxBlob[4], oMaxBlob[5]), 2, (0,255,0), 2)
            iBX.value = oMaxBlob[4]
            iBY.value = oMaxBlob[5]
        else:
            iBX.value = 0
            iBY.value = 0
        # cv2.putText(Frame, f"FPS: {1.0/(time.time()-t0):.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2); t0 = time.time()
        # if iCam == 2:
        #     cv2.imshow('Camera' + str(iCam), Frame)
        #     key = cv2.waitKey(1) & 0xFF
        #     if key == ord('q'):
        #         break
        time.sleep(0.01)

def integrateBallPos(oFrontBallX,oFrontBallY,oRightBallX,oRightBallY,oBackBallX,oBackBallY,oLeftBallX,oLeftBallY,oIX,oIY):
    while(1):
        if oFrontBallY.value != 0:
            iX = oFrontBallX.value - 320
            iY = 480 - oFrontBallY.value
        elif oRightBallY.value != 0:
            iY = -(oRightBallX.value - 320)
            iX = 480 - oRightBallY.value
        elif oBackBallY.value != 0:
            iX = -(oBackBallX.value - 320)
            iY = -(480 - oBackBallY.value)
        elif oLeftBallY.value != 0:
            iY = oLeftBallX.value - 320
            iX = -(480 - oLeftBallY.value)
        else:
            iX = 0
            iY = 0
        
        oIX.value = iX
        oIY.value = iY

        time.sleep(0.1)


        




lCams = camInit(iWidth=640, iHeight=480)

t0 = time.time()

oFrontBallX = mp.Value('i',0)
oFrontBallY = mp.Value('i',0)
oRightBallX = mp.Value('i',0)
oRightBallY = mp.Value('i',0)
oBackBallX = mp.Value('i',0)
oBackBallY = mp.Value('i',0)
oLeftBallX = mp.Value('i',0)
oLeftBallY = mp.Value('i',0)
oIX = mp.Value('i',0)
oIY = mp.Value('i',0)


oFrontFindBlobProcess = mp.Process(target = findBlobProcess,args=(lCams,0,tOrangeHSV,(95,0,450,480),oFrontBallX,oFrontBallY,0,0))
oFrontFindBlobProcess.start()
oRightFindBlobProcess = mp.Process(target = findBlobProcess,args=(lCams,1,tOrangeHSV,(95,0,450,480),oRightBallX,oRightBallY,0,14))
oRightFindBlobProcess.start()
oBackFindBlobProcess = mp.Process(target = findBlobProcess,args=(lCams,2,tOrangeHSV,(95,0,450,480),oBackBallX,oBackBallY,0,0))
oBackFindBlobProcess.start()
oRightFindBlobProcess = mp.Process(target = findBlobProcess,args=(lCams,3,tOrangeHSV,(95,0,450,480),oLeftBallX,oLeftBallY,0,14))
oRightFindBlobProcess.start()
oIntegrateBallPosProcess = mp.Process(target = integrateBallPos,args=(oFrontBallX,oFrontBallY,oRightBallX,oRightBallY,oBackBallX,oBackBallY,oLeftBallX,oLeftBallY,oIX,oIY))
oIntegrateBallPosProcess.start()



while(1):
    time.sleep(0.01)
    print(oIX.value,oIY.value)


while(1):
    Frame = readCam(lCams,0)


    # iCropWidth = 95
    # lFrames[0] = imageCrop(lFrames[0],[(iCropWidth,0),(iCropWidth,480),(640-iCropWidth,480),(640-iCropWidth,0)])
    # lFrames[1] = imageCrop(lFrames[1],[(iCropWidth,0),(iCropWidth,480),(640-iCropWidth,480),(640-iCropWidth,0)])
    # lFrames[3] = imageCrop(lFrames[3],[(iCropWidth,0),(iCropWidth,480),(640-iCropWidth,480),(640-iCropWidth,0)])

    # Frame = imageResize(lFrames[0],fScale = 0.8)

    # lFrames[1] = imageResize(lFrames[1],fScale = 1,iYOffset=14)
    # lFrames[3] = imageResize(lFrames[3],fScale = 1,iYOffset=14)

    # lRightBlobs = findBlobs(lFrames[1],tThreshold=tOrangeLAB)
    lFrontBlobs = findBlobs(Frame,tOrangeHSV,ROI = (95,0,450,480))

    if lFrontBlobs:
        oMaxBlob = findMaxBlob(lFrontBlobs)
        print(oMaxBlob[4]-320,480-oMaxBlob[5])
        cv2.circle(Frame, (oMaxBlob[4], oMaxBlob[5]), 2, (0,255,0), 2)


    # for oBlob in lFrontBlobs:
    #     cv2.circle(Frame, (oBlob[4], oBlob[5]), 2, (0,255,0), 2)
        
    # Frame = imageCrop(Frame,[(0,0),(0,160),(320,480),(640,180),(640,0)])

    # Frame = imageResize(cv2.hconcat([lFrames[0],lFrames[1]]),0.6)
    # LowerFrame = cv2.hconcat([lFrames[2],lFrames[3]])
    # Frame  = cv2.vconcat([UpperFrame,LowerFrame])
    # print(lBlobs)
    # cv2.putText(lFrames[1], f"FPS: {1.0/(time.time()-t0):.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2); t0 = time.time()
    cv2.putText(Frame, f"FPS: {1.0/(time.time()-t0):.1f}", (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0,255,0), 2); t0 = time.time()
    # cv2.imshow('Right', lFrames[1])
    cv2.imshow('Front', Frame)
    # cv2.imshow('Right', lFrames[1])
    # cv2.imshow('Left', lFrames[3])
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break


cv2.destroyAllWindows()
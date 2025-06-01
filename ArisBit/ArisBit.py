# ArisBit v1.0 By XiaoliMEMZ
# 邦邦咔邦！(＠＾◡＾)

from Rosmaster_Lib import Rosmaster
import time
import multiprocessing
import threading

oBot = Rosmaster()
oBot.create_receive_threading()

bCompassReset = False
iCompass = 0

lPulsePerSecond = [0,0,0,0]
lAimPulsePerSecond = [0,0,0,0]
bAimPulsePerSecondChange = False


class AdaptiveEMAFilter:
    def __init__(self):
        self.ema_value = None
        self.alpha_normal = 0.2    # 正常平滑系数
        self.alpha_fast = 0.7      # 快速响应系数
        self.change_threshold = 0.4
        
    def update(self, measurement):
        if self.ema_value is None:
            self.ema_value = measurement
            return measurement
        
        # 检测变化幅度
        change_ratio = abs(measurement - self.ema_value) / max(abs(self.ema_value), 1)
        
        # 自适应调整alpha
        if change_ratio > self.change_threshold or (abs(measurement) < 50 and abs(self.ema_value) > 300):
            alpha = self.alpha_fast  # 快速响应
        else:
            alpha = self.alpha_normal  # 正常平滑
        
        # EMA计算
        self.ema_value = alpha * measurement + (1 - alpha) * self.ema_value
        return self.ema_value

def CompassProcessing():
    global bCompassReset, iCompass
    iOffset = 0
    while(1):
        iRawCompass = (360 - int(oBot.get_imu_attitude_data()[2])) % 360  # 获取原始指南针角度
        if bCompassReset:
            iOffset = iRawCompass
            bCompassReset = False
            # print("Compass reset to: ", iOffset)
        iCompass = iRawCompass - iOffset
        iCompass = iCompass % 360  # 保持在 0~360 度之间
        time.sleep(0.04)

def ResetCompass():
    global bCompassReset
    bCompassReset = True

def GetCompass():
    global iCompass
    return iCompass

def MotorEncoderProcessing():
    global lPulsePerSecond
    lKalmanFilter = [AdaptiveEMAFilter() for _ in range(4)]
    while True:
        lBeforePulse = list(oBot.get_motor_encoder())
        fStartTime = time.time()
        while (abs(oBot.get_motor_encoder()[0] - lBeforePulse[0]) < 10 and
               abs(oBot.get_motor_encoder()[1] - lBeforePulse[1]) < 10 and
               abs(oBot.get_motor_encoder()[2] - lBeforePulse[2]) < 10 and
               abs(oBot.get_motor_encoder()[3] - lBeforePulse[3]) < 10):
            fDuration = time.time() - fStartTime
            if fDuration > 0.05:
                # print(1)
                break
            time.sleep(0.001)  # 等待一段时间，避免CPU占用过高
        if fDuration < 0.001:
            continue
        lAfterPulse = list(oBot.get_motor_encoder())
        lDeltaPulse = [lAfterPulse[i] - lBeforePulse[i] for i in range(4)]
        for i in range(4):
            if abs(lDeltaPulse[i]) < 10:
                lDeltaPulse[i] = 0
            iPulsePerSecond = lDeltaPulse[i] / fDuration
            lPulsePerSecond[i] = int(lKalmanFilter[i].update(iPulsePerSecond))

def GetMotorEncoder():
    global lPulsePerSecond
    return lPulsePerSecond

def MotorPIDProcessing():
    global lPulsePerSecond, lAimPulsePerSecond, bAimPulsePerSecondChange
    lCurrentPWM = [0, 0, 0, 0]
    # lAimPWM = [0, 0, 0, 0]
    while True:
        if lAimPulsePerSecond == [0, 0, 0, 0]:
            oBot.set_motor(0, 0, 0, 0)
            continue
        if bAimPulsePerSecondChange:
            for i in range(4):
                lCurrentPWM[i] = int(0.006 * lAimPulsePerSecond[i])
                if lAimPulsePerSecond[i] > 0:
                    lCurrentPWM[i] += 20
                elif lAimPulsePerSecond[i] < 0:
                    lCurrentPWM[i] -= 20
            oBot.set_motor(*lCurrentPWM)
            bAimPulsePerSecondChange = False
            time.sleep(0.3)
            continue
        for i in range(4):
            iCurrentPulsePerSecond = lPulsePerSecond[i]
            iDeltaPulsePerSecond = lAimPulsePerSecond[i] - iCurrentPulsePerSecond
            iDeltaPWM = 0.001 * iDeltaPulsePerSecond  # 调整PWM变化率
            lCurrentPWM[i] += iDeltaPWM  # 调整PWM
        oBot.set_motor(int(lCurrentPWM[0]), int(lCurrentPWM[1]), int(lCurrentPWM[2]), int(lCurrentPWM[3]))
        time.sleep(0.04)  # 控制循环频率

def SetMotorPPS(iPPS1,iPPS2,iPPS3,iPPS4):
    global lAimPulsePerSecond, bAimPulsePerSecondChange
    lAimPulsePerSecond = [iPPS1, iPPS2, iPPS3, iPPS4]
    bAimPulsePerSecondChange = True

    

oCompassThread = threading.Thread(target=CompassProcessing)
oCompassThread.daemon = True  # 设置为守护线程
oCompassThread.start()

oMotorEncoderThread = threading.Thread(target=MotorEncoderProcessing)
oMotorEncoderThread.daemon = True  # 设置为守护线程
oMotorEncoderThread.start()

oMotorPIDThread = threading.Thread(target=MotorPIDProcessing)
oMotorPIDThread.daemon = True  # 设置为守护线程
oMotorPIDThread.start()








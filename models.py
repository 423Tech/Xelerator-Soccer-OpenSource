import random

class set_led:
    def out(self, t_ch:int , t_mode:int) -> None:
        '''
        t_ch = 1~3
        t_mode = 0/1
        '''


class beep:
    def set(self, state:int) -> None:
        '''
        state (0,1)
        '''
    def frequency(self, arr:int) -> None:
        '''
        arr (0,100000)
        '''

class set_io:
    def out(self, ch:int, mode:int) -> None:
        '''
        ch (1,12)
        mode (0,1)
        '''

    def read(self, ch:int) -> None:
        '''
        ch (1,12)
        '''

class set_adc:
    def read(ch:int) -> int:
        '''
        ch (1,12)
        return (1,1023)
        '''
        output = random.randint(0, 1023)
        return output
    
class time:
    def start(self, ch:int) -> None:
        '''
        ch (1,10)
        开始计时
        '''

    def read(self, ch:int) -> int:
        '''
        ch (1,10)
        查询计数
        '''
        return ch

    def pause(self, ch:int) -> None:
        '''
        ch (1,10)
        暂停计时
        '''

    def clear(self, ch:int) -> None:
        '''
        ch (1,10)
        '''

class delay:
    def us(self, time:int) -> None:
        '''
        ch (1,65536)
        延时微秒
        '''

    def ms(self, time:int) -> None:
        '''
        ch (1,65535)
        延时毫秒
        '''
    
    def s(self, time:int) -> None:
        '''
        ch (1,65535)
        延时秒
        '''

class set_servo:
    def angle(self, ch:int, angle:int) -> None:
        '''
        ch (11,12)
        angle (0,180)
        设置舵机转动的目标角度
        '''

class key:
    def read() -> int:
        '''
        retrun (0,1)
        '''
        return 0

class compass:
    def read() -> int:
        '''
        retrun (0,359)
        '''
        return 0

class set_motor:
    def out(self, ch:int, speed:int) -> None:
        '''
        ch (1,4)
        speed (-1000,1000)
        '''

    def RPM(self, motor1Speed:int, motor0Speed:int, motor3Speed:int, motor2Speed:int) -> None:
        '''
        motor1 -> / \ <- motor0
        motor2 -> \ / <- motor3
        '''
        
class car:
    def straight(self, aim_angle:int, speed:int, fix_k:int, fix_b:int) -> None:
        '''
        aim_angle (0,359)
        speed (450,800)
        fix_k (2,10) #比例
        fix_b (10,60) #常数
        ! 在while(1)中使用
        '''

    def turn(self, aim_angle:int, fix_k:int, fix_b:int, angle_range:int, keep_time:int) -> None:
        '''
        aim_angle (0,359)
        fix_k (2,10) #比例
        fix_b (10,60) #常数
        angle_range (1,5)
        keep_time (50,200)

        ! 函数进行的转向为强制转向，如果转向未完成，将会一直停在这里，不会执行下一条语句。
        '''

    def cross(self, aim_angle:int, speed:int, fix_k:int, fix_b:int) -> None:
        '''
        aim_angle (0,359)
        speed (600,900)
        fix_k (2,10) #比例
        fix_b (10,60) #常数
        keep_time (50,200)
        '''
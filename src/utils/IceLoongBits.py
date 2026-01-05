
import struct
import time
from typing import Optional, Tuple, List

from loguru import logger
from pathlib import Path
Date = time.strftime("%Y%m", time.localtime())
APP_DIR = Path(__file__).parent
LOG_FILE = APP_DIR / f"{Date}_IceLoong.log"
logger.add(LOG_FILE)


try:
    import serial
except Exception:  # pragma: no cover - import error handled at runtime
    serial = None

class IceLoongBits:
    """串口通信封装类，用于与 F407（STM32）类设备交互。
    方法命名使用大驼峰（PascalCase）。
    """

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 921600, timeout: float = 0.02):
        """初始化串口参数（不自动打开）。

        Args:
            port: 串口设备路径，例如 "/dev/ttyUSB0" 或 "COM3"。
            baudrate: 波特率，例如 115200。
            timeout: 读超时（秒）。
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.Yaw =  0.0
        # 串口句柄（运行时为 serial.Serial 实例），这里不在类型注解中引用 serial 变量以避免 lint 问题
        self.ser = None
        self.logger = logger

    def OpenPort(self) -> None:
        """打开串口（如果尚未打开）。"""
        if serial is None:
            raise RuntimeError("pyserial 未安装，请运行: pip install pyserial")
        if self.ser and getattr(self.ser, "is_open", False):
            # self.logger.info("串口已打开: %s", self.port)
            return
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        # self.logger.info("已打开串口 %s @ %d", self.port, self.baudrate)

    def ClosePort(self) -> None:
        """关闭串口并释放句柄。"""
        if self.ser:
            try:
                self.ser.close()
                self.logger.success("已关闭串口 %s", self.port)
            except Exception as e:
                self.logger.error("关闭串口失败: %s", e)
            finally:
                self.ser = None

    def _ReadUntilTimeout(self) -> bytes:
        """辅助：读取直到超时（按字节读取）。"""
        buf = bytearray()
        while True:
            b = self.ser.read(1)
            if not b:
                break
            buf.extend(b)
        return bytes(buf)

    def SendCommand(self, data: bytes, read_response: bool = False, response_length: int = 0, response_timeout: Optional[float] = None) -> bytes:
        """发送原始字节命令到 F407。

        Args:
            data: 需要发送的原始字节数据。
            read_response: 是否在发送后立即读取响应。
            response_length: 如果大于 0，按长度读取；否则读取直到超时。
            response_timeout: 单次读取的临时超时（秒），若 None 则使用初始化的 timeout。

        Returns:
            bytes: 读取到的响应（如果 read_response=False 返回 b''）。
        """
        if serial is None:
            raise RuntimeError("pyserial 未安装，请运行: pip install pyserial")
        if not self.ser or not getattr(self.ser, "is_open", False):
            self.OpenPort()

        # 清空输入缓冲，避免读到旧数据
        try:
            self.ser.reset_input_buffer()
        except Exception:
            # 有些 serial 实现可能没有该方法
            pass
        data.hex()
        # self.logger.info("发送: "+)
        self.ser.write(data)
        time.sleep(0.001)
        self.ser.flush()

        if not read_response:
            return b""

        # 暂时调整 timeout（若提供），发送后立即读取
        old_timeout = getattr(self.ser, "timeout", None)
        if response_timeout is not None:
            self.ser.timeout = response_timeout

        try:
            if response_length > 0:
                resp = self.ser.read(response_length)
            else:
                # 读取直到超时
                resp = self._ReadUntilTimeout()
            resp.hex()
            # self.logger.info("接收: "+)
            return resp
        finally:
            if response_timeout is not None:
                self.ser.timeout = old_timeout

    def SendHexCommand(self, hexstr: str, read_response: bool = False, response_length: int = 0, response_timeout: Optional[float] = None) -> bytes:
        """便捷方法：从十六进制字符串发送命令，如 'AA0101AB'。"""
        data = bytes.fromhex(hexstr)
        return self.SendCommand(data, read_response=read_response, response_length=response_length, response_timeout=response_timeout)

    def HandShake(self) -> Tuple[bool, str]:
        """与下位机握手，确认下位机状态。
        
        发送: 0x01
        接收: 0x81 + 状态字节(0x00:空闲, 0x01:忙)
        
        Returns:
            Tuple[bool, str]: (握手成功, 状态描述)
        """
        # 发送握手命令0x01，等待2字节响应
        resp = self.SendHexCommand("01", read_response=True, response_length=2, response_timeout=0.1)
        
        if len(resp) < 2:
            self.logger.error("握手响应长度不足，期望2字节，实际收到"+ len(resp) +"字节")
            return False, "响应长度不足"
        
        # 检查响应头
        if resp[0] != 0x81:
            self.logger.error("握手响应头错误，期望0x81，实际收到0x%02x", resp[0])
            return False, f"响应头错误: 0x{resp[0]:02x}"
        
        # 检查状态字节
        status = resp[1]
        if status == 0x00:
            self.logger("下位机状态: 空闲")
            return True, "空闲"
        elif status == 0x01:
            self.logger("下位机状态: 忙")
            return True, "忙"
        else:
            self.logger.warning("未知状态字节: 0x%02x", status)
            return True, f"未知状态: 0x{status:02x}"

    def GetYaw(self):
        # self.logger.info("获取航向: "+ str(self.Yaw))
        return self.Yaw

    def UpdateYaw(self):
        """向 F407 请求航向（Yaw），并解析为 float 和时间戳。

        发送: 0x02
        接收: 0x82 + 3个float(小端) + 1个uint32_t(小端)

        Returns:
            Tuple[float, int]: (yaw值, 时间戳)
        """
        # 总共17字节: 1字节头 + 3*4字节float + 4字节uint32
        resp_len = 1 + (3 * 4) + 4
        resp = self.SendHexCommand("02", read_response=True,
                                  response_length=resp_len,
                                  response_timeout=0.01)  # 10ms超时

        # 检查响应长度
        if len(resp) < resp_len:
            self.logger.warning("响应长度不足，期望"+ resp_len + "字节，实际收到"+ len(resp) +"字节")
            self.Yaw =  0.0

        # 检查响应头
        if resp[0] != 0x82:
            self.logger.warning("响应头错误，期望0x82，实际收到0x%02x", resp[0])
            self.Yaw =  0.0

        try:
            # 解析数据部分（跳过第一个字节的响应头）
            # 数据格式: 3个float + 1个uint32，都是小端
            data_part = resp[1:]  # 跳过0x82头

            # 确保数据部分长度足够
            if len(data_part) < 16:
                self.logger.error("数据部分长度不足，期望16字节，实际"+ len(data_part) + "字节")
                self.Yaw =  0.0

            # 解析所有数据
            # <fffI: 3个float + 1个unsigned int，都是小端
            float1, float2, float3, timestamp = struct.unpack('<fffI', data_part)

            # 记录调试信息
            # self.logger.info("解析到数据: float1=%f, float2=%f, yaw=%f, timestamp=%u", 
            #                   float1, float2, float3, timestamp)

            # 返回第三个float（yaw）和时间戳
            self.Yaw = float3 % 360

        except struct.error as e:
            self.logger.error("解析数据失败: %s，原始数据: %s", e, resp.hex())
            self.Yaw =  0.0

    def SetWheelSpeed(self, speeds1,speeds2,speeds3,speeds4) -> None:
        """设置四个轮子的转速。
        
        发送: 0x03 + 4个float(小端)
        不需要等待回复。
        
        Args:
            speeds: 包含4个浮点数的列表，分别对应四个轮子的转速(rpm)
        
        earaises:
            ValueError: 如果输入不是4个浮点数
        """
        speeds = [speeds1,speeds2,-speeds3,-speeds4]
        if len(speeds) != 4:
            raise ValueError(f"需要4个轮子的速度，但收到了{len(speeds)}个")
        
        # 将速度值转换为float类型（确保是浮点数）
        try:
            speed_values = [float(speed) for speed in speeds]
        except (ValueError, TypeError) as e:
            raise ValueError("速度值必须是数字类型") from e
        
        # 构建数据包: 0x03 + 4个float(小端)
        # 使用struct.pack打包4个浮点数，格式为'<ffff'表示4个小端浮点数
        data_bytes = struct.pack('<ffff', *speed_values)
        
        # 添加命令头0x03
        full_data = b'\x03' + data_bytes
        
        # 发送数据，不等待回复
        self.SendHexCommand(full_data.hex(), read_response=False)
        
        # 记录调试信息
        # self.logger.info("设置轮子转速: "+ str(speed_values[0]) +' ' + str(speed_values[1]) + ' '+ str(speed_values[2]) + ' ' + str(speed_values[3]))
        self.UpdateYaw()

    def Kick(self):
        """弹射踢球
        
        发送: 0x04
        不需要等待回复。
        """
        # 发送握手命令0x04，
        resp = self.SendHexCommand("04", read_response=False)
        
    def SetIO(self,port,status):
        """设置IO口状态

        Args:
            port: IO口编号
            status: IO口状态
        """
        if port == 3:
            if status == 1:
                pass
            else:
                self.Kick()


    def __enter__(self):
        self.OpenPort()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.ClosePort()



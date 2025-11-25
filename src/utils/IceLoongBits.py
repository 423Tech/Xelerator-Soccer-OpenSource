
import logging
import struct
import time
from typing import Optional

try:
    import serial
except Exception:  # pragma: no cover - import error handled at runtime
    serial = None


class IceLoongBits:
    """串口通信封装类，用于与 F103（STM32）类设备交互。

    说明与假设：
    - 本类负责打开/关闭串口、发送原始字节命令并读取响应。
    - 因为没有收到“表格中 f103”的具体协议，这里提供通用的 SendCommand/ReadResponse
      方法，和两个示例便捷方法 GetYaw / SetIO。
    - 示例方法内部使用的命令（YAW_CMD、SetIO 命令构造）为占位符，请根据你的表格把命令字节替换为真实值。

    方法命名使用大驼峰（PascalCase）。
    """

    def __init__(self, port: str = "/dev/ttyUSB0", baudrate: int = 115200, timeout: float = 0.02):
        """初始化串口参数（不自动打开）。

        Args:
            port: 串口设备路径，例如 "/dev/ttyUSB0" 或 "COM3"。
            baudrate: 波特率，例如 115200。
            timeout: 读超时（秒）。
        """
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        # 串口句柄（运行时为 serial.Serial 实例），这里不在类型注解中引用 serial 变量以避免 lint 问题
        self.ser = None
        self.logger = logging.getLogger(self.__class__.__name__)
        if not self.logger.handlers:
            # 避免多次添加 handler
            self.logger.addHandler(logging.NullHandler())

    def OpenPort(self) -> None:
        """打开串口（如果尚未打开）。"""
        if serial is None:
            raise RuntimeError("pyserial 未安装，请运行: pip install pyserial")
        if self.ser and getattr(self.ser, "is_open", False):
            self.logger.debug("串口已打开: %s", self.port)
            return
        self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
        self.logger.debug("已打开串口 %s @ %d", self.port, self.baudrate)

    def ClosePort(self) -> None:
        """关闭串口并释放句柄。"""
        if self.ser:
            try:
                self.ser.close()
                self.logger.debug("已关闭串口 %s", self.port)
            except Exception as e:
                self.logger.exception("关闭串口失败: %s", e)
            finally:
                self.ser = None

    def SendCommand(self, data: bytes, read_response: bool = False, response_length: int = 0, response_timeout: Optional[float] = None) -> bytes:
        """发送原始字节命令到 F103。

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

        self.logger.debug("发送: %s", data.hex())
        self.ser.write(data)
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
            self.logger.debug("接收: %s", resp.hex())
            return resp
        finally:
            if response_timeout is not None:
                self.ser.timeout = old_timeout

    def _ReadUntilTimeout(self) -> bytes:
        """辅助：读取直到超时（按字节读取）。"""
        buf = bytearray()
        while True:
            b = self.ser.read(1)
            if not b:
                break
            buf.extend(b)
        return bytes(buf)

    def ReadResponse(self, length: int = 0, timeout: Optional[float] = None) -> bytes:
        """显式读取响应数据（可在外部调用用于主动读取）。

        Args:
            length: 希望读取的字节数；0 表示读取直到超时。
            timeout: 临时超时（秒），None 则使用初始化值。
        """
        if not self.ser or not getattr(self.ser, "is_open", False):
            self.OpenPort()

        old_timeout = getattr(self.ser, "timeout", None)
        if timeout is not None:
            self.ser.timeout = timeout
        try:
            if length > 0:
                return self.ser.read(length)
            return self._ReadUntilTimeout()
        finally:
            if timeout is not None:
                self.ser.timeout = old_timeout

    def GetYaw(self) -> float:
        """示例方法：向 F103 请求航向（Yaw），并解析为 float。

        注意：这里使用的是占位命令与解析方式，必须根据你的表格协议替换：
        - YAW_CMD: 用表中给出的请求原始字节替换
        - 响应解析：当前假设返回 4 字节 little-endian float（IEEE754 单精度）
        """
        # 占位请求命令（请替换为表中的真实命令）

        # YAW_CMD = bytes.fromhex("AA0101AB")
        # resp = self.SendCommand(YAW_CMD, read_response=True, response_length=4, response_timeout=0.2)
        # if len(resp) >= 4:
        #     try:
        #         yaw = struct.unpack("<f", resp[:4])[0]
        #         return float(yaw)
        #     except Exception:
        #         self.logger.exception("解析 yaw 响应失败: %s", resp.hex())
        return 0.0

    def SetIO(self, io_state: int) -> bool:
        """示例方法：设置 IO 输出状态。

        Args:
            io_state: 整数状态（按协议定义，例如 0/1 或位掩码）。

        返回:
            bool: 如果收到非空响应则认为成功（根据需要可改为检查特定 ACK）。

        注意：以下命令构造为示例（0xAA 0x02 <state> <checksum>），请根据表格协议替换。
        """
        # 构造示例命令：头(0xAA) + 命令码(0x02) + 状态字节 + 校验

        # prefix = b"\xAA\x02" + bytes([io_state & 0xFF])
        # checksum = sum(prefix) & 0xFF
        # cmd = prefix + bytes([checksum])
        # resp = self.SendCommand(cmd, read_response=True, response_length=1, response_timeout=0.2)
        # return len(resp) > 0

    def SendHexCommand(self, hexstr: str, read_response: bool = False, response_length: int = 0, response_timeout: Optional[float] = None) -> bytes:
        """便捷方法：从十六进制字符串发送命令，如 'AA0101AB'。"""
        data = bytes.fromhex(hexstr)
        return self.SendCommand(data, read_response=read_response, response_length=response_length, response_timeout=response_timeout)

    # ------------------------- 表格协议高层封装 (F103) -------------------------
    H750_ADDR = 0x01
    F103_ADDR = 0x02
    FRAME_HEAD = bytes.fromhex("5599")
    FRAME_TAIL = bytes.fromhex("AACC")

    def _ToU16BE(self, v: int) -> bytes:
        return v.to_bytes(2, byteorder="big", signed=False)

    def _ToU32BE(self, v: int) -> bytes:
        return v.to_bytes(4, byteorder="big", signed=False)

    def _BuildFrame(self, target_addr: int, func: int, data: bytes) -> bytes:
        """根据协议构造帧：头(0x5599) + 目标地址 + 功能码 + 数据长度 + 数据 + 尾(0xAACC)。"""
        if not (2 <= len(data) <= 128):
            # 协议要求数据长度在 2~128，但某些命令表格显示长度可为1或0，允许特殊处理
            # 这里不强制，仍允许0~128长度
            pass
        frame = bytearray()
        frame.extend(self.FRAME_HEAD)
        frame.append(target_addr & 0xFF)
        frame.append(func & 0xFF)
        frame.append(len(data) & 0xFF)
        frame.extend(data)
        frame.extend(self.FRAME_TAIL)
        return bytes(frame)

    def SendFrame(self, func: int, data: bytes, target_addr: int = F103_ADDR, read_response: bool = False, response_length: int = 0, response_timeout: Optional[float] = None) -> bytes:
        """构造并发送一条帧给目标地址（默认 F103）。"""
        frame = self._BuildFrame(target_addr, func, data)
        return self.SendCommand(frame, read_response=read_response, response_length=response_length, response_timeout=response_timeout)

    # ------------------------- 常用命令封装（按表格） -------------------------
    def SetMotorPidSingle(self, motor_index: int, p: float = None, i: float = None, d: float = None) -> bool:
        """单独设置 1~4 号电机的速度 PID 参数（传入其中一个或多个），数值按 *1000 后以 u16(大端) 发送。

        motor_index: 1~4
        p,i,d: 浮点数，范围 0~60
        根据功能码：P=0x01, I=0x03, D=0x04（表格里的码位）
        返回 True 表示发送成功（收到非空响应）。
        """
        if not (1 <= motor_index <= 4):
            raise ValueError("motor_index must be 1..4")
        # motor index could be encoded in data or command context; 表格没有明确索引字节位置，假设数据直接为参数值
        success = True
        base_funcs = {"p": 0x01, "i": 0x03, "d": 0x04}
        for name, val in (("p", p), ("i", i), ("d", d)):
            if val is None:
                continue
            ival = int(round(val * 1000))
            data = self._ToU16BE(ival)
            # 如果需要指定电机编号放入数据，请修改这里；现在发送参数仅为两个字节（表格示例）
            resp = self.SendFrame(base_funcs[name], data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
            if len(resp) == 0:
                success = False
        return success

    def SetPwmFour(self, pwm_list: list[int]) -> bool:
        """一次性设置 4 个电机的 PWM，输入范围 -1000~1000，发送时需 +10000，按 u16(大端) 发送，功能码 0x05。"""
        if len(pwm_list) != 4:
            raise ValueError("pwm_list must have 4 elements")
        data = bytearray()
        for v in pwm_list:
            iv = int(v) + 10000
            data.extend(self._ToU16BE(iv))
        resp = self.SendFrame(0x05, bytes(data), target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def SetUniformSpeedPid(self, p: float, i: float, d: float) -> bool:
        """统一设置 4 个电机的速度 PID（功能码 0x06），每个参数按 *1000 发送为 u16。"""
        data = bytearray()
        for val in (p, i, d):
            data.extend(self._ToU16BE(int(round(val * 1000))))
        resp = self.SendFrame(0x06, bytes(data), target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def SetRpmFour(self, rpm_list: list[int]) -> bool:
        """一次性设置 4 个电机的转速，输入范围 -1000~1000，发送时 +10000，功能码 0x07。"""
        if len(rpm_list) != 4:
            raise ValueError("rpm_list must have 4 elements")
        data = bytearray()
        for v in rpm_list:
            iv = int(v) + 10000
            data.extend(self._ToU16BE(iv))
        resp = self.SendFrame(0x07, bytes(data), target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def SetPolePairs(self, pairs: int) -> bool:
        """设置编码器磁环极对数（功能码 0x08），2 字节 u16。"""
        data = self._ToU16BE(int(pairs))
        resp = self.SendFrame(0x08, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def SetGearRatio(self, ratio: float) -> bool:
        """设置减速比（功能码 0x09），按 *100 发送 u16。"""
        iv = int(round(ratio * 100))
        data = self._ToU16BE(iv)
        resp = self.SendFrame(0x09, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def SetUniformPosPid(self, p: float, i: float, d: float) -> bool:
        """统一设置位置 PID（功能码 0x0A），按 *1000 发送 u16。"""
        data = bytearray()
        for val in (p, i, d):
            data.extend(self._ToU16BE(int(round(val * 1000))))
        resp = self.SendFrame(0x0A, bytes(data), target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def SetMotorType(self, motor_type: int) -> bool:
        """设置电机类型（功能码 0x0B），2 字节 u16。"""
        data = self._ToU16BE(int(motor_type))
        resp = self.SendFrame(0x0B, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def SetSoftStartTime(self, ms: int) -> bool:
        data = self._ToU16BE(int(ms))
        resp = self.SendFrame(0x11, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def SetSoftStopTime(self, ms: int) -> bool:
        data = self._ToU16BE(int(ms))
        resp = self.SendFrame(0x12, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def SetBlockTime(self, ms: int) -> bool:
        data = self._ToU16BE(int(ms))
        resp = self.SendFrame(0x13, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def ResetAllParams(self) -> bool:
        data = bytes([0x01])
        resp = self.SendFrame(0x1F, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def CarKeepAngleZSpeedMove(self, aim_angle: float, move_angle: float, speed: int) -> bool:
        """功能码 0x21: aim_angle( float*10 +10000), move_angle(float*10 +10000), speed(+10000) 各 u16 大端。"""
        a1 = int(round(aim_angle * 10)) + 10000
        a2 = int(round(move_angle * 10)) + 10000
        s = int(speed) + 10000
        data = self._ToU16BE(a1) + self._ToU16BE(a2) + self._ToU16BE(s)
        resp = self.SendFrame(0x21, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def CarKeepAngleZSpeedMoveTime(self, aim_angle: float, move_angle: float, speed: int, ms: int) -> bool:
        a1 = int(round(aim_angle * 10)) + 10000
        a2 = int(round(move_angle * 10)) + 10000
        s = int(speed) + 10000
        data = self._ToU16BE(a1) + self._ToU16BE(a2) + self._ToU16BE(s) + self._ToU16BE(int(ms))
        resp = self.SendFrame(0x22, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def CarKeepAngleXySpeedMove(self, move_angle: float, vx: int, vy: int) -> bool:
        a2 = int(round(move_angle * 10)) + 10000
        vxv = int(vx) + 10000
        vyv = int(vy) + 10000
        data = self._ToU16BE(a2) + self._ToU16BE(vxv) + self._ToU16BE(vyv)
        resp = self.SendFrame(0x23, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def CarTurn(self, aim_angle: float) -> bool:
        a = int(round(aim_angle * 10)) + 10000
        data = self._ToU16BE(a)
        resp = self.SendFrame(0x24, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def CarKeepAngleLocationMove(self, aim_angle: float, move_angle: float, speed: int, position: int) -> bool:
        a1 = int(round(aim_angle * 10)) + 10000
        a2 = int(round(move_angle * 10)) + 10000
        s = int(speed) + 10000
        # position 4 字节处理：表格建议发送 position + 0x7FFFFFFF
        pos = (int(position) + 0x7FFFFFFF) & 0xFFFFFFFF
        data = self._ToU16BE(a1) + self._ToU16BE(a2) + self._ToU16BE(s) + self._ToU32BE(pos)
        resp = self.SendFrame(0x25, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def CarStop(self) -> bool:
        data = bytes([0x01])
        resp = self.SendFrame(0x26, data, target_addr=self.F103_ADDR, read_response=True, response_length=1, response_timeout=0.2)
        return len(resp) > 0

    def ParseF0Response(self, resp: bytes) -> dict:
        """解析来自 F103 发向 H750 的 0xF0 反馈数据（按表格说明）。

        返回字典，包含解析出的陀螺仪角度和各类状态标志。
        """
        out = {}
        if len(resp) < 2:
            return out
        # 假设陀螺仪值占用字节0~1，u16 big-endian，编码为 value*10 + 10000
        gyro_raw = int.from_bytes(resp[0:2], byteorder="big", signed=False)
        gyro = (gyro_raw - 10000) / 10.0
        out["gyro"] = gyro
        # 之后的字节为若干状态标志，按表格位置解析
        # 为兼容性，逐字节放入 statusN
        for i in range(2, min(len(resp), 20)):
            out[f"status_{i}"] = resp[i]
        return out

    def __enter__(self):
        self.OpenPort()
        return self

    def __exit__(self, exc_type, exc, tb):
        self.ClosePort()



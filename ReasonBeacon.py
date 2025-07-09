import bluetooth
import subprocess
import re
import threading

class BTBeacon:
    def __init__(self, port=1):
        from ReasonData import QkJson,logger
        self.logger = logger
        self.cfg = QkJson()
        if not self.cfg.read("BLE", "Setup"):
            try:
                # 方法1: 使用hciconfig命令
                result = subprocess.run(['hciconfig'], capture_output=True, text=True)
                if result.returncode == 0:
                    # 查找BD Address
                    match = re.search(r'BD Address: ([0-9A-Fa-f:]{17})', result.stdout)
                    if match:
                        logger.info(f"蓝牙地址: {match.group(1).upper()}")
                        self.cfg.write("BLE", "MAC", match.group(1).upper())
            except:
                logger.error("蓝牙自动设置失败，请先配置蓝牙参数。")
                raise RuntimeError("蓝牙自动设置失败，请先配置蓝牙参数。")
        if self.cfg.read("BLE", "REMOTE") == "NONE":
            logger.error("请先配置蓝牙远程设备地址。")
            raise RuntimeError("请先配置蓝牙远程设备地址。")
        self.type = self.cfg.read("BLE", "Type")
        self.port = port
        if self.type == "Slave":
            self.server_address = self.cfg.read("BLE", "REMOTE")
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        else:
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_socket.bind(("", self.port))
            self.server_socket.listen(1)
        self.MessageCache = None
        self.connected = False
        self.CreateConnection()
        
    def StartServer(self):
        """启动蓝牙服务器"""
        while True:
            try:
                # 创建蓝牙套接字
                self.logger.info(f"蓝牙服务器启动，监听端口: {self.port}")
                self.logger.info("等待客户端连接...")
                # 等待客户端连接
                self.socket, self.client_address = self.server_socket.accept()
                self.logger.success(f"客户端已连接: {self.client_address}")
                self.connected = True
                # 启动接收消息的线程
                receive_thread = threading.Thread(target=self.receive_messages)
                receive_thread.daemon = True
                receive_thread.start()
                break
            except bluetooth.btcommon.BluetoothError as e:
                self.connected = False
            except Exception as e:
                self.logger.error(f"服务器错误: {e}")
    
    def ConnectToServer(self):
            """连接到蓝牙服务器"""
            try:
                self.logger.info(f"正在连接到服务器: {self.server_address}")
                # 连接到服务器
                self.socket.connect((self.server_address, self.port))
                self.logger.success("连接成功！")
                self.connected = True
                
                # 启动接收消息的线程
                self.receive_thread = threading.Thread(target=self.receive_messages)
                self.receive_thread.daemon = True
                self.receive_thread.start()
            except bluetooth.btcommon.BluetoothError as e:
                self.connected = False
            except Exception as e:
                self.logger.error(f"连接错误: {e}")

    def CreateConnection(self):
        # self.cleanup()
        if self.type == "Master":
            self.StartServer()
        else:
            self.ConnectToServer()

    def receive(self):
        """接收消息的线程函数"""
        while True:
            if not self.connected:
                self.logger.warning("未连接到服务器，尝试重连中。")
                self.CreateConnection()
            try:
                if self.socket:
                    data = self.socket.recv(1024)
                    if data:
                        message = data.decode('utf-8')
                        self.logger.success(f"收到消息: {message}")
                        self.MessageCache = message
            except bluetooth.btcommon.BluetoothError as e:
                self.connected = False
                break
            except Exception as e:
                self.logger.error(f"接收消息错误: {e}")
                self.connected = False
                break
    
    def Send(self,message):
        """发送消息"""
        try:
            if not self.connected:
                self.logger.warning("未连接到服务器，尝试重连中。")
                self.CreateConnection()
            if self.socket:
                self.socket.send(message.encode('utf-8'))
                self.logger.success("发送成功")
                return True
            else:
                self.logger.error("发送失败")
                return False
        except bluetooth.btcommon.BluetoothError as e:
            self.connected = False
            self.cleanup()
            self.__init__(self.port)  # 重新初始化
        except Exception as e:
            self.logger.error(f"发送消息错误: {e}")


    def cleanup(self):
        """清理资源"""
        if self.socket:
            self.socket.close()
        try:
            if self.server_socket:
                self.server_socket.close()
        except AttributeError:
            pass
        self.logger.success("服务已关闭")

class SerialCommunicate:
    def __init__(self):
        '''
        TODO no code here
        '''
        pass

import bluetooth
import subprocess
import re
import threading

class Bluetooth:
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
        if self.type == "Slave":
            self.server_address = self.cfg.read("BLE", "REMOTE")
            self.port = port
            self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        else:
            self.port = port
            self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            self.server_socket.bind(("", self.port))
            self.server_socket.listen(1)
        
    def start_server(self):
        """启动蓝牙服务器"""
        try:
            # 创建蓝牙套接字
            self.logger.info(f"蓝牙服务器启动，监听端口: {self.port}")
            self.logger.info("等待客户端连接...")
            # 等待客户端连接
            self.client_socket, self.client_address = self.server_socket.accept()
            self.logger.success(f"客户端已连接: {self.client_address}")
            # 启动接收消息的线程
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            return True
        except Exception as e:
            self.logger.error(f"服务器错误: {e}")
    
    def connect_to_server(self):
        """连接到蓝牙服务器"""
        try:
            self.logger.info(f"正在连接到服务器: {self.server_address}")
            
            # 连接到服务器
            self.socket.connect((self.server_address, self.port))
            self.logger.success("连接成功！")
            
            # 启动接收消息的线程
            self.receive_thread = threading.Thread(target=self.receive_messages)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            return True
        except Exception as e:
            self.logger.error(f"连接错误: {e}")
            self.cleanup()
    
    def create_connection(self):
        if self.type == "Slave":
            if not self.connect_to_server():
                self.create_connection()
        else:
            if not self.start_server():
                self.create_connection()

    def receive_messages(self):
        """接收消息的线程函数"""
        try:
            if self.client_socket:
                data = self.client_socket.recv(1024)
                if data:
                    message = data.decode('utf-8')
                    self.logger.success(f"收到消息: {message}")
                    return message
                else:
                    self.receive_messages()
        except KeyboardInterrupt as e:
            self.cleanup()
            self.logger.info("蓝牙线程已停止")
        except Exception as e:
            self.logger.error(f"接收消息错误: {e}")
            self.cleanup()
    
    def send_messages(self,message):
        """发送消息"""
        try:
            if self.client_socket:
                self.client_socket.send(message.encode('utf-8'))
                return True
            else:
                return False
        except Exception as e:
            self.logger.error(f"发送消息错误: {e}")
    
    def cleanup(self):
        """清理资源"""
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        self.logger.success("服务已关闭")

class SerialCommunicate:
    def __init__(self):
        '''
        TODO no code here
        '''
        pass
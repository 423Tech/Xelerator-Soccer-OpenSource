#!/usr/bin/env python3
# bluetooth_client.py

import bluetooth
import threading
import time

class BluetoothClient:
    def __init__(self, server_address, port=1):
        self.server_address = server_address
        self.port = port            
        self.socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)

        
    def connect_to_server(self):
        """连接到蓝牙服务器"""
        try:
            print(f"正在连接到服务器: {self.server_address}")
            
            # 连接到服务器
            self.socket.connect((self.server_address, self.port))
            print("连接成功！")
            
            # 启动接收消息的线程
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # 主线程处理发送消息
            self.send_messages()
            
        except Exception as e:
            print(f"连接错误: {e}")
        finally:
            self.cleanup()
    
    def receive_messages(self):
        """接收消息的线程函数"""
        while True:
            try:
                if self.socket:
                    data = self.socket.recv(1024)
                    if data:
                        message = data.decode('utf-8')
                        print(f"收到消息: {message}")
                    else:
                        break
            except Exception as e:
                print(f"接收消息错误: {e}")
                break
    
    def send_messages(self):
        """发送消息"""
        while True:
            try:
                message = input("输入要发送的消息 (输入 'quit' 退出): ")
                if message.lower() == 'quit':
                    break
                if self.socket:
                    self.socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"发送消息错误: {e}")
                break
    
    def cleanup(self):
        """清理资源"""
        if self.socket:
            self.socket.close()
        print("客户端已断开连接")

def scan_devices():
    """扫描附近的蓝牙设备"""
    print("正在扫描蓝牙设备...")
    devices = bluetooth.discover_devices(duration=10, lookup_names=True)
    
    if devices:
        print("发现的设备:")
        for i, (addr, name) in enumerate(devices):
            print(f"{i+1}: {name} - {addr}")
        return devices
    else:
        print("未发现任何设备")
        return []

if __name__ == "__main__":
        # 选择要连接的设备
    choice = "2C:CF:67:AB:3D:C5"
    client = BluetoothClient(choice)
    client.connect_to_server()

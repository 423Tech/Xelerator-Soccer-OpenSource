#!/usr/bin/env python3
# bluetooth_server.py

import bluetooth
import threading
import time

class BluetoothServer:
    def __init__(self, port=1):
        self.port = port
        self.server_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        self.server_socket.bind(("", self.port))
        self.server_socket.listen(1)
        
    def start_server(self):
        """启动蓝牙服务器"""
        try:
            # 创建蓝牙套接字
            print(f"蓝牙服务器启动，监听端口: {self.port}")
            print("等待客户端连接...")
            # 等待客户端连接
            self.client_socket, self.client_address = self.server_socket.accept()
            print(f"客户端已连接: {self.client_address}")
            
            # 启动接收消息的线程
            receive_thread = threading.Thread(target=self.receive_messages)
            receive_thread.daemon = True
            receive_thread.start()
            
            # 主线程处理发送消息
            self.send_messages()
            
        except Exception as e:
            print(f"服务器错误: {e}")
        finally:
            self.cleanup()
    
    def receive_messages(self):
        """接收消息的线程函数"""
        while True:
            try:
                if self.client_socket:
                    data = self.client_socket.recv(1024)
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
                if self.client_socket:
                    self.client_socket.send(message.encode('utf-8'))
            except Exception as e:
                print(f"发送消息错误: {e}")
                break
    
    def cleanup(self):
        """清理资源"""
        if self.client_socket:
            self.client_socket.close()
        if self.server_socket:
            self.server_socket.close()
        print("服务器已关闭")



if __name__ == "__main__":
    server = BluetoothServer()
    server.start_server()

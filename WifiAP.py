import network
import socket
import time

port = 10000  #端口号
wlan = None  #wlan
listenSocket = None  #套接字

#创建WiFi
def createWifi():   
  global ap
  ap = network.WLAN(network.AP_IF)     #创建接入点界面
  ap.active(True)                      #激活界面
  ap.config(essid='ESP-AP')  #设置接入点的ESSID，和WiFi 通道
  while(ap.ifconfig()[0] == '0.0.0.0'):   #等待连接
    time.sleep(1)
  return True

#Catch exceptions,stop program if interrupted accidentally in the 'try'
try:
  createWifi()
  ip = ap.ifconfig()[0]   #获取IP地址
  print(ip)
  listenSocket = socket.socket()   #创建套接字
  listenSocket.bind((ip, port))   #绑定地址和端口号
  listenSocket.listen(1)   #监听套接字
  listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   #设置套接字
  print ('tcp waiting...')

  while True:
    print("accepting.....")
    conn, addr = listenSocket.accept()   #接收连接请求，返回收发数据的套接字对象和客户端地址
    print(addr, "connected")

    while True:
      data = conn.recv(1024)   #接收数据（1024字节大小）
      if(len(data) == 0):   #判断客户端是否断开连接
        print("close socket")
        conn.close()   #关闭套接字
        break
      print(data)
      ret = conn.send(data)   #发送数据
except:
  if(listenSocket):   #判断套接字是否为空
    listenSocket.close()   #关闭套接字



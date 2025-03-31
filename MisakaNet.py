import network
import socket,os

class misakaNet:  
    def startAP(sSSID, sPassword): #开启热点
        listenSocket = None  #套接字
        try:
            ap = network.WLAN(network.AP_IF)     #创建接入点界面
            ap.active(True)                      #激活界面
            ap.config(essid=sSSID)  #设置接入点的ESSID，和WiFi 通道
            while(ap.ifconfig()[0] == '0.0.0.0'):   #等待连接
                pass
            ip = ap.ifconfig()[0]   #获取IP地址
            print(ip)
            listenSocket = socket.socket()   #创建套接字
            listenSocket.bind((ip, 1000))   #绑定地址和端口号
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
        except:
            if(listenSocket):   #判断套接字是否为空
                listenSocket.close()   #关闭套接字

    def connectWIFI(SSID, Password): #连接热点
        global s
        wlan = network.WLAN(network.STA_IF)  #创建WLAN对象
        wlan.active(True)                  #激活界面
        wlan.scan()                        #扫描接入点
        wlan.isconnected()                 #检查站点是否连接到AP
        wlan.connect(SSID, Password)       #连接到AP
        wlan.config('mac')                 #获取接口的MAC adddress
        wlan.ifconfig() 
        s = socket.socket()         # 创建 socket 对象
        host = '192.168.4.1'      # esp32 ip
        port = 10000                # 设置端口号
        try:
            s.connect((host, port))
            return True
        except:
            return False


    def sendData(IP,Port,sData): #发送数据
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((IP,Port))
        s.sendall(sData.encode('utf-8'))
        s.close()

    def receiveData(IP,Port,Data): #接收数据
        oServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        oServerSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
        oServerSocket.bind((IP,Port))
        oServerSocket.listen(50)
        while(1):
            oClientSocket,oClientAddr = oServerSocket.accept()
            while(1):
                sData = oClientSocket.recv(1024)
                if not sData:
                    break
                Data.value = sData.decode('UTF-8')
            oClientSocket.close()
        return Data



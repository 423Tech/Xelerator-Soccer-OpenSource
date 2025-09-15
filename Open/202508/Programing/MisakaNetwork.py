import socket,os


def startAP(sSSID, sPassword): #开启热点
    W = network.wifi.Wifi()
    E = W.start_ap(sSSID, sPassword)

def connectWIFI(SSID, Password): #连接热点
    W = network.wifi.Wifi()
    W.connect(SSID, Password, wait=True, timeout=10)
    # os.system('ip addr del ' + W.get_ip() + '/24 dev wlan0') #这里开始是指定IP
    # os.system('ip addr add ' + IP + '/24 dev wlan0')
    # os.system('wpa_cli reconnect')

def sendData(IP,Port,sData): #发送数据
    ClientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ClientSocket.connect((IP,Port))
    ClientSocket.sendall(sData.encode('utf-8'))
    ClientSocket.close()

def receiveData(IP,Port): #接收数据
    ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ServerSocket.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    ServerSocket.bind((IP,Port))
    ServerSocket.listen(50)
    while(1):
        ClientSocket,ClientAddr = ServerSocket.accept()
        while(1):
            Data = ClientSocket.recv(1024)
            if not Data:
                break
            Data = Data.decode('UTF-8')
            print(Data)
        ClientSocket.close()
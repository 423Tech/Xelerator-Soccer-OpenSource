import network
import socket,os

class misakaNet:  
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



import network
import socket
import time
from cfg import QkJson

cfg = QkJson()

SSID = "ESP-AP"                  #WiFi名称
PASSWORD = ""            #WiFi密码

wlan = network.WLAN(network.STA_IF)  #创建WLAN对象
wlan.active(True)                  #激活界面
wlan.scan()                        #扫描接入点
wlan.isconnected()                 #检查站点是否连接到AP
wlan.connect(SSID, PASSWORD)       #连接到AP
wlan.config('mac')                 #获取接口的MAC adddress
wlan.ifconfig() 

s = socket.socket()         # 创建 socket 对象
host = '192.168.4.1'      # esp32 ip
port = 10000                # 设置端口号

s.connect((host, port))

if __name__ == '__main__':
    while True:
        msg = 'aaaaaaa'
        s.send(msg)
        time.sleep(1)



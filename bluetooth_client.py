#!/usr/bin/env python3
# bluetooth_client.py

import bluetooth
import threading
import time


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

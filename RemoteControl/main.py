from flask import Flask, render_template
from flask_socketio import SocketIO
from maix import uart

# 初始化 Flask 和 Socket.IO
app = Flask(__name__)
socketio = SocketIO(app)

# 初始化 UART
devices = uart.list_devices()
if not devices:
    raise Exception("No UART devices found!")
serial = uart.UART(devices[0], 115200)

# 全局变量存储 x、y 和 speed
current_data = {'x': 0, 'y': 0, 'speed': 0}

# 发送数据到 UART
def send_uart_data():
    data_str = f"x{current_data['x']}y{current_data['y']}speed{current_data['speed']}end"
    serial.write_str(data_str)
    print(f"Sent to UART: {data_str}")

# WebSocket 事件
@socketio.on('direction')
def handle_direction(data):
    global current_data
    current_data['x'] = data.get('x', 0)
    current_data['y'] = data.get('y', 0)
    send_uart_data()

@socketio.on('speed')
def handle_speed(data):
    global current_data
    current_data['speed'] = data
    send_uart_data()

# 路由
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=80, allow_unsafe_werkzeug=True)

import cv2
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import threading

app = FastAPI()

# 全局变量存储摄像头对象
camera = None
camera_num = 1 
camera_lock = threading.Lock()

def initialize_camera():
    global camera
    with camera_lock:
        if camera is None:
            camera = cv2.VideoCapture(camera_num)
            if not camera.isOpened():
                print("Error: Camera not found.")
                return False
    return True

def generate_frames():
    """生成视频帧的生成器函数"""
    global camera
    
    while True:
        with camera_lock:
            if camera is None:
                break
            
            ret, frame = camera.read()
            if not ret:
                print("Error: Could not read frame.")
                break
            
            # 将帧编码为JPEG格式
            _, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            
            # 生成多部分响应格式
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')
        
        # time.sleep(0.033)  # 约30fps

@app.get("/")
async def home():
    """返回显示视频流的HTML页面"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Camera Feed</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                text-align: center;
                margin: 0;
                padding: 20px;
                background-color: #f0f0f0;
            }
            .container {
                max-width: 800px;
                margin: 0 auto;
                background-color: white;
                padding: 20px;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            h1 {
                color: #333;
                margin-bottom: 20px;
            }
            #video-stream {
                max-width: 100%;
                height: auto;
                border: 2px solid #333;
                border-radius: 5px;
            }
            .controls {
                margin-top: 20px;
            }
            button {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px 20px;
                margin: 5px;
                border-radius: 5px;
                cursor: pointer;
                font-size: 14px;
            }
            button:hover {
                background-color: #0056b3;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>实时摄像头画面</h1>
            <img id="video-stream" src="/video_feed" alt="Video Stream">
            <div class="controls">
                <button onclick="location.reload()">刷新页面</button>
                <button onclick="toggleFullscreen()">全屏显示</button>
            </div>
        </div>
        
        <script>
            function toggleFullscreen() {
                const img = document.getElementById('video-stream');
                if (!document.fullscreenElement) {
                    img.requestFullscreen().catch(err => {
                        alert('无法进入全屏模式: ' + err.message);
                    });
                } else {
                    document.exitFullscreen();
                }
            }
            
            // 检测图像加载错误
            document.getElementById('video-stream').onerror = function() {
                this.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjMwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZGRkIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPua憒WDj+WktOi0pe+8jOivt+ajgOafpeaRhOWDj+WktOi/nue6rzwvdGV4dD48L3N2Zz4=';
                alert('摄像头连接失败，请检查摄像头是否正常工作');
            };
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/video_feed")
async def video_feed():
    """返回视频流"""
    if not initialize_camera():
        return {"error": "Camera not available"}
    
    return StreamingResponse(
        generate_frames(),
        media_type="multipart/x-mixed-replace; boundary=frame"
    )

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化摄像头"""
    initialize_camera()

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时释放摄像头资源"""
    global camera
    with camera_lock:
        if camera is not None:
            camera.release()
            camera = None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

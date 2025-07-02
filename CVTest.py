import cv2
import asyncio
from fastapi import FastAPI
from fastapi.responses import StreamingResponse, HTMLResponse
import threading

app = FastAPI()

# 全局变量存储摄像头对象
camera = None
camera_num = 2
camera_lock = threading.Lock()

def initialize_camera():
    global camera
    with camera_lock:
        # 如果摄像头已存在，先释放
        if camera is not None:
            camera.release()
            
        camera = cv2.VideoCapture(camera_num, cv2.CAP_V4L2)
        if not camera.isOpened():
            print(f"Error: Camera {camera_num} not found.")
            camera = None
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
            .camera-selector {
                margin: 20px 0;
                padding: 15px;
                background-color: #f8f9fa;
                border-radius: 5px;
            }
            input[type="number"] {
                padding: 8px;
                margin: 0 10px;
                border: 1px solid #ddd;
                border-radius: 3px;
                width: 80px;
            }
            .status {
                margin: 10px 0;
                padding: 10px;
                border-radius: 5px;
                background-color: #e9ecef;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>实时摄像头画面</h1>
            
            <div class="status" id="camera-status">
                当前摄像头: <span id="current-camera">加载中...</span> | 
                状态: <span id="camera-state">检测中...</span>
            </div>
            
            <img id="video-stream" src="/video_feed" alt="Video Stream">
            
            <div class="camera-selector">
                <label for="camera-input">摄像头端口号:</label>
                <input type="number" id="camera-input" value="2" min="0" max="10">
                <button onclick="changeCamera()">切换摄像头</button>
            </div>
            
            <div class="controls">
                <button onclick="location.reload()">刷新页面</button>
                <button onclick="toggleFullscreen()">全屏显示</button>
                <button onclick="updateStatus()">更新状态</button>
            </div>
        </div>
        
        <script>
            // 切换摄像头功能
            async function changeCamera() {
                const cameraId = document.getElementById('camera-input').value;
                try {
                    const response = await fetch(`/change_camera/${cameraId}`, {
                        method: 'POST'
                    });
                    const result = await response.json();
                    
                    if (result.success) {
                        alert(result.message);
                        // 重新加载视频流
                        const videoImg = document.getElementById('video-stream');
                        videoImg.src = '/video_feed?' + new Date().getTime();
                        updateStatus();
                    } else {
                        alert('切换失败: ' + result.message);
                    }
                } catch (error) {
                    alert('切换摄像头时发生错误: ' + error.message);
                }
            }
            
            // 更新摄像头状态
            async function updateStatus() {
                try {
                    const response = await fetch('/camera_status');
                    const status = await response.json();
                    
                    document.getElementById('current-camera').textContent = status.current_camera;
                    document.getElementById('camera-state').textContent = status.status;
                    document.getElementById('camera-input').value = status.current_camera;
                } catch (error) {
                    console.error('更新状态失败:', error);
                }
            }
            
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
            
            // 页面加载完成后更新状态
            window.onload = function() {
                updateStatus();
                // 定期更新状态
                setInterval(updateStatus, 5000);
            };
            
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

@app.post("/change_camera/{camera_id}")
async def change_camera(camera_id: int):
    """切换摄像头端口"""
    global camera, camera_num
    
    with camera_lock:
        # 释放当前摄像头
        if camera is not None:
            camera.release()
            camera = None
        
        # 更新摄像头编号
        camera_num = camera_id
        
        # 尝试初始化新的摄像头
        if initialize_camera():
            return {"success": True, "message": f"成功切换到摄像头 {camera_id}"}
        else:
            return {"success": False, "message": f"无法打开摄像头 {camera_id}"}

@app.get("/camera_status")
async def camera_status():
    """获取当前摄像头状态"""
    global camera, camera_num
    with camera_lock:
        is_active = camera is not None and camera.isOpened()
        return {
            "current_camera": camera_num,
            "is_active": is_active,
            "status": "正常运行" if is_active else "未连接"
        }

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
    uvicorn.run(app, host="127.0.0.1", port=8000)

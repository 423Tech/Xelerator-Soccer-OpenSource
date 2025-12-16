from .PreProcess import Settings, logger, MODEL_DIR, VisionPreUntil, threading, queue, time, cv2, np

import numpy as np
import cv2
from typing import Dict, List

import numpy as np
import cv2

def simple_decode(raw_data, img_width=640, img_height=640, conf_threshold=0.5):
    """
    最简单的暴力解码器
    raw_data: 读取 bin 文件后的 numpy array (假设已经是 float32)
    """
    # 1. 展平数据，不管它原来是什么形状
    flat_data = raw_data.flatten()
    
    # 2. YOLOv8 的输出步长通常是 84 (4 coords + 1 obj + 80 classes)
    # 如果你用自己的数据集训练，把 84 改成 (4+1+你的类别数)
    stride = 84 
    num_boxes = len(flat_data) // stride
    
    results = []
    
    # 3. 暴力遍历每一个“框”的数据
    for i in range(num_boxes):
        start_idx = i * stride
        # 防止数据长度不够
        if start_idx + stride > len(flat_data):
            break
            
        # 提取这一组数据
        box_data = flat_data[start_idx : start_idx + stride]
        
        # 前4个是坐标 (cx, cy, w, h)
        cx, cy, w, h = box_data, box_data, box_data, box_data
        
        # 第5个是目标置信度
        obj_conf = box_data
        
        # 如果置信度太低，跳过这个框 (这是节省计算量的关键)
        if obj_conf < conf_threshold:
            continue
            
        # 4. 计算类别
        class_probs = box_data[5:]
        cls_id = np.argmax(class_probs)
        cls_conf = class_probs[cls_id]
        
        final_conf = obj_conf * cls_conf
        if final_conf < conf_threshold:
            continue
        
        # 5. 关键：坐标转换 (这里假设 NPU 已经帮我们做了大部分工作)
        # 将归一化坐标转换为像素坐标
        # 注意：这里假设 cx, cy 是相对于 640x640 的比例
        x1 = (cx - w / 2) * img_width
        y1 = (cy - h / 2) * img_height
        x2 = (cx + w / 2) * img_width
        y2 = (cy + h / 2) * img_height
        
        # 6. 确保坐标在图片范围内
        x1 = max(0, min(img_width, x1))
        y1 = max(0, min(img_height, y1))
        x2 = max(0, min(img_width, x2))
        y2 = max(0, min(img_height, y2))
        
        # 7. 存入结果
        results.append([x1, y1, x2, y2, final_conf, int(cls_id)])
    
    return results

# ================== 调用 ==================
# 1. 读取 bin
with open("your_output.bin", "rb") as f:
    # 注意：这里必须确认 bin 里存的是 float32 还是 int8
    # 如果是 int8，需要先转 float32 并归一化
    raw = np.frombuffer(f.read(), dtype=np.float32) 

# 2. 解码 (假设原图是 640x640)
boxes = simple_decode(raw, img_width=640, img_height=640)

# 3. 打印结果
for box in boxes:
    print(f"画框坐标: {box:.2f}, {box:.2f}, {box:.2f}, {box:.2f} | 置信度: {box:.2f} | 类别: {box}")


class TunaVision(VisionPreUntil):
    '''
    support for RDK x5 BPU
    '''
    def __init__(self):
        super().__init__()
        import bpu_infer_lib
        self.infer = bpu_infer_lib.Infer(False)
        self.infer.load_model(str(MODEL_DIR / "yolov8n.bin"))


        self.YOLOQueue = queue.Queue(maxsize=1)
        self.ChassisQueue = queue.Queue(maxsize=1)
        self.BallQueue = queue.Queue(maxsize=1)


        self.YoloProcessThread = threading.Thread(target=self.YoloProcess)
        self.YoloProcessThread.daemon = True
        self.YoloProcessThread.start()

        self.ModelInferThread = threading.Thread(target=self.ModelInfer)
        self.ModelInferThread.daemon = True
        self.ModelInferThread.start()


    def bgr2nv12_opencv(self, image):
        height, width = image.shape[0], image.shape[1]
        area = height * width
        yuv420p = cv2.cvtColor(image, cv2.COLOR_BGR2YUV_I420).reshape((area * 3 // 2,))
        y = yuv420p[:area] # Y分量：前area个元素
        uv_planar = yuv420p[area:].reshape((2, area // 4)) # UV分量：后面的元素，每2个元素分别为U和V分量
        uv_packed = uv_planar.transpose((1, 0)).reshape((area // 2,)) # 将UV分量交替排列为交错的UV格式
        nv12 = np.zeros_like(yuv420p) # 创建与原YUV数据形状相同的空数组用于存放NV12格式数据
        nv12[:height * width] = y # 将Y分量直接赋值到NV12数组的前部
        nv12[height * width:] = uv_packed  # 将交错的UV分量赋值到NV12数组的后部
        return nv12

    def YoloProcess(self):
        while(1):
            BindingsList = []
            for i in range(4):
                Frame = self.Frames[i]
                if Frame is not None:
                    BindingsList.append(self.bgr2nv12_opencv(Frame))
            if self.YOLOQueue.full():
                pass
            else:
                self.PreProcessTF = self.PreProcessTF + 1
                self.YOLOQueue.put(BindingsList)
            time.sleep(0.01)
        
    def ModelInfer(self):
        while(1):
            print(1)
            FrameCount = 0
            LastTime = time.time()
            # while(1):
            FrameCount += 1
            CurrentTime = time.time()
            if CurrentTime - LastTime >= 1.0:
                logger.success(f"Hailo Process FPS: {FrameCount}")
                FrameCount = 0
                LastTime = CurrentTime
            BindingsList = self.YOLOQueue.get()
            self.InferTF = self.InferTF + 1
            # 确保在传递给 BindingsList 之前执行此操作
            BallOutputs = []
            ChassisList = []
            count = 0
            for Bindings in BindingsList:
                flag = 0
                self.infer.read_input(Bindings, 0)
                self.infer.forward(True) 
                self.infer.get_output()
                # TODO finish data after-process
                # breakpoint()
                print(simple_decode(self.infer.outputs.data, img_width=640, img_height=640))
                breakpoint()
                # self.infer.outputs.data
                # x_start, x_end, y_start, y_end, confidence, class_id = detection
                # BallOutputs.append([CenterX*self.IMAGE_SIZE/10, BottomY*self.IMAGE_SIZE/10, BallWidth*self.IMAGE_SIZE/10, BallHeight*self.IMAGE_SIZE/10, confidence])
                # BallOutputs.append([0,0,0,0,0])
                    

                # # 0 512000
                # # 1 409600
                # # 2 128000
                # # 3 102400
                # # 4 32000
                # # 5 25600
                # ChassisList.append(self.multi_scale_yolov8_post_process(bpu_raw_outputs_dict))
            logger.info(BallOutputs)
            self.ChassisQueue.put(ChassisList)
            self.BallQueue.put(BallOutputs)

from .PreProcess import Settings, logger, MODEL_DIR, VisionPreUntil, threading, queue, time, cv2, np

class TunaVision(VisionPreUntil):
    '''
    support for RDK x5 BPU
    '''
    def __init__(self):
        super().__init__()
        import bpu_infer_lib
        self.inf = bpu_infer_lib.Infer(True)
        self.inf.load_model(str(MODEL_DIR / "yolov8n.bin"))

        self.YOLOQueue = queue.Queue(maxsize=1)
        self.ChassisQueue = queue.Queue(maxsize=1)
        self.BallQueue = queue.Queue(maxsize=1)

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
                continue
            else:
                self.PreProcessTF = self.PreProcessTF + 1
                self.YOLOQueue.put(BindingsList)
            time.sleep(0.01)
        
    def ModelInfer(self):
        FrameCount = 0
        LastTime = time.time()
        while(1):
            FrameCount += 1
            CurrentTime = time.time()
            if CurrentTime - LastTime >= 1.0:
                self.logger.debug(f"Hailo Process FPS: {FrameCount}")
                FrameCount = 0
                LastTime = CurrentTime
            BindingsList = self.YOLOQueue.get()
            self.InferTF = self.InferTF + 1
            # 确保在传递给 BindingsList 之前执行此操作
            self.infer.forward(True)
            Outputs = []
            ChassisList = []
            for Bindings in BindingsList:
                self.inf.set_input(Bindings)
                self.inf.forward()
                OutputBuffer = self.inf.outputs[0].data
                Outputs.append(OutputBuffer)            
            self.ChassisQueue.put(Outputs[0])
            self.BallQueue.put(Outputs[1])

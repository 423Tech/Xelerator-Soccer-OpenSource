from .PreProcess import Settings, logger, MODEL_DIR, VisionPreUntil, threading, queue, time, cv2, np

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

    def post_process_bpu_output(self,raw_output: np.ndarray, width: int, height: int) -> np.ndarray:
        """
        将 BPU 原始输出（80个元素）进行后处理，得到最终的检测框列表。
        输出的框坐标是相对于像素的 (x1, y1, x2, y2)。
        """

        # 1. Reshape: 假设是 (N, 5) 结构，这里 N=16
        try:
            # candidates 的 shape: (16, 5)
            candidates = raw_output.flatten().reshape(-1, 5)
            return candidates
        except ValueError:
            print(f"错误: 原始输出长度 {raw_output.size} 无法重塑为 N x 5 结构。")
            return np.empty((0, 5))

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
        # while(1):
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
            FrameCount = 0
            LastTime = time.time()
            # while(1):
            FrameCount += 1
            CurrentTime = time.time()
            if CurrentTime - LastTime >= 1.0:
                self.logger.debug(f"Hailo Process FPS: {FrameCount}")
                FrameCount = 0
                LastTime = CurrentTime
            BindingsList = self.YOLOQueue.get()
            self.InferTF = self.InferTF + 1
            # 确保在传递给 BindingsList 之前执行此操作
            BallOutputs = []
            ChassisList = []
            for Bindings in BindingsList:
                self.infer.read_input(Bindings, 0)
                self.infer.forward(True)
                time.sleep(0.02)          
                self.infer.get_output()
                # TODO finish data after-process
                BallOutputBuffer = self.infer.outputs[1].data
                print(self.post_process_bpu_output(BallOutputBuffer,15,15))
                breakpoint()
                BallOutputs.append(BallOutputBuffer[0])  
                ChassisOutputBuffer = self.infer.outputs[3].data
                ChassisList.append(ChassisOutputBuffer)  
            self.ChassisQueue.put(ChassisList)
            self.BallQueue.put(BallOutputs)

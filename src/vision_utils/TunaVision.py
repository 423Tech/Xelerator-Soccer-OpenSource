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
        IMAGE_WIDTH = 640
        IMAGE_HEIGHT = 640
        CONFIDENCE_THRESHOLD = 0.5  # 置信度筛选阈值
        NMS_IOU_THRESHOLD = 0.45    # NMS (非极大值抑制) 的 IoU 阈值
        BPU_OUTPUT_SIZE = 80
        if raw_output.size != BPU_OUTPUT_SIZE:
            print(f"⚠️ 警告: 原始输出长度 {raw_output.size} 不等于预期 {BPU_OUTPUT_SIZE}。")
            return np.empty((0, 5))

        # 1. Reshape: 假设是 (N, 5) 结构，这里 N=16
        try:
            # candidates 的 shape: (16, 5)
            candidates = raw_output.flatten().reshape(-1, 5)
        except ValueError:
            print(f"错误: 原始输出长度 {raw_output.size} 无法重塑为 N x 5 结构。")
            return np.empty((0, 5))

        # 假设 BPU 输出的 5 个值是归一化的 (0到1) 的 (cx, by, w, h, conf)
        
        # 2. 转换为像素坐标并提取 NMS 所需数据 (x1, y1, x2, y2, conf)
        
        # 从原始输出中分离各个属性
        cx, by, w, h, conf = candidates.T
        
        # 将归一化坐标转换为像素坐标 (Ball_Bottom_Y -> by)
        # y1 = by - h, y2 = by
        x1 = (cx - w / 2) * width
        y1 = (by - h) * height
        x2 = (cx + w / 2) * width
        y2 = by * height
        
        # 结合成 NMS 输入格式
        boxes_for_nms = np.stack([x1, y1, x2, y2], axis=1)
        
        # 3. Thresholding: 筛选置信度高的框
        # 注意：这里直接操作置信度数组，以便同时筛选 boxes_for_nms
        valid_indices = conf > CONFIDENCE_THRESHOLD
        
        high_conf_boxes = boxes_for_nms[valid_indices]
        high_conf_scores = conf[valid_indices]

        if high_conf_boxes.shape[0] == 0:
            return np.empty((0, 5))

        # 4. NMS (非极大值抑制)
        # cv2.dnn.NMSBoxes 要求输入是 int 坐标，所以我们需要四舍五入
        # NMSBoxes 返回的是保留下来的框的索引
        indices = cv2.dnn.NMSBoxes(
            high_conf_boxes.astype(np.float32).tolist(), # NMS 需要 float32 列表
            high_conf_scores.tolist(), 
            CONFIDENCE_THRESHOLD, 
            NMS_IOU_THRESHOLD
        )
        
        if len(indices) == 0:
            return np.empty((0, 5))
        
        indices = indices.flatten()
        
        # 最终的检测结果 (格式: x1, y1, x2, y2, conf)
        final_detections_xyxy = np.concatenate(
            [high_conf_boxes[indices], high_conf_scores[indices].reshape(-1, 1)], 
            axis=1
        )

        return final_detections_xyxy

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

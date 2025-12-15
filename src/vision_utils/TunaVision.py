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

    def yolov8_post_process(self,raw_output: np.ndarray) -> np.ndarray:
        """
        将 BPU 的原始扁平输出 (409600 元素) 转换为最终的检测框列表。
        输出格式: (N, 5) 数组，每行: [x1, x2, y1, y2, confidence]
        """
        IMAGE_SIZE = 640
        CONFIDENCE_THRESHOLD = 0.5  # 置信度筛选阈值
        NMS_IOU_THRESHOLD = 0.45    # NMS IOU 阈值
        # 警告: BPU_RAW_SIZE 是 409600，我们假设这个数对应于 YOLOv8 的某个特征图的元素总数
        BPU_RAW_SIZE = 409600
        if raw_output.size != BPU_RAW_SIZE:
            print(f"⚠️ 错误: 原始输出长度 {raw_output.size} 不等于预期 {BPU_RAW_SIZE}。无法进行YOLOv8解码。")
            return np.empty((0, 5))

        # --- 阶段 1: 解码 (Decoding) ---
        
        # ⚠️ 占位符：YOLOv8 DFL 解码是核心且复杂的步骤。
        # 
        # 这一步的目标是：
        # 1. 将 raw_output (409600) 重塑为逻辑张量 (例如 80x80x64 或 80x80x(4+64+1))
        # 2. 对 DFL 通道应用 Softmax 和加权求和，解码出 d_l, d_t, d_r, d_b 四个距离。
        # 3. 结合网格坐标，计算出 N 个预测框的 (x_center, y_center, w, h)。
        # 4. 提取 N 个预测框的置信度 (Confidence)。
        
        # --- 模拟解码结果 (实际需要替换为复杂的 DFL 解码代码) ---
        
        # 假设解码后得到了 6400 个预测（80x80），每个预测有 5 个属性：
        # (x_center, y_center, width, height, confidence)
        
        try:
            # 假设解码函数返回了 6400 个预测框的原始数据 (6400, 5)
            # 注意：实际中，您需要将 DFL 解码后的结果放在这里
            # 为了演示 NMS 和最终格式，我们在这里创建模拟数据：
            NUM_PREDICTIONS = 6400
            
            # 模拟解码结果 (归一化坐标 0-1)
            simulated_detections = np.random.rand(NUM_PREDICTIONS, 5).astype(np.float32)
            
            # 将大部分置信度设置为低值，以便筛选
            simulated_detections[:, 4] *= 0.1
            
            # 植入几个高置信度的球
            simulated_detections[100, :] = [0.5, 0.5, 0.1, 0.1, 0.95]
            simulated_detections[101, :] = [0.51, 0.51, 0.1, 0.1, 0.90] # 重叠框
            
            
        except Exception as e:
            print(f"解码错误或模拟失败: {e}")
            return np.empty((0, 5))
            
        # 将格式转换为 NMS 所需的 (x1, y1, x2, y2, conf)
        x_center, y_center, w, h, conf = simulated_detections.T
        
        # 转换为归一化像素坐标 (0到1) 的 (x1, y1, x2, y2)
        x1 = x_center - w / 2
        y1 = y_center - h / 2
        x2 = x_center + w / 2
        y2 = y_center + h / 2
        
        boxes_for_nms = np.stack([x1, y1, x2, y2], axis=1)

        # --- 阶段 2: 筛选 (Thresholding) ---
        
        # 筛选置信度高于阈值的候选框
        valid_indices = conf > CONFIDENCE_THRESHOLD
        
        high_conf_boxes = boxes_for_nms[valid_indices]
        high_conf_scores = conf[valid_indices]

        if high_conf_boxes.shape[0] == 0:
            return np.empty((0, 5))

        # --- 阶段 3: 非极大值抑制 (NMS) ---
        
        # NMS 仅在保留的框中运行
        # 注意: NMSBoxes 需要 (x1, y1, x2, y2) 列表，我们使用 float32 传入
        indices = cv2.dnn.NMSBoxes(
            high_conf_boxes.astype(np.float32).tolist(), 
            high_conf_scores.tolist(), 
            CONFIDENCE_THRESHOLD, 
            NMS_IOU_THRESHOLD
        ).flatten()
        
        if len(indices) == 0:
            return np.empty((0, 5))
        
        # 提取最终的框和置信度
        final_boxes_xyxy = high_conf_boxes[indices]
        final_scores = high_conf_scores[indices]
        
        # --- 阶段 4: 格式化输出 ---

        # 您的目标格式是 [start_x, end_x, start_y, end_y, confidence]
        # NMS 输出的 final_boxes_xyxy 已经是 [x1, y1, x2, y2]
        
        # 重新排列并合并为最终的 (N, 5) 数组
        # final_boxes_xyxy[:, 0] 是 x1 (start_x)
        # final_boxes_xyxy[:, 2] 是 x2 (end_x)
        # final_boxes_xyxy[:, 1] 是 y1 (start_y)
        # final_boxes_xyxy[:, 3] 是 y2 (end_y)
        
        # 重新组合张量以满足 [start_x, end_x, start_y, end_y, confidence] 顺序
        output_array = np.stack([
            final_boxes_xyxy[:, 0], # x_start
            final_boxes_xyxy[:, 2], # x_end
            final_boxes_xyxy[:, 1], # y_start
            final_boxes_xyxy[:, 3], # y_end
            final_scores           # confidence
        ], axis=1)

        Ball_Y_Min = int(output_array[0,1] * 640) - 80 + 15
        Ball_X_Min = int(output_array[0,0] * 640) + 15
        Ball_Y_Max = int(output_array[0,3] * 640) - 80 -15
        Ball_X_Max = int(output_array[0,2] * 640) -15
        Ball_Bottom_Y = Ball_Y_Max
        Ball_Width = Ball_X_Max - Ball_X_Min
        Ball_Height = Ball_Y_Max - Ball_Y_Min
        Ball_Center_X = int((Ball_X_Min + Ball_X_Max) / 2)

        return [Ball_Center_X,Ball_Bottom_Y,Ball_Width,Ball_Height,final_scores]
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
            count = 0
            for Bindings in BindingsList:
                self.infer.read_input(Bindings, 0)
                self.infer.forward(True)
                time.sleep(0.02)          
                self.infer.get_output()
                # TODO finish data after-process
                BallOutputBuffer = self.infer.outputs[1].data
                BallOutputs.append(self.yolov8_post_process(self.infer.outputs[1].data))
                # 0 512000
                # 1 409600
                # 2 128000
                # 3 102400
                # 4 32000
                # 5 25600
                ChassisOutputBuffer = self.infer.outputs[5].data
                ChassisList.append(self.yolov8_post_process(ChassisOutputBuffer))  
                count += 1
            self.ChassisQueue.put(ChassisList)
            self.BallQueue.put(BallOutputs)

from .PreProcess import Settings, logger, MODEL_DIR, VisionPreUntil, threading, queue, time, cv2, np

class ArisuIntelligence(VisionPreUntil):
    '''
    with hailo only
    '''
    
    def __init__(self):


        self.logger = logger

        from hailo_platform import VDevice, HailoSchedulingAlgorithm

        self.PreProcessTF = 0
        self.InferTF = 0

        self.HailoParams = VDevice.create_params()
        self.HailoParams.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN

        self.YOLOQueue = queue.Queue(maxsize=1)

        self.MergedChassisList = []
        self.ChassisQueue = queue.Queue(maxsize=1)
        self.BallQueue = queue.Queue(maxsize=1)

        super().__init__()

        self.InitConfiguredModelThread = threading.Thread(target=self.InitConfiguredModel)
        self.InitConfiguredModelThread.daemon = True
        self.InitConfiguredModelThread.start()

        # 报错会阻塞程序 try&except
        time.sleep(2)


        self.ModelPreProcessThread = threading.Thread(target=self.ModelPreProcess)
        self.ModelPreProcessThread.daemon = True
        self.ModelPreProcessThread.start()

        self.ModelInferThread = threading.Thread(target=self.ModelInfer)
        self.ModelInferThread.daemon = True
        self.ModelInferThread.start()


    def Resize(self, Frame, TargetSize=(640, 640)):
        Height, Width = Frame.shape[:2]
        TargetHeight, TargetWidth = TargetSize
        
        Scale = min(TargetWidth/Width, TargetHeight/Height)
        
        NewWidth = int(Width * Scale)
        NewHeight = int(Height * Scale)
        
        ResizedImage = cv2.resize(Frame, (NewWidth, NewHeight))
        
        PaddedImage = np.zeros((TargetHeight, TargetWidth, 3), dtype=np.uint8)
        
        YOffset = (TargetHeight - NewHeight) // 2
        XOffset = (TargetWidth - NewWidth) // 2
        
        PaddedImage[YOffset:YOffset+NewHeight, XOffset:XOffset+NewWidth] = ResizedImage
        
        return PaddedImage
   

    def InitConfiguredModel(self):
        with VDevice(self.HailoParams) as Hat:
            InferModel = Hat.create_infer_model(str(MODEL_DIR)+"/yolov8s.hef")
            InferModel.set_batch_size(4)
            self.InputShape = InferModel.input().shape
            self.OutputShape = InferModel.output().shape
            with InferModel.configure() as ConfiguredInferModel:
                self.ConfiguredInferModel = ConfiguredInferModel
                time.sleep(114514)

    def ModelPreProcess(self):
        '''
        input: int8
        output: float32
        '''
        while(1):
            BindingsList = []
            for i in range(4):
                Bindings = self.ConfiguredInferModel.create_bindings()
                OutputBuffer = np.empty(self.OutputShape, dtype=np.float32)
                Frame = self.Frames[i]
                if Frame is not None:
                    Frame = self.Resize(Frame, (640, 640))
                    Frame = cv2.cvtColor(Frame, cv2.COLOR_BGR2RGB)
                    # cv2.imshow(f"Frame {i}", Frame)
                    # Frame = Frame.astype(np.uint8)
                    # Frame = np.ascontiguousarray(Frame, dtype=np.uint8)
                    # print(Frame.shape)
                    Bindings.input().set_buffer(Frame)
                    Bindings.output().set_buffer(OutputBuffer)
                    BindingsList.append(Bindings)
            if self.YOLOQueue.full():
                self.YOLOQueue.empty()
                # print(self.YOLOQueue.get())
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
            try:
                self.ConfiguredInferModel.run(BindingsList, 1000)
            except Exception as e:
                self.logger.error(f"Hailo Inference Error: {e}, automatically restarting inference thread.")
                self.ModelInfer()
            BallOutputs = []
            ChassisOutputs = []
            for Bindings in BindingsList:
                OutputBuffer = Bindings.output().get_buffer()
                BallOutputs.append(OutputBuffer[0])
                ChassisOutputs.append(OutputBuffer[3])
            self.ChassisQueue.put(ChassisOutputs)
            self.BallQueue.put(BallOutputs)
            # print(ChassisList)
        
            # print(Output0)
            # time.sleep(0.01)


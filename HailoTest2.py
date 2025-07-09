import numpy as np
from functools import partial
from hailo_platform import VDevice, HailoSchedulingAlgorithm, FormatType
import time

number_of_frames = 4
timeout_ms = 10000

def example_callback(completion_info, bindings):
    if completion_info.exception:
        # handle exception
        pass

    _ = bindings.output().get_buffer()

def infer(should_use_multi_process_service):
    # Create a VDevice
    params = VDevice.create_params()
    params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
    params.group_id = "SHARED"
    if should_use_multi_process_service:
        params.multi_process_service = should_use_multi_process_service

    with VDevice(params) as vdevice:

        # Create an infer model from an HEF:
        infer_model = vdevice.create_infer_model('/xel/yolov8m.hef')

        # Set optional infer model parameters
        infer_model.set_batch_size(4)

        # For a single input / output model, the input / output object
        # can be accessed with a name parameter ...
        while True:

        # Once the infer model is set, configure the infer model
            with infer_model.configure() as configured_infer_model:
                for _ in range(number_of_frames):
                    # Create bindings for it and set buffers
                    bindings = configured_infer_model.create_bindings()
                    bindings.input().set_buffer(np.empty(infer_model.input().shape).astype(np.uint8))
                    bindings.output().set_buffer(np.empty(infer_model.output().shape).astype(np.float32))

                    # Wait for the async pipeline to be ready, and start an async inference job
                    configured_infer_model.wait_for_async_ready(timeout_ms=10000)

                    # Any callable can be passed as callback (lambda, function, functools.partial), as long
                    # as it has a keyword argument "completion_info"
                    job = configured_infer_model.run_async([bindings], partial(example_callback, bindings=bindings))

                # Wait for the last job
                job.wait(timeout_ms)
    
LastTime = time.time()
FrameCount = 0

while True:
    try:
        if time.time() - LastTime > 1:
            print(f"FPS: {FrameCount}")
            LastTime = time.time()
            FrameCount = 0

        # Call the infer function with multi-process service enabled
        infer(False)
        FrameCount += 1

    except KeyboardInterrupt:
        break
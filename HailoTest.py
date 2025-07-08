import numpy as np
import time
from hailo_platform import VDevice, HailoSchedulingAlgorithm

def pure_inference_benchmark():
    """
    纯推理性能测试 - 接近hailortcli benchmark的结果
    """
    timeout_ms = 1000
    hef_path = '/xel/ArisuIntelligence.hef'
    test_duration = 10  # 测试时长（秒）
    
    params = VDevice.create_params()
    params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
    
    print("="*60)
    print("纯推理性能测试 (类似 hailortcli benchmark)")
    print("="*60)
    print(f"模型文件: {hef_path}")
    print(f"测试模式: 纯推理 + 随机数据")
    print(f"测试时长: {test_duration} 秒")
    print("-"*60)
    
    try:
        with VDevice(params) as vdevice:
            print("VDevice 创建成功")
            
            infer_model = vdevice.create_infer_model(hef_path)
            print("推理模型加载成功")
            
            # 测试不同批次大小
            for batch_size in [1, 2, 4, 8]:
                print(f"\n{'='*40}")
                print(f"测试批次大小: {batch_size}")
                print(f"{'='*40}")
                
                try:
                    # 设置批次大小
                    infer_model.set_batch_size(batch_size)
                    
                    input_shape = infer_model.input().shape
                    output_shape = infer_model.output().shape
                    
                    print(f"输入形状: {input_shape}")
                    print(f"输出形状: {output_shape}")
                    
                    with infer_model.configure() as configured_infer_model:
                        bindings = configured_infer_model.create_bindings()
                        
                        # 使用随机数据（类似benchmark）
                        input_buffer = np.random.randint(0, 255, input_shape, dtype=np.uint8)
                        output_buffer = np.empty(output_shape, dtype=np.float32)

                        
                        bindings.input().set_buffer(input_buffer)
                        bindings.output().set_buffer(output_buffer)
                        
                        print("预热...")
                        # 预热
                        for _ in range(10):
                            configured_infer_model.run([bindings], timeout_ms)
                        
                        print("开始纯推理测试...")
                        
                        # 纯推理性能测试
                        inference_count = 0
                        start_time = time.time()
                        
                        while time.time() - start_time < test_duration:
                            # 只测量推理时间，不包括其他操作
                            if batch_size == 4:
                                configured_infer_model.run([bindings,bindings,bindings,bindings], timeout_ms)
                                inference_count += 4
                            else:
                                configured_infer_model.run([bindings], timeout_ms)
                                inference_count += 1
                            
                        
                        total_time = time.time() - start_time
                        total_frames = inference_count * batch_size
                        pure_fps = total_frames / total_time
                        inference_per_sec = inference_count / total_time
                        avg_inference_time = total_time / inference_count * 1000
                        
                        print(f"结果:")
                        print(f"  推理次数: {inference_count}")
                        print(f"  总帧数: {total_frames}")
                        print(f"  纯推理FPS: {pure_fps:.1f} FPS")
                        print(f"  推理次数/秒: {inference_per_sec:.1f}")
                        print(f"  平均推理时间: {avg_inference_time:.2f} ms/batch")
                        print(f"  单帧推理时间: {avg_inference_time/batch_size:.2f} ms/frame")
                        
                        # 与benchmark对比
                        benchmark_fps = 398.41
                        efficiency = (pure_fps / benchmark_fps) * 100
                        print(f"  vs hailortcli: {efficiency:.1f}% 效率")
                        
                except Exception as e:
                    print(f"批次大小 {batch_size} 测试失败: {e}")
                    continue
            
    except Exception as e:
        print(f"错误: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    pure_inference_benchmark()
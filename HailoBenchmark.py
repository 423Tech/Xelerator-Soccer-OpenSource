import numpy as np
import cv2
import time
from hailo_platform import VDevice, HailoSchedulingAlgorithm

def batch_inference(batch_size=4):
    """批处理推理"""
    timeout_ms = 1000
    image_path = "./Test.png"  # 图像路径
    
    print(f"=== Hailo-8 批处理推理测试 ===")
    print(f"图像路径: {image_path}")
    print(f"批处理大小: {batch_size}")
    
    params = VDevice.create_params()
    params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
    
    # 创建VDevice
    with VDevice(params) as vdevice:
        # 加载HEF模型
        infer_model = vdevice.create_infer_model('/xel/yolov11s.hef')
        infer_model.set_batch_size(batch_size)
        
        # 配置并创建推理模型
        with infer_model.configure() as configured_infer_model:
            # 创建批处理绑定列表
            bindings_list = []
            
            # 加载图像并预处理
            image = cv2.imread(image_path)
            if image is not None:
                print(f"成功加载图像: {image_path}")
                
                # 获取模型输入形状
                input_shape = infer_model.input().shape
                target_height, target_width = input_shape[0], input_shape[1]
                print(f"模型输入尺寸: {target_height} x {target_width}")
                print(f"原始图像尺寸: {image.shape[0]} x {image.shape[1]}")
                
                # 调整大小并转换色彩空间
                image = cv2.resize(image, (target_width, target_height))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                processed_image = image.astype(np.uint8)
                
                print("✓ 图像预处理完成")
            else:
                print(f"⚠️ 无法加载图像: {image_path}")
                print("使用随机数据...")
                processed_image = np.random.randint(0, 255, size=infer_model.input().shape, dtype=np.uint8)
            
            # 为每个批次创建绑定
            print("准备批处理绑定...")
            for i in range(batch_size):
                bindings = configured_infer_model.create_bindings()
                
                # 设置输入缓冲区 (使用相同的图像)
                bindings.input().set_buffer(processed_image)
                
                # 设置输出缓冲区
                output_buffer = np.empty(infer_model.output().shape).astype(np.float32)
                bindings.output().set_buffer(output_buffer)
                
                bindings_list.append(bindings)
            
            # 预热
            print("进行预热推理...")
            configured_infer_model.run(bindings_list, timeout_ms)
            
            # 开始批处理推理
            print(f"\n开始批处理推理 ({batch_size} 个实例)...")
            
            # 记录多次运行的时间
            num_runs = 10
            total_times = []
            
            for run in range(num_runs):
                start_time = time.time()
                configured_infer_model.run(bindings_list, timeout_ms)
                end_time = time.time()
                total_time = (end_time - start_time) * 1000  # 转换为毫秒
                total_times.append(total_time)
                print(f"运行 {run+1}/{num_runs}: {total_time:.2f} ms")
            
            # 计算平均时间
            avg_time = np.mean(total_times)
            min_time = np.min(total_times)
            std_dev = np.std(total_times)
            
            print(f"\n✓ 批处理推理完成")
            print(f"平均总推理时间: {avg_time:.2f} ms")
            print(f"最快总推理时间: {min_time:.2f} ms")
            print(f"时间标准差: {std_dev:.2f} ms")
            print(f"平均每个实例时间: {avg_time / batch_size:.2f} ms")
            print(f"理论最大FPS: {batch_size * 1000 / min_time:.2f}")
            print(f"平均FPS: {batch_size * 1000 / avg_time:.2f}")
            
            return {
                'method': 'batch',
                'batch_size': batch_size,
                'avg_time': avg_time,
                'min_time': min_time,
                'std_dev': std_dev,
                'avg_per_instance': avg_time / batch_size,
                'max_fps': batch_size * 1000 / min_time,
                'avg_fps': batch_size * 1000 / avg_time
            }


def single_inference_repeated(num_repeats=4):
    """重复单个图像推理"""
    timeout_ms = 1000
    image_path = "/root/TestImage.jpg"  # 图像路径
    
    print(f"\n=== Hailo-8 重复单图像推理测试 ===")
    print(f"图像路径: {image_path}")
    print(f"重复次数: {num_repeats}")
    
    params = VDevice.create_params()
    params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
    
    # 创建VDevice
    with VDevice(params) as vdevice:
        # 加载HEF模型
        infer_model = vdevice.create_infer_model('/xel/yolov11s.hef')
        
        # 配置并创建推理模型
        with infer_model.configure() as configured_infer_model:
            # 加载图像并预处理
            image = cv2.imread(image_path)
            if image is not None:
                print(f"成功加载图像: {image_path}")
                
                # 获取模型输入形状
                input_shape = infer_model.input().shape
                target_height, target_width = input_shape[0], input_shape[1]
                print(f"模型输入尺寸: {target_height} x {target_width}")
                print(f"原始图像尺寸: {image.shape[0]} x {image.shape[1]}")
                
                # 调整大小并转换色彩空间
                image = cv2.resize(image, (target_width, target_height))
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
                processed_image = image.astype(np.uint8)
                
                print("✓ 图像预处理完成")
            else:
                print(f"⚠️ 无法加载图像: {image_path}")
                print("使用随机数据...")
                processed_image = np.random.randint(0, 255, size=infer_model.input().shape, dtype=np.uint8)
            
            # 创建绑定
            bindings = configured_infer_model.create_bindings()
            
            # 设置输入缓冲区
            bindings.input().set_buffer(processed_image)
            
            # 设置输出缓冲区
            output_buffer = np.empty(infer_model.output().shape).astype(np.float32)
            bindings.output().set_buffer(output_buffer)
            
            # 预热
            print("进行预热推理...")
            configured_infer_model.run([bindings], timeout_ms)
            
            # 记录多次运行的时间
            num_runs = 10
            all_run_times = []
            
            print(f"\n开始重复单图像推理...")
            
            for run in range(num_runs):
                run_times = []
                start_total = time.time()
                
                for i in range(num_repeats):
                    start_time = time.time()
                    configured_infer_model.run([bindings], timeout_ms)
                    end_time = time.time()
                    time_ms = (end_time - start_time) * 1000
                    run_times.append(time_ms)
                
                end_total = time.time()
                total_time = (end_total - start_total) * 1000
                
                all_run_times.append(run_times)
                print(f"运行 {run+1}/{num_runs}: 总时间 {total_time:.2f} ms, 平均 {total_time/num_repeats:.2f} ms/图像")
            
            # 计算统计数据
            all_times = np.array(all_run_times).flatten()
            avg_single_time = np.mean(all_times)
            min_single_time = np.min(all_times)
            std_dev_single = np.std(all_times)
            
            # 计算总时间统计
            total_times = [sum(run) for run in all_run_times]
            avg_total_time = np.mean(total_times)
            min_total_time = np.min(total_times)
            std_dev_total = np.std(total_times)
            
            print(f"\n✓ 重复单图像推理完成")
            print(f"单次推理统计:")
            print(f"  平均时间: {avg_single_time:.2f} ms")
            print(f"  最快时间: {min_single_time:.2f} ms")
            print(f"  时间标准差: {std_dev_single:.2f} ms")
            
            print(f"\n总体统计 ({num_repeats}次推理):")
            print(f"  平均总时间: {avg_total_time:.2f} ms")
            print(f"  最快总时间: {min_total_time:.2f} ms")
            print(f"  时间标准差: {std_dev_total:.2f} ms")
            print(f"  平均每个实例时间: {avg_total_time / num_repeats:.2f} ms")
            print(f"  理论最大FPS: {num_repeats * 1000 / min_total_time:.2f}")
            print(f"  平均FPS: {num_repeats * 1000 / avg_total_time:.2f}")
            
            return {
                'method': 'single_repeated',
                'repeats': num_repeats,
                'avg_single_time': avg_single_time,
                'min_single_time': min_single_time,
                'std_dev_single': std_dev_single,
                'avg_total_time': avg_total_time,
                'min_total_time': min_total_time,
                'std_dev_total': std_dev_total,
                'avg_per_instance': avg_total_time / num_repeats,
                'max_fps': num_repeats * 1000 / min_total_time,
                'avg_fps': num_repeats * 1000 / avg_total_time
            }


def compare_methods():
    """比较批处理和重复单图像处理的性能"""
    batch_size = 4
    num_repeats = 4
    
    # 运行测试
    batch_results = batch_inference(batch_size)
    single_results = single_inference_repeated(num_repeats)
    
    # 对比结果
    print("\n\n========== 性能对比 ==========")
    print(f"批处理 vs 重复单图像 (均处理 {batch_size} 张图像)")
    print("\n平均总时间:")
    print(f"  批处理:     {batch_results['avg_time']:.2f} ms")
    print(f"  重复单图像: {single_results['avg_total_time']:.2f} ms")
    print(f"  速度提升:   {single_results['avg_total_time'] / batch_results['avg_time']:.2f}x")
    
    print("\n最快总时间:")
    print(f"  批处理:     {batch_results['min_time']:.2f} ms")
    print(f"  重复单图像: {single_results['min_total_time']:.2f} ms")
    print(f"  速度提升:   {single_results['min_total_time'] / batch_results['min_time']:.2f}x")
    
    print("\n平均每实例时间:")
    print(f"  批处理:     {batch_results['avg_per_instance']:.2f} ms")
    print(f"  重复单图像: {single_results['avg_per_instance']:.2f} ms")
    print(f"  速度提升:   {single_results['avg_per_instance'] / batch_results['avg_per_instance']:.2f}x")
    
    print("\n平均FPS:")
    print(f"  批处理:     {batch_results['avg_fps']:.2f}")
    print(f"  重复单图像: {single_results['avg_fps']:.2f}")
    print(f"  性能比:     {batch_results['avg_fps'] / single_results['avg_fps']:.2f}x")
    
    print("\n理论最大FPS:")
    print(f"  批处理:     {batch_results['max_fps']:.2f}")
    print(f"  重复单图像: {single_results['max_fps']:.2f}")
    print(f"  性能比:     {batch_results['max_fps'] / single_results['max_fps']:.2f}x")
    
    print("\n时间标准差:")
    print(f"  批处理:     {batch_results['std_dev']:.2f} ms")
    print(f"  重复单图像: {single_results['std_dev_total']:.2f} ms")
    
    print("\n========== 总结 ==========")
    if batch_results['avg_fps'] > single_results['avg_fps']:
        print(f"✅ 批处理 比 重复单图像处理 快 {batch_results['avg_fps'] / single_results['avg_fps']:.2f} 倍")
        print("💡 批处理减少了API调用开销并优化了硬件利用率")
    else:
        print(f"❗️ 重复单图像处理 比 批处理 快 {single_results['avg_fps'] / batch_results['avg_fps']:.2f} 倍")
        print("💡 这种情况比较罕见，可能是由于某些硬件或驱动因素造成的")
    
    print("\n推荐:")
    if batch_results['avg_fps'] > single_results['avg_fps']:
        print("👉 使用批处理方式来获得最佳性能")
        print("👉 尝试增加批大小以进一步提高性能")
    else:
        print("👉 对这个特定模型，单图像重复处理更有效")
        print("👉 考虑检查批处理实现是否有优化空间")


if __name__ == "__main__":
    compare_methods()
# 1. 尝试使用 'find' 命令查找 libhailort.so 文件
HAILO_LIB_PATH=$(find /usr /opt /home -name 'libhailort.so*' 2>/dev/null | grep -v 'cmake' | head -n 1 | xargs dirname)

echo "--- HailoRT Library Search Result ---"

if [ -n "$HAILO_LIB_PATH" ]; then
    echo "✅ HailoRT C++ 库路径找到: $HAILO_LIB_PATH"
    echo "---"
    echo "💡 建议操作: 设置 LD_LIBRARY_PATH"
    
    # 2. 输出设置 LD_LIBRARY_PATH 的命令 (仅供复制粘贴)
    echo "请在您的虚拟环境激活后运行以下命令，或将其添加到您的虚拟环境激活脚本中:"
    echo "export LD_LIBRARY_PATH=\$LD_LIBRARY_PATH:$HAILO_LIB_PATH"
    
    # 3. 检查当前 LD_LIBRARY_PATH 是否已包含该路径
    if [[ ":$LD_LIBRARY_PATH:" == *":$HAILO_LIB_PATH:"* ]]; then
        echo "✅ 当前 LD_LIBRARY_PATH 已包含该路径。"
    else
        echo "⚠️ 当前 LD_LIBRARY_PATH 似乎缺少该路径。"
    fi
else
    echo "❌ 警告: 未能找到 'libhailort.so' 文件。请检查 HailoRT SDK 是否正确安装。"
fi

echo "-------------------------------------"
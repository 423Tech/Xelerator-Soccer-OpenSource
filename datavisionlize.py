import matplotlib.pyplot as plt
import math

# 假设你有以下数据结构
data = [[],[2271.975, 62.58864, 2257.375, 2259.9, 2250.609, 2246.352, 205.9093, 206.7702, 205.3073, 205.9765, 205.5863, 206.1245, 206.5952, 206.9977, 207.7888, 206.9953, 207.6802, 207.439, 205.9093, 206.7702, 205.3073, 205.9765, 205.5863, 206.1245, 206.5952, 206.9977, 207.7888, 206.9953, 207.6802, 207.439, 205.9093, 206.7702, 205.3073, 205.9765, 205.5863, 206.1245, 206.5952, 206.9977, 207.7888, 206.9953, 207.6802, 207.439, 206.9953, 207.439, 858.7335, 868.0794, 875.7299, 206.9953, 2282.417, 2276.356, 2272.342, 2267.507, 2263.815, 2258.356, 2255.064, 2258.098, 2250.328, 2246.355, 2243.667, 2241.277, 2235.198, 2232.97, 2229.833, 2225.02, 2219.533, 2215.373, 2214.528, 2200.387, 206.9953, 2282.417, 2276.356, 2272.342, 2267.507, 2263.815, 2258.356, 2255.064, 2258.098, 2250.328, 2246.355, 2243.667, 2241.277, 2235.198, 2232.97, 2229.833, 2225.02, 2219.533, 2215.373, 2214.528, 2200.387, 206.9953, 91.7665]]

for i in range(len(data[1])):
    data[0].append(i)

# lRawDists = [[],[],[],[]]
# lAngles = [[],[],[],[]]
# lCache = [0,0,0,0]

# for i in range(len(data[0])):
#     # y方向 sin 270-90
#     # print(i)
#     if data[1][i] < 3000:
#         if 90 < data[0][i] < 270:
#             lAngles[0].append(data[0][i])
#             lRawDists[0].append(data[1][i]*abs(math.cos(abs(math.radians(data[0][i])))))
#         else:
#             lAngles[2].append(data[0][i])
#             lRawDists[2].append(data[1][i]*abs(math.cos(abs(math.radians(data[0][i])))))
#         # x方向 sin 0-180
#         if 0 < data[0][i] < 180:
#             lAngles[1].append(data[0][i])
#             lRawDists[1].append(data[1][i]*abs(math.sin(abs(math.radians(data[0][i])))))
#         else:
#             lAngles[3].append(data[0][i])
#             lRawDists[3].append(data[1][i]*abs(math.sin(abs(math.radians(data[0][i])))))

MetaData = [
    [[],[]],  # 第一组数据: x1 = [1, 2, 3], y1 = [4, 5, 6]
    [[],[]],  # 第一组数据: x1 = [1, 2, 3], y1 = [4, 5, 6]
    [[],[]],  # 第一组数据: x1 = [1, 2, 3], y1 = [4, 5, 6]
    [[],[]],  # 第一组数据: x1 = [1, 2, 3], y1 = [4, 5, 6]
    [[],[]],  # 第一组数据: x1 = [1, 2, 3], y1 = [4, 5, 6]
    [[],[]],  # 第一组数据: x1 = [1, 2, 3], y1 = [4, 5, 6]
    [[],[]],  # 第一组数据: x1 = [1, 2, 3], y1 = [4, 5, 6]
    [[],[]],  # 第一组数据: x1 = [1, 2, 3], y1 = [4, 5, 6]
]

# for i in range(len(lRawDists)):
#     for j in range(len(lRawDists[i])):
#                 MetaData[i][0].append(lAngles[i][j])
#                 MetaData[i][1].append(lRawDists[i][j])
#                 lCache[i] = lRawDists[i][j]

# for i in range(len(lRawDists)):
#     for j in range(len(lRawDists[i])):
#         if (0 <abs(lRawDists[i][j]-lRawDists[i][j-1]) < -100):
#             # if :
#                 MetaData[i+4][0].append(lAngles[i][j])
#                 MetaData[i+4][1].append(lRawDists[i][j])
#                 lCache[i] = lRawDists[i][j]
#         else:
#             lCache[i] = lRawDists[i][j]

# for i in range(len(data)):
#     for j in range(len(data[i])):
#         if (0 <abs(data[i][j]-data[i][j-1]) < 10):
#             # if :
#                 MetaData[i][0].append(data[0][j])
#                 MetaData[i][1].append(data[1][j])
    
# print(len(MetaData[7][0]))
# print(len(MetaData[0][1]))

# 假设你有以下数据结构，表示三组数据

# 定义不同的颜色
colors = ['r',"y", "o","p" ,'g', 'b',"pink","cryan"]  # 'r' = 红色, 'g' = 绿色, 'b' = 蓝色

# 创建图形
plt.figure()

# 遍历每组数据并绘制
# for i, (x, y) in enumerate(data):
plt.scatter(data[0], data[1], label=f"Group {i+1}")

# 添加标题和标签
plt.title("Scatter Plot with Multiple Groups")
plt.xlabel("X-axis")
plt.ylabel("Y-axis")

# 显示图例
plt.legend()

# 显示图形
plt.show()

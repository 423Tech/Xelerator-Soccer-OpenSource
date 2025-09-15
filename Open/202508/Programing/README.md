<center>
<img src="https://github.com/423Tech/RoboCupJuniorModels/blob/c7cd00d63be94a02cbed2f1108fe58e916d54725/.readme/images/logo-white.png" width=300px>

# Xelerator Soccer Team Readme
</center>

## 游戏规则
https://github.com/423Tech/RoboCupJuniorModels/blob/main/.readme/pdf/rules.pdf

## 机器人结构
<p align="center"><img src="https://github.com/423Tech/RoboCupJuniorModels/blob/c7cd00d63be94a02cbed2f1108fe58e916d54725/.readme/images/MetaX.png" width=300px></p>

机器人主要分为三个部分：
1. 上层 **摄像头和雷达**

    #### 摄像头部分

    > 摄像头变换项目地址: https://github.com/XiaoliMEMZ/Pixel2CM

    > 人工智能识别项目地址: https://github.com/XiaoliMEMZ/ArisuIntelligence

    涵盖技术: 人工智能-模型训练 (CS-AI)

    #### 雷达部分:

    <image src="https://github.com/423Tech/RoboCupJuniorModels/blob/c7cd00d63be94a02cbed2f1108fe58e916d54725/.readme/images/Lidar_Example.png?raw=true" width=30%/>

    雷达主要依赖ROS系统进行数据获取。

2. 中层 **主板&通讯**

    >ROS开发板完整项目地址: https://github.com/XiaoliMEMZ/ArisBit (Archieved)

    涵盖技术: 电子工程(EE)

3. 下层 **马达&弹射&盘球**

对应三个职位:
    
    1. 3D模型设计
        例如：机器人组装与维护、机器人装配设计
    2. 电子工程设计
        例如：小型电路板设计、信号线处理、接线
    3. 机器人视觉与定位
        例如：视觉模型改进、雷达定位模型
    4. 攻防策略设计(主要针对游戏规则)


## 基础规则

机器人的方向描述统一以从提手处往下观察，指南针`0˚`为正方向，`90˚`为右侧，`270˚`为左侧
角度系统统一为 `0-360`

### 方向和坐标系统

方向和坐标系统分绝对和相对

<image src="../RoboCupJuniorModels/.readme/images/field.png" width=30%/>

| 名称   |   绝对   |   相对   |
| :----: | :----: | :----: |
| 参考点 | 以球场中圈圆心为原点 | 以机器人中心为原点 |
| 参考方向 | 对方球门中心为正方向 | 指南针0˚为正方向 |


## 基础命名规范
### 所有函数命名必须遵行大驼峰 用英文命名 例如 `ChassisAngle`,`ChasingBall`, etc.
### 所有变量命名必须遵行蛇峰 用英文命名 例如 `my_robot`,`my_position`, etc.
#### 命名前缀

| 名称   |   含义   |
| :----: | :----: |
| rel | 针对相对的角度系统和坐标系 |
| abs | 针对绝对的角度系统和坐标系 |
| dir | 原始数据 |
| _ | class内的变量，不推荐直接读取 |



#### 其他名词

| 名称   |   含义   |
| :----: | :----: |
| Self | 机器人自己 |
| Peer | 队友 |
| Ball | 球 |
| Chassis | 所有机器人底盘(包括队友) |
| Enemy | 敌方机器人底盘 |


## 其他碎碎念
### 通讯
通讯有蓝牙，wifi两种方式 都不稳定，后续会开发uart通讯
通讯函数需要包含`MessageCahce`,`Send`两个核心功能

## ReasonData
### 日志 logger
日志等级分: `info`,`debug`,`warning`,`success`,`error`五个等级
<table>
    <tr>
        <td>info</td>
        <td>记录普通信息 例如球的坐标 自己的坐标等基础数据</td>
    </tr>
    <tr>
        <td>debug</td>
        <td>记录只会在调试阶段用到的变量 例如电机编码器数值</td>
    </tr>
    <tr>
        <td>warning</td>
        <td>记录不符合预期 但是不值得阻塞主程序继续进行的异常情况</td>
    </tr>
    <tr>
        <td>error</td>
        <td>记录不符合预期 必须要阻塞程序/报错之前的所有变量</td>
    </tr>

</table>

### 配置文件
配置文件是json文件，用于存储例如机器人的编号，加载的下位机系统，端口号等每台机器可能不同变量信息
> 具体内容看注释 不再赘述

### 数据库
支援未来
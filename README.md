# Xelerator RoboCup Soccer Readme

## 基础规则
机器人的方向描述统一以从提手处往下观察，指南针`0˚`为正方向，`90˚`为右侧，`270˚`为左侧
角度系统统一为 `0-360`
### 方向和坐标系统
> 方向和坐标系统分绝对和相对
<table>
    <tr>
        <td>绝对</td>
        <td>相对</td>
    </tr>
    <tr>
        <td>以球场中圈圆心为原点，对方球门中心为正方向
        <td>以机器人中心为原点，指南针0˚为正方向
    </tr>
</table>

## 基础命名规范
### 所有命名必须遵行大驼峰 用英文命名 例如 `ChassisAngle`,`ChasingBall`, etc.
>命名前缀
<table>
    <tr>
        <td>rel</td>
        <td>abs</td>
        <td>dir</td>
    </tr>
    <tr>
        <td>针对相对的角度系统和坐标系</td>
        <td>针对绝对的角度系统和坐标系</td>
        <td>原始数据</td>
    </tr>
</table>

> 其他名词
<table>
    <tr>
        <td>Robo</td>
        <td>Peer</td>
        <td>Ball</td>
        <td>Chassis</td>
        <td>Enemy</td>
    </tr>
    <tr>
        <td>机器人自己</td>
        <td>队友</td>
        <td>球</td>
        <td>所有机器人底盘</td>
        <td>敌方机器人底盘</td>
    </tr>
</table>

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
#ifndef __CAR_RTU_H
#define __CAR_RTU_H
#include "stm32f4xx_hal.h"
#include "system.h"	 


#define UART4_RTU_TX_MAX 		30		//串口 RTU 发送 数据段 最大值
#define UART4_RTU_RX_Data_MAX 	12		//串口 RTU 接收 数据段 最大值


#define UART4_RTU_FH_H					0X55	//帧头 高位
#define UART4_RTU_FH_L					0X99	//帧头 低位

#define UART4_RTU_FE_H 					0XAA	//帧尾 高位
#define UART4_RTU_FE_L 					0XCC	//帧尾 低位
//*************************  地址  *************************
#define UART4_RTU_ADDRES_H750 			0X01		//上位机 地址
#define UART4_RTU_ADDRES_F103 			0X02		//F103 地址

#define UART4_RTU_ADDRES_MINE 	UART4_RTU_ADDRES_F103	//当前程序下，我的 地址

//*************************  功能码 F103接收 *************************

//*****************  设置电机参数  *****************
#define UART4_RTU_Function_Speed_PID_1 						0x01		//单独设置 电机1 PID参数
#define UART4_RTU_Function_Speed_PID_2 						0x02		//单独设置 电机2 PID参数
#define UART4_RTU_Function_Speed_PID_3 						0x03		//单独设置 电机3 PID参数
#define UART4_RTU_Function_Speed_PID_4 						0x04		//单独设置 电机4 PID参数
#define UART4_RTU_Function_Set_PWM 							0x05		//一次性设置4个电机的PWM，单位：PWM
#define UART4_RTU_Function_Speed_PID_ALL 					0x06		//统一设置 电机 速度PID参数
#define UART4_RTU_Function_Set_RPM 							0x07		//一次性设置4个电机的转速，单位：RPM
#define UART4_RTU_Function_Encoder_Resolution 				0x08		//配置磁环极对数
#define UART4_RTU_Function_Motor_Reduction_Ratio 			0x09		//配置电机的减速比
#define UART4_RTU_Function_Location_PID_ALL 				0x0A		//统一设置 电机 位置PID参数
#define UART4_RTU_Function_Motor_Type 						0x0B		//配置 电机型号（1：370 ; 2：普通310）

//*****************  设置整车参数  *****************
#define UART4_RTU_Function_Soft_Starter_Set_Time 		0x11		//配置 软启动时间
#define UART4_RTU_Function_Soft_Stop_Set_Time 			0x12		//配置 软停止时间
#define UART4_RTU_Function_Timeout_Set_Time 			0x13		//配置 阻塞时间
#define UART4_RTU_Function_Car_Move_Fix 				0x14		//配置 整车运动过程中，车头修正参数
#define UART4_RTU_Function_Car_Turn_Fix 				0x15		//配置 整车原地旋转过程中，车头修正参数
#define UART4_RTU_Function_Data_Reset 					0x1F		//配置 复位所有参数

//*****************  设置整车移动函数参数  *****************
#define UART4_RTU_Function_Car_Z_Speed					0x21		//配置 整车 车头保持在目标角度，向任意角度运动
#define UART4_RTU_Function_Car_Z_Speed_Time				0x22		//配置 整车 车头保持在目标角度，向任意角度运动一段时间
#define UART4_RTU_Function_Car_XY_Speed					0x23		//配置 整车 车头保持在目标角度，给定xy速度运动，x->车身右侧正，y->车头前正
#define UART4_RTU_Function_Car_Turn						0x24		//配置 整车 车原地旋转角度（角度闭环）
#define UART4_RTU_Function_Car_Location					0x25		//配置 整车 车头保持在目标角度，向任意角度位移 距离
#define UART4_RTU_Function_Car_Stop						0x26		//配置 整车 停止移动
//*************************  功能码 F103发送 *************************

#define UART4_RTU_Function_Responce 					0xF0		//反馈信息


void UART4_RTU_TX_Mesage(u8 function,u8 len,u8 *pData);		//UART4_RTU 数据发送,功能码，数据长度，内容
void UART4_RTU_Buff_Process(void);							//UART4_RTU 数据解析，解析出  功能码，数据位，数据段
void UART4_RTU_Buff_Deal(void);								//RS485 RTU 数据处理(事件处理)

void UART4_RTU_TX_Buff_CLR(void);							//清空RTU发送buff
void UART4_RTU_RX_Data_Buff_CLR(void);						//清空 RTU 数据段 的数据
void UART4_RTU_Function_Clear(void);						//UART4_RTU 接收到正确功能码后，清除一些标志位


void UART4_RTU_SET_PWM_Data(u8 *buf);						//UART4_RTU 将接收到的 PWM 转化（因为放大了）
void UART4_RTU_Speed_PID_Data(u8 *buf);						//UART4_RTU 将接收到的 速度PID数据 转化（因为放大了）
void UART4_RTU_SET_RPM_Data(u8 *buf);						//UART4_RTU 将接收到的 转速 转化（因为放大了）
void UART4_RTU_Encoder_Resolution(u8 *buf);					//UART4_RTU 设置编码器磁环 极对数
void UART4_RTU_Motor_Reduction_Ratio(u8 *buf);				//UART4_RTU 设置电机 减速比
void UART4_RTU_Soft_Starter_Set_Time(u8 *buf);				//UART4_RTU 设置软启动时间
void UART4_RTU_Soft_Stop_Set_Time(u8 *buf);					//UART4_RTU 设置软停止时间
void UART4_RTU_Car_Move_Timeout(u8 *buf);					//UART4_RTU 设置阻塞时间 
void UART4_RTU_Location_PID_Data(u8 *buf);					//UART4_RTU 将接收到的 位置PID数据 转化（因为放大了）	
void UART4_RTU_Motor_Type(u8 *buf);							//UART4_RTU 设置电机型号（1：370 ; 2：普通310）
	

void UART4_RTU_Car_Move_Fix_Value(u8 *buf);					//UART4_RTU 设置整车运动过程中，车头修正参数
void UART4_RTU_Car_Turn_Fix_Value(u8 *buf);					//UART4_RTU 设置整车原地旋转过程中，车头修正参数
void UART4_RTU_Car_Reset_Value(u8 *buf);					//UART4_RTU 复位所有参数



void UART4_RTU_Car_Keep_Angle_Z_Speed_Move(u8 *buf);		//UART4_RTU 整车控制，车头保持在目标角度，向任意角度运动
void UART4_RTU_Car_Keep_Angle_Z_Speed_Move_Time(u8 *buf);	//UART4_RTU 整车控制，车头保持在目标角度，向任意角度运动一段时间
void UART4_RTU_Car_Keep_Angle_XY_Speed_Move(u8 *buf);		//UART4_RTU 整车控制，车头保持在目标角度，给定xy速度运动，x->车身右侧正，y->车头前正
void UART4_RTU_Car_Turn(u8 *buf);							//UART4_RTU 整车控制，车原地旋转角度（角度闭环）
void UART4_RTU_Car_Keep_Angle_Location_Move(u8 *buf);		//UART4_RTU 整车控制，车头保持在目标角度，向任意角度位移 距离
void UART4_RTU_Car_Stop(u8 *buf);							//UART4_RTU 整车控制，停止移动



void UART4_RTU_Car_Move(void);						//UART4_RTU 的功能码，对应 车移动的方式。在F103主程序大循环里用


void UART4_RTU_Send_Responce(void);				//UART4_RTU 发送 返回信号 to 上位机
void UART4_RTU_Send_Message(void);					//UART4_RTU 发送信息 to 上位机



#endif

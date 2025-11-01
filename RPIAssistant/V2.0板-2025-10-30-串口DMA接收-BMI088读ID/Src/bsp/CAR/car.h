#ifndef __CAR_H
#define __CAR_H

#include "stm32f4xx_hal.h"
#include "system.h"

#define PI 3.1415926535f  

#define Car_Soft_Starter_Default_Value 				500			//整车参数，默认值，软启动 时间
#define Car_Soft_Stop_Default_Value 				500			//整车参数，默认值，软停止 时间
#define Car_Keep_Angle_Move_Default_Fix_k 			2.1			//整车参数，默认值，移动过程中，需要校正车头的，k
#define Car_Keep_Angle_Move_Default_Fix_b 			10			//整车参数，默认值，移动过程中，需要校正车头的，b
#define Car_Keep_Angle_Turn_Default_Fix_k 			2			//整车参数，默认值，原地旋转过程中，需要校正车头的，k
#define Car_Keep_Angle_Turn_Default_Fix_b 			10			//整车参数，默认值，原地旋转过程中，需要校正车头的，b
#define Car_Keep_Angle_Turn_Default_Angle_range 	1			//整车参数，默认值，原地旋转过程中，保持目标角度 阈值
#define Car_Keep_Angle_Turn_Default_keep_time 		200			//整车参数，默认值，原地旋转过程中，保持目标角度 时间

#define Car_Move_Default_Timeout 					0XFFFF		//整车参数，默认值，超时时间


void Car_Stop(void);	//车停止运动
void Car_Keep_Angle_Z_Speed_Move(float aim_angle,float move_angle,int speed);	//	车头保持在目标角度，向任意角度运动
u8 Car_Keep_Angle_Z_Speed_Move_Time(float aim_angle,float move_angle,int speed,u32 time);	//车头保持在目标角度，向任意角度运动 一段时间
void Car_Keep_Angle_XY_Speed_Move(float aim_angle,int vx,int vy);	//	车头保持在目标角度，给定xy速度运动，x->车身右侧正，y->车头前正
void Car_Straight(float aim_angle,int speed);						//车保持直线运动（角度闭环）,车头一直向前，转向加运动，先转向后运动
u8 Car_Straight_Time(int aim_angle,int speed,u32 time);				//车保持直线运动时间（角度闭环）
u8 Car_Turn(float aim_angle);									//车原地旋转角度（角度闭环）
void Car_Cross(float aim_angle,int speed);							//车横向移动（角度闭环）
u8 Car_Cross_Time(float aim_angle,int speed,u32 time);				//车横向移动时间（角度闭环）
u8 Car_Keep_Angle_Location_Move(float aim_angle,float move_angle,int speed,int location);	//车头保持在目标角度，向任意角度位移 距离
void Car_Move_Flags_Clear(void);	//车运动，所有标志位 清零 
#endif









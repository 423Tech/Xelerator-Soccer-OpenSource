#ifndef __PID_H
#define	__PID_H

#include "stm32f4xx_hal.h"
#include "system.h"

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

//**************  速度PID 默认 参数  **************  
#define PID_Speed_P_Default_Value 	3
#define PID_Speed_I_Default_Value 	0.2
#define PID_Speed_D_Default_Value 	1
//**************  位置PID 默认 参数  ************** 
#define PID_Location_P_Default_Value 	0.9
#define PID_Location_I_Default_Value 	0.045
#define PID_Location_D_Default_Value 	0.5

typedef struct
{
	float target_val[5];   //目标值
	float err[5];          //偏差值
	float err_last[5];     //上一个偏差值
	float Kp,Ki,Kd;     //比例、积分、微分系数
	float integral[5];     //积分值
	float output_val[5];   //输出值
}PID;



extern PID PID_Location;
extern PID PID_Speed;

void  PID_param_init(void);
void  Pid_Set_Target(u8 ch,PID *pid, float temp_val);				//PID 设置目标值
float Pid_Get_Target(u8 ch,PID *pid);								//PID 获取目标值
void  PID_Set_p_i_d(PID *pid, float p, float i, float d);	//PID 设置参数 p、i、d
float PID_Location_Realize(u8 ch,PID *pid, float actual_val);
float PID_Speed_Realize(u8 ch,PID *pid, float actual_val);
	









#endif

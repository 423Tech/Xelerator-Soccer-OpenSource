#include "motor.h"
#include "pid.h"
#include "string.h"		
#include <stdarg.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "usart.h"
#include "car.h"
#include "IMU.h"
#include "pid.h"
#include <math.h>
#include <stdarg.h>              // USART使用
#include <stdio.h>               // USART使用
#include <stdlib.h>

u8 Motor_Control_Mode;			//电机控制方式。1：速度控制 ； 2：位置控制

//**********************************  大类： 速度 控制方式  **********************************
//**********************************  大类： 速度 控制方式  **********************************
//**********************************  大类： 速度 控制方式  **********************************
extern u8 TIM6_Car_move_Start;					//定时器 - 车运动时间函数 开始
extern u32 TIM6_Car_move_Count;					//定时器 - 车运动时间函数 计数
extern u8 TIM6_Car_move_Timeout_Start;			//定时器 - 车运动超时时间函数 开始
extern u32 TIM6_Car_move_Timeout_Count;			//定时器 - 车运动超时时间函数 计数
extern u8 TIM6_Car_Soft_Stop_Start[5];			//定时器 - 整车软停止 开始
extern u32 TIM6_Car_Soft_Stop_Count[5];			//定时器 - 整车软停止 计数
int Motor_LF_Speed;
int Motor_RF_Speed;
int Motor_LB_Speed;
int Motor_RB_Speed;
int Motor_Location[5];		//电机位置1~4对应，左前，左后，右前，右后
float Motor_Speed[5]={0.0f,0.0f,0.0f,0.0f,0.0f};			//电机速度1~4对应，左前，左后，右前，右后
int Motor_Rad_Correct;			//旋转修正速度
float Angle_Error=0.0f;			//误差角度 = 实际角度 - 目标角度
float Angle_Error_Correct=0.0f;	//修正过的误差角度 = （实际角度 - 目标角度 +180.0f ）/360 -180.0f ,将角度差映射到 [0, 360),- 180.0f 再偏移回 [-180.0f, 180.0f] 范围

extern float Compass_Value;  		//用户用的角度（正北修正后）
extern u8 TIM6_Car_Soft_Starter_Start[5];		//定时器 - 整车软启动 开始
extern u32 TIM6_Car_Soft_Starter_Count[5];		//定时器 - 整车软启动 计数
u16 Car_Soft_Starter_Time_Set_Value=Car_Soft_Starter_Default_Value;		//车移动，设定的 软启动时间，单位（ms）
u16 Car_Soft_Stop_Time_Set_Value=Car_Soft_Stop_Default_Value;			//车移动，设定的 软停止时间，单位（ms）
u16 Car_Move_Timeout_Set_Value=Car_Move_Default_Timeout;				//车移动，设定的 阻塞时间，单位（ms），位移时间、位移距离函数适用
u8 Car_Soft_Start_Flag;							//车移动，软启动标志位。0：未完成 ； 1：完成
u8 Car_Soft_Stop_Flag;							//车移动，软停止标志位。0：未开始软停 ； 1：开始软停
u32 Car_Move_Aim_Time;							//车运动“一段时间”的函数内，获取的时间参数。
//*****************************  车停止运动 *****************************
void Car_Stop(void)
{
	Motor_Control_Mode=1;				//电机控制方式。1：速度控制 ； 2：位置控制
	Set_Target_Expect_Speed(0,0,0,0);	//一次性设置4个电机的PWM，单位：RPM
	Car_Move_Flags_Clear();				//车运动，所有标志位 清零 
}
float Car_Keep_Angle_Move_Set_Fix_k=Car_Keep_Angle_Move_Default_Fix_k;				//统一设置，移动过程中，需要校正车头的，k
float Car_Keep_Angle_Move_Set_Fix_b=Car_Keep_Angle_Move_Default_Fix_b;				//统一设置，移动过程中，需要校正车头的，k
float Car_Keep_Angle_Turn_Set_Fix_k=Car_Keep_Angle_Turn_Default_Fix_k;				//统一设置，原地旋转过程中，需要校正车头的，k
float Car_Keep_Angle_Turn_Set_Fix_b=Car_Keep_Angle_Turn_Default_Fix_b;				//统一设置，原地旋转过程中，需要校正车头的，k
float Car_Keep_Angle_Turn_Set_Angle_range=Car_Keep_Angle_Turn_Default_Angle_range;	//统一设置，原地旋转过程中，保持目标角度 阈值
//float Car_Keep_Angle_Turn_Set_Angle_range=0;	//统一设置，原地旋转过程中，保持目标角度 阈值
u16 Car_Keep_Angle_Turn_Set_keep_time=Car_Keep_Angle_Turn_Default_keep_time;		//统一设置，原地旋转过程中，保持目标角度 时间

//*****************************  车头保持在目标角度，向任意角度运动 *****************************
void Car_Keep_Angle_Z_Speed_Move(float aim_angle,float move_angle,int speed)	//	车头保持在目标角度，向任意角度运动
{
	u8 i;
	Motor_Control_Mode=1;			//电机控制方式。1：速度控制 ； 2：位置控制
	TIM6_Car_Soft_Starter_Start[0]=1;				//定时器 - 整车软启动 开始
	Angle_Error=Compass_Value-aim_angle;//Angle_Error = 实际角度 - 目标角度
	Angle_Error_Correct = Angle_Error - 360.0f * floor((Angle_Error + 180.0f) / 360.0f);//修正过的误差角度 = （实际角度 - 目标角度 +180.0f ）/360 -180.0f ,将角度差映射到 [0, 360),- 180.0f 再偏移回 [-180.0f, 180.0f] 范围
	if( Angle_Error_Correct<0)
		Motor_Rad_Correct =  Car_Keep_Angle_Move_Set_Fix_k*Angle_Error_Correct-Car_Keep_Angle_Move_Set_Fix_b ;
	else if(Angle_Error_Correct>0)
		Motor_Rad_Correct =  Car_Keep_Angle_Move_Set_Fix_b*Angle_Error_Correct+Car_Keep_Angle_Move_Set_Fix_b ;
	else
		Motor_Rad_Correct=0;
	Motor_Speed[1]=roundf( (float)( (speed*( cos((move_angle-aim_angle)*PI/180.0f) + sin((move_angle-aim_angle)*PI/180.0f) ) )  ) ) ;	
	Motor_Speed[2]=roundf( (float)( (speed*( cos((move_angle-aim_angle)*PI/180.0f) - sin((move_angle-aim_angle)*PI/180.0f) ) )  ) ) ;
	Motor_Speed[3]=roundf( (float)( (speed*( cos((move_angle-aim_angle)*PI/180.0f) - sin((move_angle-aim_angle)*PI/180.0f) ) )  ) ) ;
	Motor_Speed[4]=roundf( (float)( (speed*( cos((move_angle-aim_angle)*PI/180.0f) + sin((move_angle-aim_angle)*PI/180.0f) ) )  ) ) ;

	//********************  软启动过程  ********************
	if(Car_Soft_Start_Flag==0)
	{
		if(TIM6_Car_Soft_Starter_Count[0]<Car_Soft_Starter_Time_Set_Value/10)
		{
			for(i=1;i<5;i++)
				Motor_Speed[i]=(float)TIM6_Car_Soft_Starter_Count[0]/(Car_Soft_Starter_Time_Set_Value/10) *Motor_Speed[i];
		}
		else
		{
			TIM6_Car_Soft_Starter_Start[0]=0;				//定时器 - 整车软启动 开始
			TIM6_Car_Soft_Starter_Count[0]=0;				//定时器 - 整车软启动 计数
			Car_Soft_Start_Flag=1;					//车移动，软启动标志位。0：未完成 ； 1：完成
		}			
	}
	//********************  软停止过程  ********************
	else if(Car_Soft_Stop_Flag == 1)//车移动，软停止标志位。0：未开始软停 ； 1：开始软停
	{
		for(i=1;i<5;i++)
			Motor_Speed[i]=(float) (1-(float)TIM6_Car_Soft_Stop_Count[0]/(Car_Soft_Stop_Time_Set_Value/10) ) *Motor_Speed[i];
	}
	
	Motor_LF_Speed=roundf(Motor_Speed[1])- Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Motor_LB_Speed=roundf(Motor_Speed[2])- Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Motor_RF_Speed=roundf(Motor_Speed[3])+ Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Motor_RB_Speed=roundf(Motor_Speed[4])+ Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Set_Target_Expect_Speed(Motor_LF_Speed,Motor_LB_Speed,Motor_RF_Speed,Motor_RB_Speed);//一次性设置4个电机的PWM，单位：RPM	
}
//*****************************  车头保持在目标角度，向任意角度运动 一段时间 *****************************
u8 Car_Move_Aim_Time_State_Flag;	//车运动“一段时间”函数返回状态 0：空闲（完成）；2：正在运行 ； 3：完成
u8 Car_Keep_Angle_Z_Speed_Move_Time(float aim_angle,float move_angle,int speed,u32 time)	//车头保持在目标角度，向任意角度运动 一段时间
{
	if(Car_Move_Aim_Time_State_Flag==0)		//车运动“一段时间”函数返回状态 0：空闲（完成）；2：正在运行 ； 3：完成
	{
		Car_Move_Flags_Clear();				//车运动，所有标志位 清零 
		Car_Move_Aim_Time_State_Flag=2;		//车运动“一段时间”函数返回状态 0：空闲（完成）；2：正在运行 ； 3：完成
		Car_Move_Aim_Time=time;				//车运动“一段时间”的函数内，获取的时间参数。
		TIM6_Car_move_Count=0;				//定时器 - 车运动时间函数 计数
		TIM6_Car_move_Start=1;				//定时器 - 车运动时间函数 开始
		TIM6_Car_move_Timeout_Count=0;			//定时器 - 车运动超时时间函数 计数
		TIM6_Car_move_Timeout_Start=1;		//定时器 - 车运动超时时间函数 开始
	}
	//********************  判断一下，在给定运行时间范围内，是否能兼顾到 软停  ********************
	if(Car_Move_Aim_Time>(Car_Soft_Starter_Time_Set_Value+ Car_Soft_Stop_Time_Set_Value))
	{
		//********************  可以开始软停了  ********************
		if( TIM6_Car_move_Count*10 > (Car_Move_Aim_Time - Car_Soft_Stop_Time_Set_Value))
		{
			Car_Soft_Stop_Flag=1;				//车移动，软停止标志位。0：未开始软停 ； 1：开始软停
			TIM6_Car_Soft_Stop_Start[0]=1;			//定时器 - 整车软停止 开始
		}
	}
	//********************  记录运行时间  ******************** 
	if(Car_Move_Aim_Time > TIM6_Car_move_Count*10 )
	{ 
		Car_Keep_Angle_Z_Speed_Move(aim_angle,move_angle,speed);	//车头一直向前，转向加运动，先转向后运动
	}
	else 
	{
		Car_Move_Aim_Time_State_Flag=3;		//车运动“一段时间”函数返回状态 0：空闲（完成）；2：正在运行 ； 3：完成
		Car_Stop();							//车停止运动
	}
	//********************  超时  ******************** 
	if( TIM6_Car_move_Timeout_Count*10 > Car_Move_Timeout_Set_Value)
	{
		Car_Move_Aim_Time_State_Flag=4;		//车运动“一段时间”函数返回状态 0：空闲（完成）；2：正在运行 ； 3：完成
		Car_Stop();							//车停止运动
	}
	
	return Car_Move_Aim_Time_State_Flag;	//车运动“一段时间”函数返回状态 0：空闲（完成）；2：正在运行 ； 3：完成
}
//*****************************   车头保持在目标角度，给定xy速度运动，x->车身右侧正，y->车头前正 *****************************
void Car_Keep_Angle_XY_Speed_Move(float aim_angle,int vx,int vy)	//	车头保持在目标角度，给定xy速度运动，x->车身右侧正，y->车头前正
{
	u8 i;
	Motor_Control_Mode=1;			//电机控制方式。1：速度控制 ； 2：位置控制
	TIM6_Car_Soft_Starter_Start[0]=1;				//定时器 - 整车软启动 开始
	Angle_Error=Compass_Value-aim_angle;//Angle_Error = 实际角度 - 目标角度
	Angle_Error_Correct = Angle_Error - 360.0f * floor((Angle_Error + 180.0f) / 360.0f);//修正过的误差角度 = （实际角度 - 目标角度 +180.0f ）/360 -180.0f ,将角度差映射到 [0, 360),- 180.0f 再偏移回 [-180.0f, 180.0f] 范围
	if( Angle_Error_Correct<0)
		Motor_Rad_Correct =  Car_Keep_Angle_Move_Set_Fix_k*Angle_Error_Correct-Car_Keep_Angle_Move_Set_Fix_b ;
	else if(Angle_Error_Correct>0)
		Motor_Rad_Correct =  Car_Keep_Angle_Move_Set_Fix_b*Angle_Error_Correct+Car_Keep_Angle_Move_Set_Fix_b ;
	else
		Motor_Rad_Correct=0;
	Motor_Speed[1]= vx + vy ;	
	Motor_Speed[2]= -vx + vy ;
	Motor_Speed[3]= -vx + vy  + Motor_Rad_Correct ;
	Motor_Speed[4]= vx + vy  + Motor_Rad_Correct ;

	//********************  软启动过程  ********************
	if(Car_Soft_Start_Flag==0)
	{
		if(TIM6_Car_Soft_Starter_Count[0]<Car_Soft_Starter_Time_Set_Value/10)
		{
			for(i=1;i<5;i++)
				Motor_Speed[i]=(float)TIM6_Car_Soft_Starter_Count[0]/(Car_Soft_Starter_Time_Set_Value/10) *Motor_Speed[i];
		}
		else
		{
			TIM6_Car_Soft_Starter_Start[0]=0;				//定时器 - 整车软启动 开始
			TIM6_Car_Soft_Starter_Count[0]=0;				//定时器 - 整车软启动 计数
			Car_Soft_Start_Flag=1;							//车移动，软启动标志位。0：未完成 ； 1：完成
		}			
	}
	//********************  软停止过程  ********************
	else if(Car_Soft_Stop_Flag == 1)//车移动，软停止标志位。0：未开始软停 ； 1：开始软停
	{
		for(i=1;i<5;i++)
			Motor_Speed[i]=(float) (1-(float)TIM6_Car_Soft_Stop_Count[0]/(Car_Soft_Stop_Time_Set_Value/10) ) *Motor_Speed[i];
	}
	
	Motor_LF_Speed=roundf(Motor_Speed[1])- Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Motor_LB_Speed=roundf(Motor_Speed[2])- Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Motor_RF_Speed=roundf(Motor_Speed[3])+ Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Motor_RB_Speed=roundf(Motor_Speed[4])+ Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	
	Set_Target_Expect_Speed(Motor_LF_Speed,Motor_LB_Speed,Motor_RF_Speed,Motor_RB_Speed);//一次性设置4个电机的PWM，单位：RPM	
}

float Last_Aim_Angle=0.0f;//在其他转向函数、直线运动函数中给的目标角度值
//*****************************  车保持直线运动（角度闭环） *****************************
void Car_Straight(float aim_angle,int speed)//车头一直向前，转向加运动，先转向后运动
{
	Car_Keep_Angle_Z_Speed_Move(aim_angle,aim_angle,speed);	//	车头保持在目标角度，向任意角度运动
}

//*****************************  车保持直线运动时间（角度闭环） *****************************
u8 Car_Straight_Time(int aim_angle,int speed,u32 time)//车直行一定时间
{
	return Car_Keep_Angle_Z_Speed_Move_Time(aim_angle,aim_angle,speed,time);	//车头保持在目标角度，向任意角度运动 一段时间
}

u8 Car_Turn_State_Flag;			//旋转返回状态标志 。0：空闲（手动置位） ；1：激活功能 ；2：正在进行旋转；3：完成任务
//*****************************  车原地旋转角度（角度闭环） *****************************
float Car_Keep_Angle_Turn_Set_Fix_k;		//统一设置，移动过程中，需要校正车头的，k
float Car_Keep_Angle_Turn_Set_Fix_b;		//统一设置，移动过程中，需要校正车头的，k
float test_1=2*30;
float test_2;
float test_3;
	
u8 Car_Turn(float aim_angle)			//转向
{
	test_2 = sinf(test_1*PI/180.0f);
	test_3 = asinf(test_2)*180.0f/PI;
	
	
	if( Car_Turn_State_Flag == 0)
	{
		Car_Move_Flags_Clear();				//车运动，所有标志位 清零 
		Car_Turn_State_Flag=2;				//旋转返回状态标志 。0：空闲（手动置位） ；2：正在进行旋转；3：完成任务
		TIM6_Car_move_Count=0;				//定时器 - 车运动时间函数 计数
		TIM6_Car_move_Start=1;				//定时器 - 车运动时间函数 开始
		TIM6_Car_move_Timeout_Count=0;		//定时器 - 车运动超时时间函数 计数
		TIM6_Car_move_Timeout_Start=1;		//定时器 - 车运动超时时间函数 开始
	}
	Motor_Control_Mode=1;			//电机控制方式。1：速度控制 ； 2：位置控制

	Angle_Error=Compass_Value-aim_angle;//Angle_Error = 实际角度 - 目标角度
	Angle_Error_Correct = Angle_Error - 360.0f * floor((Angle_Error + 180.0f) / 360.0f);//修正过的误差角度 = （实际角度 - 目标角度 +180.0f ）/360 -180.0f ,将角度差映射到 [0, 360),- 180.0f 再偏移回 [-180.0f, 180.0f] 范围
	if( Angle_Error_Correct<0)
		Motor_Rad_Correct =  Car_Keep_Angle_Turn_Set_Fix_k*Angle_Error_Correct-Car_Keep_Angle_Turn_Set_Fix_b ;
	else if(Angle_Error_Correct>0)
		Motor_Rad_Correct =  Car_Keep_Angle_Turn_Set_Fix_k*Angle_Error_Correct+Car_Keep_Angle_Turn_Set_Fix_b ;
	else
		Motor_Rad_Correct=0;
	Motor_LF_Speed= - Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Motor_LB_Speed= - Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Motor_RF_Speed= + Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Motor_RB_Speed= + Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
	Set_Target_Expect_Speed(Motor_LF_Speed,Motor_LB_Speed,Motor_RF_Speed,Motor_RB_Speed);//一次性设置4个电机的PWM，单位：RPM	

	if( fabs(Angle_Error_Correct) < Car_Keep_Angle_Turn_Set_Angle_range)
	{
		if(TIM6_Car_move_Count * 10 > Car_Keep_Angle_Turn_Set_keep_time)
		{
			Car_Turn_State_Flag=3;			//旋转返回状态标志 。0：空闲（手动置位） ；1：激活功能 ；2：正在进行旋转；3：完成任务
			Car_Stop();	
		}
	}
	else
	{
		TIM6_Car_move_Count=0;			//定时器 - 车运动时间函数 计数
		Car_Turn_State_Flag=2;			//旋转返回状态标志 。0：空闲（手动置位） ；1：激活功能 ；2：正在进行旋转；3：完成任务
	}
	//********************  超时  ******************** 
	if( TIM6_Car_move_Timeout_Count*10 > Car_Move_Timeout_Set_Value)
	{
		Car_Move_Aim_Time_State_Flag=4;		//车运动“一段时间”函数返回状态 0：空闲（完成）；2：正在运行 ； 3：完成
		Car_Stop();							//车停止运动
	}
	return Car_Turn_State_Flag;			//旋转返回状态标志 。0：空闲（手动置位） ；1：激活功能 ；2：正在进行旋转；3：完成任务
}
//*****************************  车横向移动（角度闭环） *****************************
void Car_Cross(float aim_angle,int speed)//车横向移动（角度闭环）
{	
	Car_Keep_Angle_Z_Speed_Move(aim_angle-90,aim_angle,speed);	//	车头保持在目标角度，向任意角度运动				
}
//*****************************  车横向移动时间（角度闭环） *****************************
u8 Car_Cross_Time(float aim_angle,int speed,u32 time)//车横移一定时间
{
	return Car_Keep_Angle_Z_Speed_Move_Time(aim_angle-90,aim_angle,speed,time);	//车头保持在目标角度，向任意角度运动 一段时间
}
//**********************************  大类： 位置 控制方式  **********************************
//**********************************  大类： 位置 控制方式  **********************************
//**********************************  大类： 位置 控制方式  **********************************


extern u8 LOC_DEAD_ZONE_Flag[5];					//位置环死区标志位。1：死区了（已经到位置了） ； 0：没死（没到位置）
u8 Car_Keep_Angle_Location_Move_State_Flag;			//位置控制方式中，位置、角度到位了的标志。0：空闲（完成）；1：正在做位置任务:；2：位置完成，正在做原地校正 ； 3：所有动作完成

/*
软启、软停给定的时间，平均映射到速度
软启动和软停止，这里没写的分复杂
原本应该 预计软启、软停时间内 能走的编码器圈数（位移），判断一下，软启是否应该在还没到速度最大值的时候，切换至软停
但是没弄明白，所以就不管 “还没到最大速度就要软停”的情况
*/




extern int Encoder_Location_Now[5];    			//编码器 总计数值，当前时刻
extern int Encoder_Location_Last[5];    		//编码器 总计数值，上一次
extern float Encoder_Total_Resolution;			//编码器总分辨率
int Car_Soft_Stop_Predict_Encoder_Sum[5];		//预计软停的位移脉冲个数

u8 Car_Keep_Angle_Location_Move(float aim_angle,float move_angle,int speed,int location)	//车头保持在目标角度，向任意角度位移 距离
{
	u8 i;
	if(Car_Keep_Angle_Location_Move_State_Flag==0)	//位置控制方式中，位置、角度到位了的标志。0：空闲（手动置位）；1：正在做位置任务:；2：位置完成，正在做原地校正 ； 3：所有动作完成
	{
		Car_Move_Flags_Clear();				//车运动，所有标志位 清零 
		Motor_Control_Mode=2;						//电机控制方式。1：速度控制 ； 2：位置控制
		Car_Keep_Angle_Location_Move_State_Flag=1;	//位置控制方式中，位置、角度到位了的标志。0：空闲（手动置位）；1：正在做位置任务:；2：位置完成，正在做原地校正 ； 3：所有动作完成
		for(i=1;i<5;i++)
		{
			Encoder_Location_Now[i] = 0 ;	//编码器 总计数值，当前时刻,（获取当前的累计值）
			Encoder_Location_Last[i] = 0;							//编码器 总计数值，上一次（更新上次的累计值）
			LOC_DEAD_ZONE_Flag[i]=0;					//位置环死区标志位。1：死区了（已经到位置了） ； 0：没死（没到位置）
		}
		TIM6_Car_move_Start=0;						//定时器 - 车运动时间函数 开始
		TIM6_Car_move_Count=0;						//定时器 - 车运动时间函数 计数
		TIM6_Car_Soft_Starter_Count[0]=0;			//定时器 - 整车软启动 计数
		TIM6_Car_Soft_Starter_Start[0]=1;			//定时器 - 整车软启动 开始	

		Motor_Location[1]=roundf( (float)( (location*( cos((move_angle-aim_angle)*PI/180.0f) + sin((move_angle-aim_angle)*PI/180.0f) ) ) - 0 ) ) ;	
		Motor_Location[2]=roundf( (float)( (location*( cos((move_angle-aim_angle)*PI/180.0f) - sin((move_angle-aim_angle)*PI/180.0f) ) ) - 0 ) ) ;
		Motor_Location[3]=roundf( (float)( (location*( cos((move_angle-aim_angle)*PI/180.0f) - sin((move_angle-aim_angle)*PI/180.0f) ) ) + 0 ) ) ;
		Motor_Location[4]=roundf( (float)( (location*( cos((move_angle-aim_angle)*PI/180.0f) + sin((move_angle-aim_angle)*PI/180.0f) ) ) + 0 ) ) ;
		Set_Target_Expect_Location(Motor_Location[1],Motor_Location[2],Motor_Location[3],Motor_Location[4]);
		TIM6_Car_move_Timeout_Count=0;		//定时器 - 车运动超时时间函数 计数
		TIM6_Car_move_Timeout_Start=1;		//定时器 - 车运动超时时间函数 开始
	}
	
	Angle_Error=Compass_Value-aim_angle;//Angle_Error = 实际角度 - 目标角度
	Angle_Error_Correct = Angle_Error - 360.0f * floor((Angle_Error + 180.0f) / 360.0f);//修正过的误差角度 = （实际角度 - 目标角度 +180.0f ）/360 -180.0f ,将角度差映射到 [0, 360),- 180.0f 再偏移回 [-180.0f, 180.0f] 范围
	if( Angle_Error_Correct<0)
		Motor_Rad_Correct =  Car_Keep_Angle_Move_Set_Fix_k*Angle_Error_Correct-Car_Keep_Angle_Move_Set_Fix_b ;
	else if(Angle_Error_Correct>0)
		Motor_Rad_Correct =  Car_Keep_Angle_Move_Set_Fix_b*Angle_Error_Correct+Car_Keep_Angle_Move_Set_Fix_b ;
	else
		Motor_Rad_Correct=0;
	if(Car_Keep_Angle_Location_Move_State_Flag==1)	//位置控制方式中，位置、角度到位了的标志。0：空闲（手动置位）；1：正在做位置任务:；2：位置完成，正在做原地校正 ； 3：所有动作完成
	{
//		Motor_Speed[1]= (float)( (speed*( cos(move_angle*PI/180.0f) + sin(move_angle*PI/180.0f) ) )  )  ;
//		Motor_Speed[2]= (float)( (speed*( cos(move_angle*PI/180.0f) - sin(move_angle*PI/180.0f) ) )  )  ;
//		Motor_Speed[3]= (float)( (speed*( cos(move_angle*PI/180.0f) - sin(move_angle*PI/180.0f) ) )  )  ;
//		Motor_Speed[4]= (float)( (speed*( cos(move_angle*PI/180.0f) + sin(move_angle*PI/180.0f) ) )  )  ;
		
		Motor_Speed[1]=roundf( (float)( (speed*( cos((move_angle-aim_angle)*PI/180.0f) + sin((move_angle-aim_angle)*PI/180.0f) ) )  ) ) ;	
		Motor_Speed[2]=roundf( (float)( (speed*( cos((move_angle-aim_angle)*PI/180.0f) - sin((move_angle-aim_angle)*PI/180.0f) ) )  ) ) ;
		Motor_Speed[3]=roundf( (float)( (speed*( cos((move_angle-aim_angle)*PI/180.0f) - sin((move_angle-aim_angle)*PI/180.0f) ) )  ) ) ;
		Motor_Speed[4]=roundf( (float)( (speed*( cos((move_angle-aim_angle)*PI/180.0f) + sin((move_angle-aim_angle)*PI/180.0f) ) )  ) ) ;

		//********************  软启动过程  ********************
		if(Car_Soft_Start_Flag==0)
		{
			if(TIM6_Car_Soft_Starter_Count[0]<Car_Soft_Starter_Time_Set_Value/10)
			{
				for(i=1;i<5;i++)
					Motor_Speed[i]=(float)TIM6_Car_Soft_Starter_Count[0]/(Car_Soft_Starter_Time_Set_Value/10) *Motor_Speed[i];
			}
			else
			{
				TIM6_Car_Soft_Starter_Start[0]=0;				//定时器 - 整车软启动 开始
				TIM6_Car_Soft_Starter_Count[0]=0;				//定时器 - 整车软启动 计数
				Car_Soft_Start_Flag=1;					//车移动，软启动标志位。0：未完成 ； 1：完成
			}			
		}
		//********************  软停止过程  ********************
		else if(Car_Soft_Start_Flag==1)
		{
			for(i=0;i<5;i++)
			{
				Car_Soft_Stop_Predict_Encoder_Sum[i] = (int)fabs( (float)Motor_Speed[i]/60/100*Encoder_Total_Resolution*Car_Soft_Stop_Time_Set_Value/10/2);//（每10ms的）编码器脉冲数 * 时间（ms），公式用的是x=v*t/2	
				if( abs(Motor_Location[i]-Encoder_Location_Now[i] )< Car_Soft_Stop_Predict_Encoder_Sum[i] )
				{
					TIM6_Car_Soft_Stop_Start[i]=1;			//定时器 - 整车软停止 开始
					Motor_Speed[i]=(float) (1-(float)TIM6_Car_Soft_Stop_Count[i]/(Car_Soft_Stop_Time_Set_Value/10) ) *Motor_Speed[i];
				}				
			}
		}
		Motor_LF_Speed=roundf(Motor_Speed[1])- Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
		Motor_LB_Speed=roundf(Motor_Speed[2])- Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
		Motor_RF_Speed=roundf(Motor_Speed[3])+ Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
		Motor_RB_Speed=roundf(Motor_Speed[4])+ Motor_Rad_Correct ;	// 整车每个电机的速度 + 车头校正速度
		

		//****************************  所有电机的位置移动好了，才停止位置PID，切换至速度PID  ****************************
		if( LOC_DEAD_ZONE_Flag[1]==1 && LOC_DEAD_ZONE_Flag[2]==1 && LOC_DEAD_ZONE_Flag[3]==1 && LOC_DEAD_ZONE_Flag[4]==1)//位置环死区标志位。1：死区了（已经到位置了） ； 0：没死（没到位置）
		{
			Car_Keep_Angle_Location_Move_State_Flag=2;	//位置控制方式中，位置、角度到位了的标志。0：空闲（手动置位）；1：正在做位置任务:；2：位置完成，正在做原地校正 ； 3：所有动作完成
			Motor_Control_Mode=1;			//电机控制方式。1：速度控制 ； 2：位置控制
			TIM6_Car_move_Start=1;			//定时器 - 车运动时间函数 开始
			for(i=0;i<5;i++)
			{
				TIM6_Car_Soft_Stop_Start[i]=0;		//定时器 - 整车软停止 开始
				TIM6_Car_Soft_Stop_Count[i]=0;		//定时器 - 整车软停止 计数
				Encoder_Location_Now[i] = 0 ;		//编码器 总计数值，当前时刻,（获取当前的累计值）
				Encoder_Location_Last[i] = 0;		//编码器 总计数值，上一次（更新上次的累计值）
			}
		}	
	}
	//****************************  位置移动好了，仅车头校正  ****************************
	else if(Car_Keep_Angle_Location_Move_State_Flag==2)//位置控制方式中，位置、角度到位了的标志。0：空闲（手动置位）；1：正在做位置任务:；2：位置完成，正在做原地校正 ； 3：所有动作完成
	{
		Motor_LF_Speed= - Motor_Rad_Correct  ;	
		Motor_LB_Speed= - Motor_Rad_Correct  ;
		Motor_RF_Speed=  Motor_Rad_Correct  ;
		Motor_RB_Speed=  Motor_Rad_Correct ;
	}
	Set_Target_Expect_Speed(Motor_LF_Speed,Motor_LB_Speed,Motor_RF_Speed,Motor_RB_Speed);//一次性设置4个电机的PWM，单位：RPM		
	//****************************  位置移动好了，车头校正 保持一定时间  ****************************
	if( fabs(Angle_Error_Correct) < Car_Keep_Angle_Turn_Set_Angle_range)
	{
		if(TIM6_Car_move_Count>Car_Keep_Angle_Turn_Set_keep_time/10)
		{
			Car_Keep_Angle_Location_Move_State_Flag=3;	//位置控制方式中，位置、角度到位了的标志。0：空闲（手动置位）；1：正在做位置任务:；2：位置完成，正在做原地校正 ； 3：所有动作完成
			Car_Stop();	
		}
	}
	else
	{
		TIM6_Car_move_Count=0;			//定时器 - 车运动时间函数 计数
	}
	//********************  超时  ******************** 
	if( TIM6_Car_move_Timeout_Count*10 > Car_Move_Timeout_Set_Value)
	{
		Car_Move_Aim_Time_State_Flag=4;		//车运动“一段时间”函数返回状态 0：空闲（完成）；2：正在运行 ； 3：完成
		Car_Stop();							//车停止运动
	}
	return Car_Keep_Angle_Location_Move_State_Flag;	//位置控制方式中，位置、角度到位了的标志。0：空闲（手动置位）；1：正在做位置任务:；2：位置完成，正在做原地校正 ； 3：所有动作完成
}

//*********************  车运动，所有标志位 清零  *********************
void Car_Move_Flags_Clear(void)
{
	u8 i;
	TIM6_Car_move_Timeout_Start=0;			//定时器 - 车运动超时时间函数 开始
	TIM6_Car_move_Timeout_Count=0;			//定时器 - 车运动超时时间函数 计数
	TIM6_Car_move_Start=0;				//定时器 - 车运动时间函数 开始
	TIM6_Car_move_Count=0;				//定时器 - 车运动时间函数 计数
	TIM6_Car_Soft_Starter_Start[0]=0;	//定时器 - 整车软启动 开始
	TIM6_Car_Soft_Starter_Count[0]=0;	//定时器 - 整车软启动 计数
	Car_Soft_Start_Flag=0;				//车移动，软启动标志位。0：未完成 ； 1：完成
	Car_Soft_Stop_Flag=0;				//车移动，软停止标志位。0：未开始软停 ； 1：开始软停
	for(i=0;i<5;i++)
	{
		TIM6_Car_Soft_Stop_Start[i]=0;		//定时器 - 整车软停止 开始
		TIM6_Car_Soft_Stop_Count[i]=0;		//定时器 - 整车软停止 计数
		Encoder_Location_Now[i] = 0 ;		//编码器 总计数值，当前时刻,（获取当前的累计值）
		Encoder_Location_Last[i] = 0;		//编码器 总计数值，上一次（更新上次的累计值）
		LOC_DEAD_ZONE_Flag[i]=0;			//位置环死区标志位。1：死区了（已经到位置了） ； 0：没死（没到位置）
	}
}




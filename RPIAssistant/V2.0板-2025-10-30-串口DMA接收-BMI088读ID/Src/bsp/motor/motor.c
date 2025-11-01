#include "system.h"
#include "motor.h"
#include "pid.h"
#include "Encoder.h"
#include "string.h"		
#include <stdarg.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>

//********************************************  定时器8 PWM 电机1、2 初始化  ********************************************
void TIM8_Motor_Init(u16 arr,u16 psc)
{
	TIM_HandleTypeDef htimx;
	GPIO_InitTypeDef GPIO_InitStruct;
	TIM_ClockConfigTypeDef sClockSourceConfig;
	TIM_MasterConfigTypeDef sMasterConfig;
	TIM_OC_InitTypeDef sConfigOC;
  
	__HAL_RCC_TIM8_CLK_ENABLE();
	__HAL_RCC_GPIOC_CLK_ENABLE();
  
	//********************  PWM 引脚初始化  ********************
	GPIO_InitStruct.Pin = GPIO_PIN_6|GPIO_PIN_7|GPIO_PIN_8|GPIO_PIN_9;
	GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	GPIO_InitStruct.Alternate = GPIO_AF3_TIM8;
	HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
	
	//********************  定时器初始化并配置通道PWM输出  ********************
	htimx.Instance = TIM8;
	htimx.Init.Prescaler = psc;	//定时器预分频，定时器实际时钟频率为：84MHz/（psc+1）
	htimx.Init.CounterMode = TIM_COUNTERMODE_UP;
	htimx.Init.Period = arr;	// 定时器产生中断频率为：0.5MHz/(1000-1)=1KHz，即1ms定时周期
	htimx.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;
	HAL_TIM_Base_Init(&htimx);

	sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;//选择内部时钟
	HAL_TIM_ConfigClockSource(&htimx, &sClockSourceConfig);

	sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
	sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
	HAL_TIMEx_MasterConfigSynchronization(&htimx, &sMasterConfig);

	sConfigOC.OCMode = TIM_OCMODE_PWM1;//选择PWM模式1
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_1);
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_2);
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_3);
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_4);
	/* 启动通道PWM输出 */
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_2);
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_3);
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_4);
}

//********************************************  定时器4 PWM 电机3、BMI088 Heat 初始化  ********************************************
void TIM4_Motor_Init(u16 arr,u16 psc)
{
	TIM_HandleTypeDef htimx;
	GPIO_InitTypeDef GPIO_InitStruct;
	TIM_ClockConfigTypeDef sClockSourceConfig;
	TIM_MasterConfigTypeDef sMasterConfig;
	TIM_OC_InitTypeDef sConfigOC;
  
	__HAL_RCC_TIM4_CLK_ENABLE();
	__HAL_RCC_GPIOB_CLK_ENABLE();
 	__HAL_RCC_GPIOD_CLK_ENABLE();
  
	//********************  PWM 引脚初始化  ********************
	GPIO_InitStruct.Pin = GPIO_PIN_6|GPIO_PIN_7;
	GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	GPIO_InitStruct.Alternate = GPIO_AF2_TIM4;
	HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

	//********************  BMI088加热 PWM 引脚初始化  ********************
	GPIO_InitStruct.Pin = GPIO_PIN_14;
	GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	GPIO_InitStruct.Alternate = GPIO_AF2_TIM4;
	HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);
 	
	//********************  定时器初始化并配置通道PWM输出  ********************
	htimx.Instance = TIM4;
	htimx.Init.Prescaler = psc;	//定时器预分频，定时器实际时钟频率为：84MHz/（psc+1）
	htimx.Init.CounterMode = TIM_COUNTERMODE_UP;
	htimx.Init.Period = arr;	// 定时器产生中断频率为：0.5MHz/(1000-1)=1KHz，即1ms定时周期
	htimx.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;
	HAL_TIM_Base_Init(&htimx);

	sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;//选择内部时钟
	HAL_TIM_ConfigClockSource(&htimx, &sClockSourceConfig);

	sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
	sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
	HAL_TIMEx_MasterConfigSynchronization(&htimx, &sMasterConfig);

	sConfigOC.OCMode = TIM_OCMODE_PWM1;//选择PWM模式1
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_1);
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_2);
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_3);
	/* 启动通道PWM输出 */
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_2);
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_3);
}

//********************************************  定时器10 PWM 电机4- 初始化  ********************************************
void TIM10_Motor_Init(u16 arr,u16 psc)
{
	TIM_HandleTypeDef htimx;
	GPIO_InitTypeDef GPIO_InitStruct;
	TIM_ClockConfigTypeDef sClockSourceConfig;
	TIM_MasterConfigTypeDef sMasterConfig;
	TIM_OC_InitTypeDef sConfigOC;
  
	__HAL_RCC_TIM10_CLK_ENABLE();
	__HAL_RCC_GPIOB_CLK_ENABLE();
  
	//********************  PWM 引脚初始化  ********************
	GPIO_InitStruct.Pin = GPIO_PIN_8;
	GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	GPIO_InitStruct.Alternate = GPIO_AF3_TIM10;
	HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
	
	//********************  定时器初始化并配置通道PWM输出  ********************
	htimx.Instance = TIM10;
	htimx.Init.Prescaler = psc;	//定时器预分频，定时器实际时钟频率为：84MHz/（psc+1）
	htimx.Init.CounterMode = TIM_COUNTERMODE_UP;
	htimx.Init.Period = arr;	// 定时器产生中断频率为：0.5MHz/(1000-1)=1KHz，即1ms定时周期
	htimx.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;
	HAL_TIM_Base_Init(&htimx);

	sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;//选择内部时钟
	HAL_TIM_ConfigClockSource(&htimx, &sClockSourceConfig);

	sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
	sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
	HAL_TIMEx_MasterConfigSynchronization(&htimx, &sMasterConfig);

	sConfigOC.OCMode = TIM_OCMODE_PWM1;//选择PWM模式1
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_1);
	/* 启动通道PWM输出 */
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_1);
}
//********************************************  定时器11 PWM 电机4+ 初始化  ********************************************
void TIM11_Motor_Init(u16 arr,u16 psc)
{
	TIM_HandleTypeDef htimx;
	GPIO_InitTypeDef GPIO_InitStruct;
	TIM_ClockConfigTypeDef sClockSourceConfig;
	TIM_MasterConfigTypeDef sMasterConfig;
	TIM_OC_InitTypeDef sConfigOC;
  
	__HAL_RCC_TIM11_CLK_ENABLE();
	__HAL_RCC_GPIOB_CLK_ENABLE();
  
	//********************  PWM 引脚初始化  ********************
	GPIO_InitStruct.Pin = GPIO_PIN_9;
	GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	GPIO_InitStruct.Alternate = GPIO_AF3_TIM11;
	HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
	
	//********************  定时器初始化并配置通道PWM输出  ********************
	htimx.Instance = TIM11;
	htimx.Init.Prescaler = psc;	//定时器预分频，定时器实际时钟频率为：84MHz/（psc+1）
	htimx.Init.CounterMode = TIM_COUNTERMODE_UP;
	htimx.Init.Period = arr;	// 定时器产生中断频率为：0.5MHz/(1000-1)=1KHz，即1ms定时周期
	htimx.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;
	HAL_TIM_Base_Init(&htimx);

	sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;//选择内部时钟
	HAL_TIM_ConfigClockSource(&htimx, &sClockSourceConfig);

	sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
	sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
	HAL_TIMEx_MasterConfigSynchronization(&htimx, &sMasterConfig);

	sConfigOC.OCMode = TIM_OCMODE_PWM1;//选择PWM模式1
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_1);
	/* 启动通道PWM输出 */
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_1);
}
//********************************************  定时器9 PWM 盘球1、2 初始化  ********************************************
void TIM9_Motor_Init(u16 arr,u16 psc)
{
	TIM_HandleTypeDef htimx;
	GPIO_InitTypeDef GPIO_InitStruct;
	TIM_ClockConfigTypeDef sClockSourceConfig;
	TIM_MasterConfigTypeDef sMasterConfig;
	TIM_OC_InitTypeDef sConfigOC;
  
	__HAL_RCC_TIM9_CLK_ENABLE();
	__HAL_RCC_GPIOE_CLK_ENABLE();
  
	//********************  PWM 引脚初始化  ********************
	GPIO_InitStruct.Pin = GPIO_PIN_5|GPIO_PIN_6;
	GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	GPIO_InitStruct.Alternate = GPIO_AF3_TIM9;
	HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);
 	
	//********************  定时器初始化并配置通道PWM输出  ********************
	htimx.Instance = TIM9;
	htimx.Init.Prescaler = psc;	//定时器预分频，定时器实际时钟频率为：84MHz/（psc+1）
	htimx.Init.CounterMode = TIM_COUNTERMODE_UP;
	htimx.Init.Period = arr;	// 定时器产生中断频率为：0.5MHz/(1000-1)=1KHz，即1ms定时周期
	htimx.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;
	HAL_TIM_Base_Init(&htimx);

	sClockSourceConfig.ClockSource = TIM_CLOCKSOURCE_INTERNAL;//选择内部时钟
	HAL_TIM_ConfigClockSource(&htimx, &sClockSourceConfig);

	sMasterConfig.MasterOutputTrigger = TIM_TRGO_RESET;
	sMasterConfig.MasterSlaveMode = TIM_MASTERSLAVEMODE_DISABLE;
	HAL_TIMEx_MasterConfigSynchronization(&htimx, &sMasterConfig);

	sConfigOC.OCMode = TIM_OCMODE_PWM1;//选择PWM模式1
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_1);
	sConfigOC.Pulse = 0;
	sConfigOC.OCPolarity = TIM_OCPOLARITY_HIGH;
	sConfigOC.OCFastMode = TIM_OCFAST_DISABLE;
	HAL_TIM_PWM_ConfigChannel(&htimx, &sConfigOC, TIM_CHANNEL_2);
	/* 启动通道PWM输出 */
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htimx,TIM_CHANNEL_2);
}


//********************************************  电机输出 PWM  ********************************************
extern float ADC_BAT_Voltage;		//电池电压
void Set_Motor_PWM(u8 motor_ch,int motor_pwm)
{
	if(motor_pwm>=PWM_Max)
		motor_pwm=PWM_Max;
	else if(motor_pwm<=-PWM_Max)
		motor_pwm=-PWM_Max;
	if(ADC_BAT_Voltage<9.0f)	//读取板载5V电压值
		motor_pwm=0;
	switch(motor_ch)
	{
		case 1:
			if(motor_pwm>0){TIM8->CCR1=motor_pwm;TIM8->CCR2=0;}
			else if (motor_pwm<=0){TIM8->CCR1=0;TIM8->CCR2=abs(motor_pwm);}break;
		case 2:
			if(motor_pwm>0){TIM8->CCR3=motor_pwm;TIM8->CCR4=0;}
			else if (motor_pwm<=0){TIM8->CCR3=0;TIM8->CCR4=abs(motor_pwm);}break;
		case 3:
			if(motor_pwm>0){TIM4->CCR2=motor_pwm;TIM4->CCR1=0;}
			else if (motor_pwm<=0){TIM4->CCR2=0;TIM4->CCR1=abs(motor_pwm);}break;
		case 4:
			if(motor_pwm>0){TIM11->CCR1=motor_pwm;TIM10->CCR1=0;}
			else if (motor_pwm<=0){TIM11->CCR1=0;TIM10->CCR1=abs(motor_pwm);}break;				
	}		
}
//********************************************  盘球输出 PWM  ********************************************
extern float ADC_BAT_Voltage;		//电池电压
void Set_Ball_PWM(u8 ball_ch,u16 ball_pwm)
{
	if(ball_pwm>=PWM_Max)
		ball_pwm=PWM_Max;
	if(ADC_BAT_Voltage<9.0f)	//读取板载5V电压值
		ball_pwm=0;
	switch(ball_ch)
	{
		case 1:
			TIM9->CCR1=ball_pwm;break;
		case 2:
			TIM9->CCR2=ball_pwm;break;	
	}		
}
//********************************************  BMI088加热  ********************************************
void BMI088_Heat_PWM(u16 pwm)
{
	TIM4->CCR3=pwm;					
}

//***********************  目标速度值限制 单位 转/秒（这里限制的是期望值，达到期望值后，就控制住） ***********************

int PID_Target_Expect_Speed[5]={0,0,0,0,0};	// 目标速度的期望值 转/分钟（期望转速达到多少，这个从上位机获取）
void Speed_Protect(u8 ch,float *speed_val)
{
	if (*speed_val > abs(PID_Target_Expect_Speed[ch]))
		*speed_val = abs(PID_Target_Expect_Speed[ch]);
	else if (*speed_val < -abs(PID_Target_Expect_Speed[ch]) )
		*speed_val = -abs(PID_Target_Expect_Speed[ch]);	
		
//	if( PID_Target_Expect_Speed[ch] >=0)
//	{
//		if(*speed_val >= 0)
//		{
//			if (*speed_val > PID_Target_Expect_Speed[ch])
//				*speed_val = PID_Target_Expect_Speed[ch];
//		}
//		else if(*speed_val < 0)
//		{
//			*speed_val = PID_Target_Expect_Speed[ch];
//		}
//	}
//	else if( PID_Target_Expect_Speed[ch] <0)
//	{
//		if(*speed_val <= 0)
//		{
//			if (*speed_val < PID_Target_Expect_Speed[ch])
//				*speed_val = PID_Target_Expect_Speed[ch];
//		}
//		else if( *speed_val > 0)
//		{
//			*speed_val = PID_Target_Expect_Speed[ch];
//		}

//	}
	
}

//***********************  上位机设置期望目标速度 接口 ***********************
//speed_1:左前
//speed_2:左后
//speed_3:右前
//speed_4:右后
void Set_Target_Expect_Speed(int speed_1,int speed_2,int speed_3,int speed_4)
{
	PID_Target_Expect_Speed[1] = speed_1;
	PID_Target_Expect_Speed[2] = speed_2;
	PID_Target_Expect_Speed[3] = speed_3;
	PID_Target_Expect_Speed[4] = speed_4;
}

int PID_Target_Expect_Location[5]={0,0,0,0,0};	// 目标位置的期望值 脉冲个数（期望位置达到多少，这个从上位机获取）

//***********************  上位机设置期望目标位置 接口 ***********************
//speed_1:左前
//speed_2:左后
//speed_3:右前
//speed_4:右后
void Set_Target_Expect_Location(int location_1,int location_2,int location_3,int location_4)
{
	PID_Target_Expect_Location[1] = location_1;
	PID_Target_Expect_Location[2] = location_2;
	PID_Target_Expect_Location[3] = location_3;
	PID_Target_Expect_Location[4] = location_4;
}
/*定义位置PID与速度PID结构体型的全局变量*/
PID PID_Location;
PID PID_Speed;

int Encoder_Speed_Count[5];			//编码器 读取脉冲个数，速度PID中用到

int Encoder_Location_Now[5];    			//编码器 总计数值，当前时刻
int Encoder_Location_Last[5];    		//编码器 总计数值，上一次
int Encoder_Location_Error[5]; 			//编码器 当前时刻与上一时刻的变化量 （现在 - 上一次）
float Rotate_Target_Speed[5];   	//通过位置PID，得到 目标转速 单位 转/分钟
float Rotate_Speed_Now[5];  	 	//当前实际转速 单位 转/分钟
int PWM_Out_Value[5];				//输出的占空比
float Encoder_Total_Resolution = TOTAL_RESOLUTION;			//编码器总分辨率
u16 Encoder_Resolution = ENCODER_RESOLUTION;				//编码器 极对数
float Motor_Reduction_Ratio = MOTOR_REDUCTION_RATIO;		//电机 减速比
//********************************************   电机 串级（位置+速度） PID 控制输出  ********************************************
void Motor_Cascade_Set_Control(u8 motor_ch)
{
	//****************************   【1】读取编码器的值  ****************************
	Encoder_Speed_Count[motor_ch] = Encoder_Get(motor_ch)-ENCODER_CNT_INIT;			//编码器 读取脉冲个数，速度PID中用到
	Encoder_Clear(motor_ch);			//清除编码器 计数
	
	Encoder_Location_Now[motor_ch] += Encoder_Speed_Count[motor_ch] ;	//编码器 总计数值，当前时刻,（获取当前的累计值）
	Encoder_Location_Error[motor_ch] = Encoder_Location_Now[motor_ch] - Encoder_Location_Last[motor_ch]; 	//编码器 当前时刻与上一时刻的变化量 （现在 - 上一次）
	Encoder_Location_Last[motor_ch] = Encoder_Location_Now[motor_ch];							//编码器 总计数值，上一次（更新上次的累计值）
	
	//****************************   【2】PID运算，得到 转速目标值 单位 转/分钟  ****************************
	PID_Location.target_val[motor_ch]=PID_Target_Expect_Location[motor_ch];	//设置目标位置
	Rotate_Target_Speed[motor_ch] = (int)PID_Location_Realize(motor_ch,&PID_Location,Encoder_Location_Now[motor_ch]) ;	//传入编码器的[总计数值]，得到 输出转速目标值
	Speed_Protect(motor_ch,&Rotate_Target_Speed[motor_ch]);				//目标速度值限制 单位 转/分钟
	Pid_Set_Target(motor_ch,&PID_Speed, Rotate_Target_Speed[motor_ch]);    //PID 设定 目标转速 

    Rotate_Speed_Now[motor_ch] = (float)Encoder_Location_Error[motor_ch] / Encoder_Total_Resolution * 100 *60;	// 转速(1秒钟转多少转)=单位时间内的计数值/总分辨率*100（定时器0.01s计算一次）* 60（秒） == 转/分钟
	//****************************   【3】速度PID运算，得到PWM控制值  ****************************
	PWM_Out_Value[motor_ch] = (int)PID_Speed_Realize(motor_ch,&PID_Speed, (int)Rotate_Speed_Now[motor_ch]);
	
	//****************************   【4】PWM控制电机  ****************************
	Set_Motor_PWM(motor_ch,PWM_Out_Value[motor_ch]);
	
}

//********************************************   电机 速度 PID 控制输出  ********************************************
extern u8 TIM6_Car_Soft_Starter_Start[5];		//定时器 - 整车软启动 开始
extern u32 TIM6_Car_Soft_Starter_Count[5];		//定时器 - 整车软启动 计数
extern u16 Motor_PWM_or_RPM_Mode;		//电机工作模式，1：转速模式（默认） ； 2,：占空比模式
extern u16 Car_Soft_Starter_Time_Set_Value;		//车移动，设定的 软启动时间，单位（ms）
u8 Soft_Starter_OK_Flag[5];				//电机软启动 完成标志 0：未完成；1：完成
float Soft_Starter_Speed[5];			//电机软启动速度
void Motor_Speed_Set_Control(u8 motor_ch)
{

	PID_Speed.target_val[motor_ch]=PID_Target_Expect_Speed[motor_ch];	//不软启动

	//****************************   【1】读取编码器的值  ****************************
	Encoder_Speed_Count[motor_ch] = Encoder_Get(motor_ch)-ENCODER_CNT_INIT;			//编码器 读取脉冲个数，速度PID中用到
	Encoder_Clear(motor_ch);			//清除编码器 计数

    Rotate_Speed_Now[motor_ch] = (float)Encoder_Speed_Count[motor_ch] / Encoder_Total_Resolution * 100 *60;	// 转速(1秒钟转多少转)=单位时间内的计数值/总分辨率*100（定时器0.01s计算一次）* 60（秒） == 转/分钟

	//****************************   【2】速度PID运算，得到PWM控制值  ****************************
	PWM_Out_Value[motor_ch] = (int)PID_Speed_Realize(motor_ch,&PID_Speed, (int)Rotate_Speed_Now[motor_ch]);
	//****************************   【3】PWM控制电机  ****************************
	if(Motor_PWM_or_RPM_Mode==1)	//电机工作模式，1：转速模式（默认） ； 2,：占空比模式
	{
		Set_Motor_PWM(motor_ch,PWM_Out_Value[motor_ch]);
	}
}



#include "timer.h"
#include "motor.h"
#include "led.h"
#include "system.h"
TIM_HandleTypeDef TIM6_Handler;      //定时器句柄 
//********************************************  定时器6 计时器 初始化  ********************************************
void TIM6_Timer_Init(u16 arr,u16 psc)
{
    TIM6_Handler.Instance=TIM6;                          //通用定时器3
    TIM6_Handler.Init.Prescaler=psc;                     //分频系数
    TIM6_Handler.Init.CounterMode=TIM_COUNTERMODE_UP;    //向上计数器
    TIM6_Handler.Init.Period=arr;                        //自动装载值
    TIM6_Handler.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;//时钟分频因子
    HAL_TIM_Base_Init(&TIM6_Handler);
    
    HAL_TIM_Base_Start_IT(&TIM6_Handler); //使能定时器3和定时器3更新中断：TIM_IT_UPDATE  
}
//定时器底册驱动，开启时钟，设置中断优先级
//此函数会被HAL_TIM_Base_Init()函数调用
void HAL_TIM_Base_MspInit(TIM_HandleTypeDef *htim)
{
    if(htim->Instance==TIM6)
	{
		__HAL_RCC_TIM6_CLK_ENABLE();            //使能TIM6时钟
		HAL_NVIC_SetPriority(TIM6_DAC_IRQn,1,1);    //设置中断优先级，抢占优先级1，子优先级3
		HAL_NVIC_EnableIRQ(TIM6_DAC_IRQn);          //开启ITM3中断   
	}
}
//定时器6中断服务函数
void TIM6_DAC_IRQHandler(void)
{
    HAL_TIM_IRQHandler(&TIM6_Handler);
}

u16 test_counter;

////********************************************  定时器6 定时器中断服务函数调用  ********************************************
u8 TIM6_DEAD_ZONE_Start[5];		//定时器 - 误差死区 持续时间 开始
u16 TIM6_DEAD_ZONE_Count[5];	//定时器 - 误差死区 持续时间 计数
u8 TIM6_Compass_Key_Start;		//定时器 - Compass按键按下 计数
u16 TIM6_Compass_Key_Count;		//定时器 - Compass按键按下 开始
u8 TIM6_Compass_Calibrat_Start;	//定时器 - Compass切换模式校准按下 计数
u16 TIM6_Compass_Calibrat_Count;//定时器 - Compass切换模式按键按下 开始
u8 TIM6_BNO055_FirstON_Start=1;	//定时器 - BNO055 第一次上电 计数
u16 TIM6_BNO055_FirstON_Count;	//定时器 - BNO055 第一次上电 开始
u16 TIM6_Compass_LED_Count;		//定时器 - Compass LED闪烁 开始
u8 TIM6_BNO055_ACC_Calibrat_Start[6];	//定时器 - BNO055 加速度计 手动校准，每一个面保持时间，0~5对应 X+、X-、Y+、Y-、Z+、Z- 开始
u16 TIM6_BNO055_ACC_Calibrat_Count[6];		//定时器 - BNO055 加速度计 手动校准，每一个面保持时间，0~5对应 X+、X-、Y+、Y-、Z+、Z- 计数


extern u8 KEY_Compass_Menu;		//Compass按键菜单
extern u8 LED_Control_Mode;			//控制 LED闪烁 模式 0：关闭模式控制 ； 1：快闪 ； 2：慢闪 ；3：超慢闪。
u8 TIM6_Car_move_Start;			//定时器 - 车运动时间函数 开始
u32 TIM6_Car_move_Count;		//定时器 - 车运动时间函数 计数

u8 TIM6_Car_move_Timeout_Start;			//定时器 - 车运动超时时间函数 开始
u32 TIM6_Car_move_Timeout_Count;		//定时器 - 车运动超时时间函数 计数

u8 TIM6_test_Start=1;			//定时器 - 内部测试 开始
u32 TIM6_test_Count;			//定时器 - 内部测试 计数

u8 TIM6_Car_Soft_Starter_Start[5];		//定时器 - 整车软启动 开始
u32 TIM6_Car_Soft_Starter_Count[5];		//定时器 - 整车软启动 计数
u8 TIM6_Car_Soft_Stop_Start[5];			//定时器 - 整车软停止 开始
u32 TIM6_Car_Soft_Stop_Count[5];		//定时器 - 整车软停止 计数
extern u8 Motor_Control_Mode;			//电机控制方式。1：速度控制 ； 2：位置控制
void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
	u8 i;
    if(htim==(&TIM6_Handler))
    {
		test_counter++;
		if(test_counter==100)
		{
			LED_B=!LED_B;        //LED_B反转
			test_counter=0;
		}
		//***********************  大类： 速度PID 控制方式  ***********************
		if(Motor_Control_Mode == 1)
		{
			Motor_Speed_Set_Control(1);		//电机 速度 PID 控制输出	
			Motor_Speed_Set_Control(2);		//电机 速度 PID 控制输出	
			Motor_Speed_Set_Control(3);		//电机 速度 PID 控制输出	
			Motor_Speed_Set_Control(4);		//电机 速度 PID 控制输出	
		}
		//***********************  大类： （速度+位置）PID 控制方式  ***********************
		else if(Motor_Control_Mode == 2)
		{
			Motor_Cascade_Set_Control(1);	//电机 串级（位置+速度） PID 控制输出
			Motor_Cascade_Set_Control(2);	//电机 串级（位置+速度） PID 控制输出
			Motor_Cascade_Set_Control(3);	//电机 串级（位置+速度） PID 控制输出
			Motor_Cascade_Set_Control(4);	//电机 串级（位置+速度） PID 控制输出
		}

		//***********************  速度PID 速度为0 死区 计时 ***********************
		for(i=0;i<5;i++)
		{
			if(TIM6_DEAD_ZONE_Start[i]==1)TIM6_DEAD_ZONE_Count[i]++;
		}
//		//***********************  Compass 按键 计时 ***********************
//		if(TIM6_Compass_Key_Start==1) 	TIM6_Compass_Key_Count++;
//		
//		if(TIM6_Compass_Calibrat_Start==1)//消磁校准过程中，计时（超时作用）
//		{
//			TIM6_Compass_Calibrat_Count++;  
//		}
//		if( TIM6_Compass_Key_Count>50 && TIM6_Compass_Key_Count<100)	//按下时间500~1000ms，正北
//		{
//			LED_G=0;
//			KEY_Compass_Menu=1;		//Compass按键菜单	
//			LED_Control_Mode = 0;		//控制 LED闪烁 模式 0：关闭模式控制 ； 1：快闪 ； 2：慢闪 ；3：超慢闪。
//		}
//		else if( TIM6_Compass_Key_Count>=100 && TIM6_Compass_Key_Count<400)	//按下时间1000~40000ms，亮灯
//		{
//			LED_G=1;
//		}
//		else if( TIM6_Compass_Key_Count>=400)//按下时间4000ms以上，消磁
//		{
//			KEY_Compass_Menu=2;		//Compass按键菜单	
//			LED_Control_Mode = 1;		//控制 LED闪烁 模式 0：关闭模式控制 ； 1：快闪 ； 2：慢闪 ；3：超慢闪。
//		}
//		//***********************  陀螺仪 LED 闪烁模式 ***********************
//		if( LED_Control_Mode == 1)		//控制 LED闪烁 模式 0：关闭模式控制 ； 1：快闪 ； 2：慢闪 ；3：超慢闪。
//		{
//			TIM6_Compass_LED_Count++;		//定时器 - Compass LED闪烁 开始
//			if(TIM6_Compass_LED_Count>2)
//			{
//				TIM6_Compass_LED_Count=0;		//定时器 - Compass LED闪烁 开始
//				LED_G=!LED_G;			//绿灯闪烁
//			}
//		}
//		else if( LED_Control_Mode == 2)		//控制 LED闪烁 模式 0：关闭模式控制 ； 1：快闪 ； 2：慢闪 ；3：超慢闪。
//		{
//			TIM6_Compass_LED_Count++;		//定时器 - Compass LED闪烁 开始
//			if(TIM6_Compass_LED_Count>20)
//			{
//				TIM6_Compass_LED_Count=0;		//定时器 - Compass LED闪烁 开始
//				LED_G=!LED_G;			//绿灯闪烁
//			}
//		}
//		else if( LED_Control_Mode == 3)		//控制 LED闪烁 模式 0：关闭模式控制 ； 1：快闪 ； 2：慢闪 ；3：超慢闪。
//		{
//			TIM6_Compass_LED_Count++;		//定时器 - Compass LED闪烁 开始
//			if(TIM6_Compass_LED_Count>60)
//			{
//				TIM6_Compass_LED_Count=0;		//定时器 - Compass LED闪烁 开始
//				LED_G=!LED_G;			//绿灯闪烁
//			}
//		}
		
		
		

		//***********************  车运动时间函数 计时 ***********************
		if(TIM6_Car_move_Start==1) TIM6_Car_move_Count++;
		//***********************  车运动超时时间函数 计时 ***********************
		if(TIM6_Car_move_Timeout_Start==1) TIM6_Car_move_Timeout_Count++;	
		
		for(i=0;i<5;i++)
		{
		//***********************  整车软启动 计时 ***********************
			if(TIM6_Car_Soft_Starter_Start[i]==1) TIM6_Car_Soft_Starter_Count[i]++;
		//***********************  整车软停止 计时 ***********************
			if(TIM6_Car_Soft_Stop_Start[i]==1) TIM6_Car_Soft_Stop_Count[i]++;	
			
		}

//		//***********************  内部测试 计时 ***********************
//		if(TIM6_test_Start==1) TIM6_test_Count++;


    }
}



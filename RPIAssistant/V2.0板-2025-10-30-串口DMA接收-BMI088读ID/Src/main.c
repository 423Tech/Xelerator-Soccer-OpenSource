#include "stm32f4xx_hal.h"
#include "system.h"
#include "string.h"
#include "usart.h"
#include "led.h"
#include "stm_flash.h"
#include "key.h"
#include "myiic.h"
#include "adc.h"
#include "pid.h"
#include "BMI088driver.h"
#include "BMI088reg.h"
#include "BMI088Middleware.h"


#include "spi.h"
#include "motor.h"
#include "timer.h"
#include "Encoder.h"
#include <stdio.h>
#include <string.h>
#include "string.h"
extern u8 Motor_Control_Mode;			//电机控制方式。1：速度控制 ； 2：位置控制


uint32_t test1,test2,test3,test4;
int test_speed;
uint8_t test_bmi_gyro_id,test_bmi_acc_id;

float gyro[3], accel[3], temp;

int main(void)
{
	HAL_Init();				/* 复位所有外设，初始化Flash接口和系统滴答定时器 */
	SystemClock_Config();	/* 配置系统时钟 */
	HAL_Delay(100);
	LED_GPIO_Init();			//内部，LED引脚初始化
	Kick_IO=0;	   				//弹射 1:充电 ； 0:放电
	Adc_Init();					//ADC 初始化
	TIM8_Motor_Init(1000-1,168-1);	//定时器8 PWM 电机1、2 初始化 84000 000 / 168 = 500 kHz ; 500k/1000=500hz
	TIM4_Motor_Init(1000-1,168-1);	//定时器4 PWM 电机3、BMI088 Heat 初始化
	TIM10_Motor_Init(1000-1,168-1);	//定时器10 PWM 电机4- 初始化
	TIM11_Motor_Init(1000-1,168-1);	//定时器11 PWM 电机4+ 初始化
	TIM9_Motor_Init(1000-1,84-1);	//定时器9 PWM 盘球1、2 初始化 84000 000 / 84 = 1000 kHz ; 1000k/10=500hz
	TIM1_Encoder_Init(ENCODER_TIM_PERIOD-1,ENCODER_TIM_PSC);	//定时器1 编码器1 初始化
	TIM2_Encoder_Init(ENCODER_TIM_PERIOD-1,ENCODER_TIM_PSC);	//定时器2 编码器2 初始化
	TIM3_Encoder_Init(ENCODER_TIM_PERIOD-1,ENCODER_TIM_PSC);	//定时器3 编码器3 初始化
	TIM5_Encoder_Init(ENCODER_TIM_PERIOD-1,ENCODER_TIM_PSC);	//定时器5 编码器4 初始化
	
	TIM6_Timer_Init(100-1,8400-1); 					//定时器6 计时器 初始化，84000 000 / 8400 = 10 kHz ; 10k/100=100hz,10ms
	PID_param_init();				// PID 参数初始化 
	Set_Target_Expect_Speed(0,0,0,0);	//上位机设置期望目标速度 接口
	Motor_Control_Mode=1;			//电机控制方式。1：速度控制 ； 2：位置控制
	
	UART4_DMA_Rx_Configuration();
	UART4_Configuration(115200);			//串口4 DMA 初始化
	
	BMI088_GPIO_init();
	SPI2_Init();
    while(BMI088_init());
	Beep=1;HAL_Delay(100);Beep=0;   		//蜂鸣器

	BMI088_Heat_PWM(500);			//BMI088加热
	Set_Ball_PWM(1,0);	//盘球输出 PWM 
	Set_Ball_PWM(2,0);	//盘球输出 PWM 
	BMI088_accel_read_single_reg(BMI088_ACC_CHIP_ID, test_bmi_acc_id);
	BMI088_gyro_read_single_reg(BMI088_GYRO_CHIP_ID, test_bmi_gyro_id);
	while(1)
	{
		BMI088_read(gyro, accel, &temp);
		
		UART4_Send_str("HELLO");
		
		LED_G=1;	   			
//		Kick_IO=1;	   			//弹射 1:充电 ； 0:放电
		HAL_Delay(100);
		LED_G=0;	   			
//		Kick_IO=0;	   			//弹射 1:充电 ； 0:放电
		HAL_Delay(100);		

	}

}



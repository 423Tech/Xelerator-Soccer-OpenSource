#include "system.h"
#include "Encoder.h"
#include "motor.h"
#include "string.h"		
#include <stdarg.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "stm32f4xx_hal.h"
/* Timer handler declaration */
TIM_HandleTypeDef    htimx_Encoder1;
TIM_HandleTypeDef    htimx_Encoder2;
TIM_HandleTypeDef    htimx_Encoder3;
TIM_HandleTypeDef    htimx_Encoder4;
//********************************************  定时器1 编码器1 初始化  ********************************************
void TIM1_Encoder_Init(u16 arr,u16 psc)
{
	TIM_Encoder_InitTypeDef sEncoderConfig;
	  GPIO_InitTypeDef GPIO_InitStruct;
    __HAL_RCC_GPIOA_CLK_ENABLE();

    //**********************  编码器初始化  **********************
    GPIO_InitStruct.Pin = GPIO_PIN_8|GPIO_PIN_9;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull=GPIO_PULLUP;
    GPIO_InitStruct.Alternate = GPIO_AF1_TIM1;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
	
	__HAL_RCC_TIM1_CLK_ENABLE();
	htimx_Encoder1.Instance = TIM1;
	htimx_Encoder1.Init.Prescaler = psc;					// 定义定时器预分频，定时器实际时钟频率为：84MHz/（psc+1）,实际时钟频率为：84MHz
	htimx_Encoder1.Init.CounterMode = TIM_COUNTERMODE_UP;
	htimx_Encoder1.Init.Period = arr;						// 定义定时器周期，(编码器线数-1)*4	四倍频原理
	htimx_Encoder1.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;

	sEncoderConfig.EncoderMode        = TIM_ENCODERMODE_TI12;
	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_RISING;
//	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_FALLING;
	sEncoderConfig.IC1Selection       = TIM_ICSELECTION_DIRECTTI;
	sEncoderConfig.IC1Prescaler       = TIM_ICPSC_DIV1;
	sEncoderConfig.IC1Filter          = ICx_FILTER;

	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_RISING;
//	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_FALLING;
	sEncoderConfig.IC2Selection       = TIM_ICSELECTION_DIRECTTI;
	sEncoderConfig.IC2Prescaler       = TIM_ICPSC_DIV1;
	sEncoderConfig.IC2Filter          = ICx_FILTER;
	HAL_TIM_Encoder_Init(&htimx_Encoder1, &sEncoderConfig);

	HAL_TIM_Encoder_Start(&htimx_Encoder1, TIM_CHANNEL_1);
	HAL_TIM_Encoder_Start(&htimx_Encoder1, TIM_CHANNEL_2);
	__HAL_TIM_SET_COUNTER(&htimx_Encoder1,ENCODER_CNT_INIT);	//设置初始值
}
//********************************************  定时器2 编码器2 初始化  ********************************************
void TIM2_Encoder_Init(u16 arr,u16 psc)
{
	TIM_Encoder_InitTypeDef sEncoderConfig;
	  GPIO_InitTypeDef GPIO_InitStruct;
    __HAL_RCC_GPIOA_CLK_ENABLE();
    __HAL_RCC_GPIOB_CLK_ENABLE();

    //**********************  编码器初始化  **********************
    GPIO_InitStruct.Pin = GPIO_PIN_15;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull=GPIO_PULLUP;
    GPIO_InitStruct.Alternate = GPIO_AF1_TIM2;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

    GPIO_InitStruct.Pin = GPIO_PIN_3;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull=GPIO_PULLUP;
    GPIO_InitStruct.Alternate = GPIO_AF1_TIM2;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
    	
	__HAL_RCC_TIM2_CLK_ENABLE();
	htimx_Encoder2.Instance = TIM2;
	htimx_Encoder2.Init.Prescaler = psc;					// 定义定时器预分频，定时器实际时钟频率为：84MHz/（psc+1）,实际时钟频率为：84MHz
	htimx_Encoder2.Init.CounterMode = TIM_COUNTERMODE_UP;
	htimx_Encoder2.Init.Period = arr;						// 定义定时器周期，(编码器线数-1)*4	四倍频原理
	htimx_Encoder2.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;

	sEncoderConfig.EncoderMode        = TIM_ENCODERMODE_TI12;
	
	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_RISING;
//	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_FALLING;
	sEncoderConfig.IC1Selection       = TIM_ICSELECTION_DIRECTTI;
	sEncoderConfig.IC1Prescaler       = TIM_ICPSC_DIV1;
	sEncoderConfig.IC1Filter          = ICx_FILTER;

	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_RISING;
//	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_FALLING;
	sEncoderConfig.IC2Selection       = TIM_ICSELECTION_DIRECTTI;
	sEncoderConfig.IC2Prescaler       = TIM_ICPSC_DIV1;
	sEncoderConfig.IC2Filter          = ICx_FILTER;
	HAL_TIM_Encoder_Init(&htimx_Encoder2, &sEncoderConfig);

	HAL_TIM_Encoder_Start(&htimx_Encoder2, TIM_CHANNEL_1);
	HAL_TIM_Encoder_Start(&htimx_Encoder2, TIM_CHANNEL_2);
	__HAL_TIM_SET_COUNTER(&htimx_Encoder2,ENCODER_CNT_INIT);	//设置初始值
}
//********************************************  定时器3 编码器3 初始化  ********************************************
void TIM3_Encoder_Init(u16 arr,u16 psc)
{
	TIM_Encoder_InitTypeDef sEncoderConfig;
	  GPIO_InitTypeDef GPIO_InitStruct;
    __HAL_RCC_GPIOB_CLK_ENABLE();

    //**********************  编码器初始化  **********************
    GPIO_InitStruct.Pin = GPIO_PIN_4|GPIO_PIN_5;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull=GPIO_PULLUP;
    GPIO_InitStruct.Alternate = GPIO_AF2_TIM3;
    HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);

	__HAL_RCC_TIM3_CLK_ENABLE();
	htimx_Encoder3.Instance = TIM3;
	htimx_Encoder3.Init.Prescaler = psc;					// 定义定时器预分频，定时器实际时钟频率为：84MHz/（psc+1）,实际时钟频率为：84MHz
	htimx_Encoder3.Init.CounterMode = TIM_COUNTERMODE_UP;
	htimx_Encoder3.Init.Period = arr;						// 定义定时器周期，(编码器线数-1)*4	四倍频原理
	htimx_Encoder3.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;

	sEncoderConfig.EncoderMode        = TIM_ENCODERMODE_TI12;
	
//	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_RISING;
	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_FALLING;
	sEncoderConfig.IC1Selection       = TIM_ICSELECTION_DIRECTTI;
	sEncoderConfig.IC1Prescaler       = TIM_ICPSC_DIV1;
	sEncoderConfig.IC1Filter          = ICx_FILTER;

//	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_RISING;
	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_FALLING;
	sEncoderConfig.IC2Selection       = TIM_ICSELECTION_DIRECTTI;
	sEncoderConfig.IC2Prescaler       = TIM_ICPSC_DIV1;
	sEncoderConfig.IC2Filter          = ICx_FILTER;
	HAL_TIM_Encoder_Init(&htimx_Encoder3, &sEncoderConfig);

	HAL_TIM_Encoder_Start(&htimx_Encoder3, TIM_CHANNEL_1);
	HAL_TIM_Encoder_Start(&htimx_Encoder3, TIM_CHANNEL_2);
	__HAL_TIM_SET_COUNTER(&htimx_Encoder3,ENCODER_CNT_INIT);	//设置初始值
}
//********************************************  定时器5 编码器4 初始化  ********************************************
void TIM5_Encoder_Init(u16 arr,u16 psc)
{
	TIM_Encoder_InitTypeDef sEncoderConfig;
	  GPIO_InitTypeDef GPIO_InitStruct;
    __HAL_RCC_GPIOA_CLK_ENABLE();

    //**********************  编码器初始化  **********************
    GPIO_InitStruct.Pin = GPIO_PIN_0|GPIO_PIN_1;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull=GPIO_PULLUP;
    GPIO_InitStruct.Alternate = GPIO_AF2_TIM5;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);

	__HAL_RCC_TIM5_CLK_ENABLE();
	htimx_Encoder4.Instance = TIM5;
	htimx_Encoder4.Init.Prescaler = psc;					// 定义定时器预分频，定时器实际时钟频率为：84MHz/（psc+1）,实际时钟频率为：84MHz
	htimx_Encoder4.Init.CounterMode = TIM_COUNTERMODE_UP;
	htimx_Encoder4.Init.Period = arr;						// 定义定时器周期，(编码器线数-1)*4	四倍频原理
	htimx_Encoder4.Init.ClockDivision=TIM_CLOCKDIVISION_DIV1;

	sEncoderConfig.EncoderMode        = TIM_ENCODERMODE_TI12;
	
//	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_RISING;
	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_FALLING;
	sEncoderConfig.IC1Selection       = TIM_ICSELECTION_DIRECTTI;
	sEncoderConfig.IC1Prescaler       = TIM_ICPSC_DIV1;
	sEncoderConfig.IC1Filter          = ICx_FILTER;

//	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_RISING;
	sEncoderConfig.IC1Polarity        = TIM_ICPOLARITY_FALLING;
	sEncoderConfig.IC2Selection       = TIM_ICSELECTION_DIRECTTI;
	sEncoderConfig.IC2Prescaler       = TIM_ICPSC_DIV1;
	sEncoderConfig.IC2Filter          = ICx_FILTER;
	HAL_TIM_Encoder_Init(&htimx_Encoder4, &sEncoderConfig);

	HAL_TIM_Encoder_Start(&htimx_Encoder4, TIM_CHANNEL_1);
	HAL_TIM_Encoder_Start(&htimx_Encoder4, TIM_CHANNEL_2);
	__HAL_TIM_SET_COUNTER(&htimx_Encoder4,ENCODER_CNT_INIT);	//设置初始值
}
//********************************************  读取编码器 计数  ********************************************
uint16_t Encoder_Get(u8 motor_ch)
{
	uint16_t Temp;
	switch(motor_ch)
	{
		case 1:	Temp = __HAL_TIM_GET_COUNTER(&htimx_Encoder1);break;	//编码器 1	
		case 2:	Temp = __HAL_TIM_GET_COUNTER(&htimx_Encoder2);break;	//编码器 2	
		case 3:	Temp = __HAL_TIM_GET_COUNTER(&htimx_Encoder3);break;	//编码器 3	
		case 4:	Temp = __HAL_TIM_GET_COUNTER(&htimx_Encoder4);break;	//编码器 4		
	}
	return Temp;
}
//********************************************  清除编码器 计数  ********************************************
void Encoder_Clear(u8 motor_ch)
{
	switch(motor_ch)
	{
		case 1:	__HAL_TIM_SET_COUNTER(&htimx_Encoder1,ENCODER_CNT_INIT);break;	//编码器 1	
		case 2:	__HAL_TIM_SET_COUNTER(&htimx_Encoder2,ENCODER_CNT_INIT);break;	//编码器 2	
		case 3:	__HAL_TIM_SET_COUNTER(&htimx_Encoder3,ENCODER_CNT_INIT);break;	//编码器 3	
		case 4:	__HAL_TIM_SET_COUNTER(&htimx_Encoder4,ENCODER_CNT_INIT);break;	//编码器 4		
	}
}

#ifndef __ENCODER_H__
#define __ENCODER_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"


#define	ICx_FILTER 		15

#define ENCODER_TIM_PSC  0          //计数器分频*/
#define ENCODER_TIM_PERIOD  65535   	//计数器最大值*/
#define ENCODER_CNT_INIT 32768                  //计数器初值*/




void TIM1_Encoder_Init(u16 arr,u16 psc);	//定时器1 编码器1 初始化
void TIM2_Encoder_Init(u16 arr,u16 psc);	//定时器2 编码器2 初始化
void TIM3_Encoder_Init(u16 arr,u16 psc);	//定时器3 编码器3 初始化
void TIM5_Encoder_Init(u16 arr,u16 psc);	//定时器5 编码器4 初始化

uint16_t Encoder_Get(u8 motor_ch);			//读取编码器 计数
void Encoder_Clear(u8 motor_ch);			//清除编码器 计数

#endif  



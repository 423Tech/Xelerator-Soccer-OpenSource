#ifndef __LED_H__
#define __LED_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "system.h"

#define LED_Y 		PCout(13)   	//LED 黄灯
#define LED_B 		PCout(14)   	//LED 蓝灯
#define LED_R 		PCout(15)   	//LED 红灯
#define LED_G 		PEout(10)   	//LED 绿灯
#define Beep 		PEout(4)   		//蜂鸣器
#define Kick_IO 	PBout(0)   		//弹射 

#define ESP_IN_1 	PEin(2)   		//通讯模块 输入1
#define ESP_IN_2 	PEin(3)   		//通讯模块 输入2

#define KEY_BMI 	PEin(11)   		//按键 BMI088
#define KEY_RUN 	PEin(12)   		//按键 RUN
#define KEY_3 		PEin(13)   		//按键 KEY3
#define KEY_2 		PEin(14)   		//按键 KEY2
#define KEY_1 		PEin(15)   		//按键 KEY1



#define LED_RUN PCout(2)   	//正常运行，绿灯 0：亮 ； 1：灭
#define LED_ERR PCout(3)   	//错误，红灯		0：亮 ； 1：灭

#define Power_Supply_3V3_EN 	PCout(5)   	//3V3_EN
#define Power_Supply_5V_EN 		PBout(1)   	//5V_EN
#define Power_Supply_24V_EN 	PFout(11)   //24V_EN

#define Power_Supply_3V3_Test 	PBin(0)   	//3V3_Test
#define Power_Supply_5V_Test 	PBin(2)   	//5V_Test
#define Power_Supply_24V_Test 	PFin(12)   	//24V_Test

/* 扩展变量 ------------------------------------------------------------------*/
/* 函数声明 ------------------------------------------------------------------*/
void My_Delay_us(u16 us);
void LED_GPIO_Init(void);



#endif 

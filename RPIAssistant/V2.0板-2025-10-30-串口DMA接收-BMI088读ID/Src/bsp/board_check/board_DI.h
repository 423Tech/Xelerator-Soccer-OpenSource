#ifndef __BOARD_DI_H__
#define __BOARD_DI_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "led/bsp_led.h"
//************************  测试项目5，24路LED点亮后，通道检测   ************************
#define DI_5_LED_Channel_Check_INT_1 	PAin(12)
#define DI_5_LED_Channel_Check_INT_2 	PAin(11) 
#define DI_5_LED_Channel_Check_INT_3 	PAin(10) 
#define DI_5_LED_Channel_Check_INT_4 	PAin(9) 
#define DI_5_LED_Channel_Check_INT_5 	PAin(8)   	
#define DI_5_LED_Channel_Check_INT_6 	PCin(9) 
#define DI_5_LED_Channel_Check_INT_7 	PCin(8) 
#define DI_5_LED_Channel_Check_INT_8 	PCin(7) 
#define DI_5_LED_Channel_Check_INT_9 	PCin(6)   	
#define DI_5_LED_Channel_Check_INT_10 	PGin(8) 
#define DI_5_LED_Channel_Check_INT_11 	PGin(7) 
#define DI_5_LED_Channel_Check_INT_12 	PGin(6) 
#define DI_5_LED_Channel_Check_INT_13 	PGin(5)   	
#define DI_5_LED_Channel_Check_INT_14 	PGin(4) 
#define DI_5_LED_Channel_Check_INT_15 	PGin(3) 
#define DI_5_LED_Channel_Check_INT_16 	PGin(2) 
#define DI_5_LED_Channel_Check_INT_17 	PDin(15)   	
#define DI_5_LED_Channel_Check_INT_18 	PDin(14) 
#define DI_5_LED_Channel_Check_INT_19 	PDin(13) 
#define DI_5_LED_Channel_Check_INT_20 	PDin(12) 
#define DI_5_LED_Channel_Check_INT_21 	PDin(11) 
#define DI_5_LED_Channel_Check_INT_22 	PDin(10)   	
#define DI_5_LED_Channel_Check_INT_23 	PDin(9) 
#define DI_5_LED_Channel_Check_INT_24 	PDin(8) 

//************************  测试项目6，24路LED点亮后，断线检测   ************************
#define DI_6_LED_Cut_Check_INT_1 	PEin(1)
#define DI_6_LED_Cut_Check_INT_2 	PEin(0) 
#define DI_6_LED_Cut_Check_INT_3 	PBin(9) 
#define DI_6_LED_Cut_Check_INT_4 	PBin(8) 
#define DI_6_LED_Cut_Check_INT_5 	PBin(7)   	
#define DI_6_LED_Cut_Check_INT_6 	PBin(6) 
#define DI_6_LED_Cut_Check_INT_7 	PBin(5) 
#define DI_6_LED_Cut_Check_INT_8 	PBin(4) 
#define DI_6_LED_Cut_Check_INT_9 	PBin(3)   	
#define DI_6_LED_Cut_Check_INT_10 	PGin(15) 
#define DI_6_LED_Cut_Check_INT_11 	PGin(14) 
#define DI_6_LED_Cut_Check_INT_12 	PGin(13) 
#define DI_6_LED_Cut_Check_INT_13 	PGin(12)   	
#define DI_6_LED_Cut_Check_INT_14 	PGin(11) 
#define DI_6_LED_Cut_Check_INT_15 	PGin(10) 
#define DI_6_LED_Cut_Check_INT_16 	PGin(9) 
#define DI_6_LED_Cut_Check_INT_17 	PDin(7)   	
#define DI_6_LED_Cut_Check_INT_18 	PDin(6) 
#define DI_6_LED_Cut_Check_INT_19 	PDin(5) 
#define DI_6_LED_Cut_Check_INT_20 	PDin(4) 
#define DI_6_LED_Cut_Check_INT_21 	PDin(3) 
#define DI_6_LED_Cut_Check_INT_22 	PDin(2)   	
#define DI_6_LED_Cut_Check_INT_23 	PDin(1) 
#define DI_6_LED_Cut_Check_INT_24 	PDin(0) 


void DI_1_Short_Check(void);	//DI板，测试项目1，短路测试，3V3、5V
void DI_2_Epprom_Check(void);
void DI_3_HC595_GPIO_Init(void);
void DI_3_LED_ON_Set_ALL(u8 state);	//24 个 LED 全控制
void DI_3_LED_ON_Set_Channel(u8 ch);	//单个LED控制

void DI_5_LED_Channel_GPIO_Init(void);//测试项目5，24路LED点亮后，通道检测 ,初始化引脚
u8 DI_5_LED_Channel_Check(u8 ch);	//测试项目5，24路LED点亮后，单独通道检测
void DI_6_LED_Cut_GPIO_Init(void);//测试项目6，24路LED点亮后，断线检测 ,初始化引脚
u8 DI_6_LED_Cut_Check(u8 ch);	//测试项目6，24路LED点亮后，单独断线检测
void DI_3456_LED_ON_Check_Channel(u8 ch);//单独点亮某一通道，检测3、4、5、6项目 （摄像头检测LED好坏、通道检测、断线检测）
void DI_3456_LED_Check_Result(void);		//DI 卡，LED 通道检测、断线检测，结果汇总，全合格才算合格
void DI_3456_LED_ON_Check_Result_CLR(void);//检测4、5、6项目 （摄像头检测LED好坏、通道检测、断线检测）结果 清零
void DI_Board_Check_LED_Result_Deal(void);		//DI板 处理所有结果，判断是否全部合格
void DI_Board_Init_ALL(void);//DI初始化所有
void DI_Board_Check(void);//DI板检测所有
void DI_Check_Reset(void);	//DI板，测试项目复位


#endif  // __BSP_LED_H__



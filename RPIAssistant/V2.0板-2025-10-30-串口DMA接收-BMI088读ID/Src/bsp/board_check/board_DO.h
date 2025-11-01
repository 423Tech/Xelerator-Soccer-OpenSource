#ifndef __BOARD_DO_H__
#define __BOARD_DO_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "led/bsp_led.h"
//************************  测试项目4，16路LED点亮后，断线检测   ************************
#define DO_4_LED_Cut_Check_INT_1 	PEin(1)
#define DO_4_LED_Cut_Check_INT_2 	PEin(0) 
#define DO_4_LED_Cut_Check_INT_3 	PBin(9) 
#define DO_4_LED_Cut_Check_INT_4 	PBin(8) 
#define DO_4_LED_Cut_Check_INT_5 	PBin(7)   	
#define DO_4_LED_Cut_Check_INT_6 	PBin(6) 
#define DO_4_LED_Cut_Check_INT_7 	PBin(5) 
#define DO_4_LED_Cut_Check_INT_8 	PBin(4) 
#define DO_4_LED_Cut_Check_INT_9 	PBin(3)   	
#define DO_4_LED_Cut_Check_INT_10 	PGin(15) 
#define DO_4_LED_Cut_Check_INT_11 	PGin(14) 
#define DO_4_LED_Cut_Check_INT_12 	PGin(13) 
#define DO_4_LED_Cut_Check_INT_13 	PGin(12)   	
#define DO_4_LED_Cut_Check_INT_14 	PGin(11) 
#define DO_4_LED_Cut_Check_INT_15 	PGin(10) 
#define DO_4_LED_Cut_Check_INT_16 	PGin(9) 


void DO_1_Short_Check(void);	//DI板，测试项目1，短路测试，3V3、5V
void DO_2_Epprom_Check(void);
void DO_3_HC595_GPIO_Init(void);
void DO_3_LED_ON_Set_ALL(u8 state);			//16 路 5V 全控制
void DO_34_5V_ON_Check_Channel(u8 ch);		//单独点亮某一通道，检测3、4项目 （摄像头检测LED好坏、通道检测、断线检测）
void DO_34_LED_ON_Check_Channel(u8 ch);		//单独点亮某一通道，检测3、4项目 （摄像头检测LED好坏、通道检测、断线检测）
void DO_34_LED_Check_Result(void);			//DO 卡，LED 通道检测、断线检测，结果汇总，全合格才算合格
void DO_Board_Check_LED_Result_Deal(void);		//DO卡，处理所有结果，判断是否全部合格
void DO_Board_Init_ALL(void);//DO卡，初始化所有
void DO_Board_Check(void);//DO卡，检测所有
void DO_Check_Reset(void);	//DI板，测试项目复位
#endif  // __BSP_LED_H__



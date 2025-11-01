#ifndef __BOARD_AI_H__
#define __BOARD_AI_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "led/bsp_led.h"

//************************  测试项目3，8路LED点亮   ************************
#define AI_3_LED_Channel_1 PEout(9)   	
#define AI_3_LED_Channel_2 PEout(8)
#define AI_3_LED_Channel_3 PEout(7)
#define AI_3_LED_Channel_4 PGout(1)
#define AI_3_LED_Channel_5 PGout(0)
#define AI_3_LED_Channel_6 PFout(15)
#define AI_3_LED_Channel_7 PFout(14)
#define AI_3_LED_Channel_8 PFout(13)

#define AI_6_15V_Test_A PEin(2)
#define AI_6_15V_Test_B PEin(3)


void AI_1_Short_Check(void);	//AI板，测试项目1，短路测试，3V3、5V、24V
void AI_2_Epprom_Check(void);	//AI板，测试项目2，EEPROM 读写检测
void AI_3_LED_GPIO_Init(void);	//测试项目3，8路LED,初始化引脚
void AI_3_LED_Set_All(u8 state);	////测试项目3，8路LED,全部控制 ,1:亮 ；0：灭
void AI_3_LED_Set_Channel(u8 ch,u8 state);	//测试项目3，8路LED,,单个LED控制,ch:通道1~8 ； state,1亮 ； 0：灭
void AI_3_LED_Check(u8 ch);	//测试项目3，8路LED,检测
void AI_4_Current_Out_Channel(u8 ch);	//AI板，测试项目4，单通道 电流输出
void AI_4_Current_Out_CLR(void);	//AI板，测试项目4，8路电流输出,清零
void AI_5_SGM58200_Init(void);	//AI板，测试项目5，被测板上的，SGM58200，初始化
float AI_5_Current_Read(u8 ch);	//AI板，测试项目5，读SGM58200数据
void AI_45_Current_Check(void);	//测试项目4、5，循环检测8路电流值
void AI_6_15V_GPIO_Init(void);	//AI板，测试项目5，读SGM58200数据
void AI_6_15V_Test(void);	//AI板，测试项目6，正负15V电压检测
void AI_Board_Init_ALL(void);//AI初始化所有
void AI_Board_Check(void);//AI板检测所有
void AI_Check_Reset(void);	//AI板，测试项目复位
#endif 


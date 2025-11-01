#ifndef __BOARD_AO_H__
#define __BOARD_AO_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "led/bsp_led.h"

//************************  测试项目3，8路LED点亮   ************************
#define AO_3_LED_Channel_1 PEout(9)   	
#define AO_3_LED_Channel_2 PEout(8)
#define AO_3_LED_Channel_3 PEout(7)
#define AO_3_LED_Channel_4 PGout(1)


#define AO_6_15V_Test_A PEin(2)
#define AO_6_15V_Test_B PEin(3)



void AO_1_Short_Check(void);	//AO板，测试项目1，短路测试，3V3、5V、24V
void AO_2_Epprom_Check(void);	//AO板，测试项目2，EEPROM 读写检测
void AO_3_LED_GPIO_Init(void);	//测试项目3，4路LED,初始化引脚
void AO_3_LED_Set_All(u8 state);	////测试项目3，4路LED,全部控制 ,1:亮 ；0：灭
void AO_3_LED_Set_Channel(u8 ch,u8 state);	//测试项目3，4路LED,,单个LED控制,ch:通道1~8 ； state,1亮 ； 0：灭
void AO_3_LED_Check(u8 ch);					//测试项目3，4路LED,检测

void AO_4_TPC116S1_Set_DAC(u8 ch);		//AO板，测试项目4,被测板上 TPC116S1，输出DAC 
void AO_4_TPC116S1_Set_DAC_CLR(u8 ch);	//AO板，测试项目4,被测板上 TPC116S1，输出DAC  清零  
void AO_456_Current_AND_ADC_Check(void);//测试项目4、5、6，SPI设置电流，IIC电流检测、ADC检测


void AO_Board_Init_ALL(void);//AO初始化所有
void AO_Board_Check(void);//AO板检测所有
void AO_Check_Reset(void);	//AO板，测试项目复位
#endif 


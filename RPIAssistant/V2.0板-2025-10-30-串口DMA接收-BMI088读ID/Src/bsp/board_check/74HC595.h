#ifndef __74HC595_H__
#define __74HC595_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "led/bsp_led.h"
#define HC595_SIN(x,SIN) (x ? HAL_GPIO_WritePin(SIN->SIN_PORT, SIN->SIN_PIN,GPIO_PIN_SET): HAL_GPIO_WritePin(SIN->SIN_PORT, SIN->SIN_PIN,GPIO_PIN_RESET))
#define HC595_RCK(x,RCK) (x ? HAL_GPIO_WritePin(RCK->RCK_PORT, RCK->RCK_PIN,GPIO_PIN_SET): HAL_GPIO_WritePin(RCK->RCK_PORT, RCK->RCK_PIN,GPIO_PIN_RESET))
#define HC595_SCK(x,SCK) (x ? HAL_GPIO_WritePin(SCK->SCK_PORT, SCK->SCK_PIN,GPIO_PIN_SET): HAL_GPIO_WritePin(SCK->SCK_PORT, SCK->SCK_PIN,GPIO_PIN_RESET))

typedef	struct
{
	GPIO_TypeDef* 	SIN_PORT;	//DS
	uint16_t 		SIN_PIN;	//DS
	GPIO_TypeDef* 	RCK_PORT;	//SCTCP
	uint16_t 		RCK_PIN;	//SCTCP
	GPIO_TypeDef* 	SCK_PORT;	//SCHCP
	uint16_t 		SCK_PIN;	//SCHCP

}HC595_TypeDef;

extern HC595_TypeDef HC595_1;
extern HC595_TypeDef HC595_2;

void HC595_GPIO_Init(HC595_TypeDef *HC595);//初始化 74HC595 ，GPIO引脚

void HC595_Send_Byte(HC595_TypeDef *HC595,u8 byte);
void HC595_CS(HC595_TypeDef *HC595);
void HC595_Send_N_Byte(HC595_TypeDef *HC595,u8 *data, u16 len);	

#endif  



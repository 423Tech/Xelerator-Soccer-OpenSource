#ifndef _MYIIC_H
#define _MYIIC_H
#include "stm32f4xx_hal.h"
#include "led.h"
#include "math.h"
////////////////////////////////////////////////////////////////////////////////// 	

#define IIC_SCL(x,IIC) (x ? HAL_GPIO_WritePin(IIC->SCL_PORT, IIC->SCL_PIN,GPIO_PIN_SET): HAL_GPIO_WritePin(IIC->SCL_PORT, IIC->SCL_PIN,GPIO_PIN_RESET))
#define IIC_SDA(x,IIC) (x ? HAL_GPIO_WritePin(IIC->SDA_PORT, IIC->SDA_PIN,GPIO_PIN_SET): HAL_GPIO_WritePin(IIC->SDA_PORT, IIC->SDA_PIN,GPIO_PIN_RESET))

#define READ_SDA(IIC) HAL_GPIO_ReadPin(IIC->SDA_PORT, IIC->SDA_PIN)
#define READ_SCL(IIC) HAL_GPIO_ReadPin(IIC->SCL_PORT, IIC->SCL_PIN)


typedef	struct
{
	GPIO_TypeDef* 	SCL_PORT;
	uint16_t 		SCL_PIN;
	GPIO_TypeDef* 	SDA_PORT;
	uint16_t 		SDA_PIN;
}IIC_TypeDef;

extern IIC_TypeDef IIC1;

//IIC所有操作函数

void IIC_SDA_IN(IIC_TypeDef * IIC);
void IIC_SDA_OUT(IIC_TypeDef * IIC);
void IIC_Init(IIC_TypeDef * IIC);              	//初始化IIC的IO口				 
void IIC_Start(IIC_TypeDef * IIC);					//发送IIC开始信号
void IIC_Stop(IIC_TypeDef * IIC);	  				//发送IIC停止信号
void IIC_Send_Byte(IIC_TypeDef * IIC,u8 txd);			//IIC发送一个字节
u8 IIC_Read_Byte(IIC_TypeDef * IIC,unsigned char ack);	//IIC读取一个字节
u8 IIC_Wait_Ack(IIC_TypeDef * IIC); 				//IIC等待ACK信号
void IIC_Ack(IIC_TypeDef * IIC);					//IIC发送ACK信号
void IIC_NAck(IIC_TypeDef * IIC);				//IIC不发送ACK信号


#endif


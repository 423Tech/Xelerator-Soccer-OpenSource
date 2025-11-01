/* 包含头文件 ----------------------------------------------------------------*/
#include "board_check.h"
#include "usart/bsp_debug_usart.h"
#include "led/bsp_led.h"
#include "74HC595.h"

//#define DI_3_HC595_SIN   PFout(3) //DS
//#define DI_3_HC595_RCK   PFout(4) //SCTCP
//#define DI_3_HC595_SCK   PFout(5)  //SCHCP

/***
 *74HC595 发送一个字节 
 *即往74HC595的DS引脚发送一个字节
*/

HC595_TypeDef HC595_1=
{
	GPIOF,GPIO_PIN_0,//SIN 	//DS
	GPIOF,GPIO_PIN_1,//RCK	//SCTCP
	GPIOF,GPIO_PIN_2,//RCK	//SCHCP
};
HC595_TypeDef HC595_2=
{
	GPIOF,GPIO_PIN_3,//SIN 	//DS
	GPIOF,GPIO_PIN_4,//RCK	//SCTCP
	GPIOF,GPIO_PIN_5,//RCK	//SCHCP
};
void HC595_GPIO_Init(HC595_TypeDef *HC595)//初始化 74HC595 ，GPIO引脚
{
	GPIO_InitTypeDef GPIO_InitStruct;
	__HAL_RCC_GPIOF_CLK_ENABLE();
	GPIO_InitStruct.Pin = HC595->SIN_PIN|HC595->RCK_PIN|HC595->SCK_PIN;	//DI板 SIN ; RCK ; SCK 
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOF, &GPIO_InitStruct);
	
	HAL_GPIO_WritePin(HC595->SIN_PORT, HC595->SIN_PIN,GPIO_PIN_RESET);
	HAL_GPIO_WritePin(HC595->SIN_PORT, HC595->SIN_PIN,GPIO_PIN_RESET);
	HAL_GPIO_WritePin(HC595->SIN_PORT, HC595->SIN_PIN,GPIO_PIN_RESET);
}

u8 HC595_delay=10;
void HC595_Send_Byte(HC595_TypeDef *HC595,u8 byte)
{
	u8 i;
	for (i = 0; i < 8; i ++)  //一个字节8位，传输8次，一次一位，循环8次，刚好移完8位
	{

		  /****  步骤1：将数据传到DS引脚    ****/
			if (byte & 0x80)        //先传输高位，通过与运算判断第八是否为1
				HC595_SIN(1,HC595);	//如果第八位是1，则与 595 DS连接的引脚输出高电平
			else                    //否则输出低电平
				HC595_SIN(0,HC595);
			/*** 步骤2：SHCP每产生一个上升沿，当前的bit就被送入移位寄存器 ***/
			HC595_SCK(0,HC595);	// SHCP拉低
			My_Delay_us(HC595_delay);           // 适当延时
			HC595_SCK(1,HC595);// SHCP拉高， SHCP产生上升沿
			My_Delay_us(HC595_delay);
			byte <<= 1;		// 左移一位，将低位往高位移，通过	if (byte & 0x80)判断低位是否为1	
	}
}
 
/**
 *74HC595输出锁存 使能 
**/
void HC595_CS(HC595_TypeDef *HC595) 
{
		/**  步骤3：STCP产生一个上升沿，移位寄存器的数据移入存储寄存器  **/
		HC595_RCK(0,HC595);// 将STCP拉低
		My_Delay_us(HC595_delay);           // 适当延时
		HC595_RCK(1,HC595);// 再将STCP拉高，STCP即可产生一个上升沿
		My_Delay_us(HC595_delay);
}
 
/**
 *发送多个字节
 *便于级联时数据的发送
 *级联N级，就需要发送N个字节控制HC595
***/
void HC595_Send_N_Byte(HC595_TypeDef *HC595,u8 *data, u16 len)
{
	u8 i;
	for (i = 0; i < len; i ++ ) // len 个字节
	{
		HC595_Send_Byte(HC595,data[i]);
	}
	HC595_CS(HC595); //先把所有字节发送完，再使能输出
}


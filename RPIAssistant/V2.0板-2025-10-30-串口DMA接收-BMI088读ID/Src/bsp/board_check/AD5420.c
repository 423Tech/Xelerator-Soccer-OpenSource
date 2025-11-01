/* 包含头文件 ----------------------------------------------------------------*/
#include "board_DI.h"
#include "usart/bsp_debug_usart.h"
#include "AD5420.h"
#include "led/bsp_led.h"
//---------------------------------
//void WriteToAD5420(unsigned char count,unsigned char *Buf);
//---------------------------------
//Function that writes to the AD5420 via the SPI port.
//--------------------------------------------------------------------------------
u16 AD5420_delay_us=100;
void WriteToAD5420(unsigned char count,unsigned char *Buf)
{
	unsigned char ValueToWrite = 0;
	unsigned char i = 0;
	unsigned char j = 0;
	CLR_LATCH();
		for ( i=count;i>0;i-- )
		{
			ValueToWrite = *(Buf+i-1);
			for (j=0; j<8; j++)
			{
				CLR_SCL();
				if(0x80 == (ValueToWrite & 0x80))
				{
					SET_SDO(); //Send one to SDIN pin of AD5420
				}
				else
				{
					CLR_SDO(); //Send zero to SDIN pin of AD5420
				}
				My_Delay_us(AD5420_delay_us);
				SET_SCL();
				My_Delay_us(AD5420_delay_us);
				ValueToWrite <<= 1; //Rotate data
			}
		}	
	CLR_SCL();
	My_Delay_us(AD5420_delay_us);
	SET_LATCH();
	My_Delay_us(AD5420_delay_us);
}
void WriteToAD5420_REG_DATA(u8 data_H,u8 data_L,u8 reg,u8 times)
{
	unsigned char Buf[3];
	unsigned char ValueToWrite = 0;
	unsigned char i = 0;
	unsigned char j = 0;
	unsigned char count = 0;
	Buf[2] = reg;
	Buf[1] = data_H;
	Buf[0] = data_L;

	for(count=0;count<times;count++)
	{
		for ( i=3;i>0;i-- )
		{
			ValueToWrite = *(Buf+i-1);
			for (j=0; j<8; j++)
			{
				CLR_SCL();
				if(0x80 == (ValueToWrite & 0x80))
				{
					SET_SDO(); //Send one to SDIN pin of AD5420
				}
				else
				{
					CLR_SDO(); //Send zero to SDIN pin of AD5420
				}
				My_Delay_us(AD5420_delay_us);
				SET_SCL();
				My_Delay_us(AD5420_delay_us);
				ValueToWrite <<= 1; //Rotate data
			}
		}
		CLR_SCL();
		My_Delay_us(AD5420_delay_us);	
		SET_LATCH();
		My_Delay_us(AD5420_delay_us);
		CLR_LATCH();	
		My_Delay_us(AD5420_delay_us);		
	}



}
//---------------------------------
//Function that reads from the AD5420 via the SPI port.
//--------------------------------------------------------------------------------
void ReadFromAD5420(unsigned char count,unsigned char *buf)
{
	unsigned char i = 0;
	unsigned char j = 0;
	unsigned int iTemp = 0;
	unsigned char RotateData = 0;
	CLR_LATCH();
	for(j=count; j>0; j--)
	{
		for(i=0; i<8; i++)
		{
			CLR_SCL();
			RotateData <<= 1; //Rotate data
			My_Delay_us(1);
			CLR_SDO(); //write a nop condition when read the data.
			iTemp = AD5420_READ; //Read SDO of AD5420
			SET_SCL();
			if(0x00000020 == (iTemp & 0x00000020))
			{
				RotateData |= 1;
			}
			My_Delay_us(AD5420_delay_us);
		}
		*(buf+j-1)= RotateData;
	}
	CLR_SCL();
	My_Delay_us(AD5420_delay_us);
	SET_LATCH();
	My_Delay_us(AD5420_delay_us);
}

void AD5420_GPIO_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	__HAL_RCC_GPIOA_CLK_ENABLE();
	__HAL_RCC_GPIOC_CLK_ENABLE();

//**************  输出	**************
	// A4:CLEAR ; A5:SCLK ; A6:MISO(SDO) ; A7:MOSI(SDIN)  ; C4:LATCH
	GPIO_InitStruct.Pin = GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_7;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);  	

	GPIO_InitStruct.Pin = GPIO_PIN_6;
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_PULLDOWN;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);  
	
	GPIO_InitStruct.Pin = GPIO_PIN_4;//LATCH
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);  
	CLR_CLEAR();
}
void AD5420_Conf_Init(void)//AD5420 模式配置
{
	WriteToAD5420_REG_DATA(0x00,0x01,AD5420_RESET_REG_ADDR,1);HAL_Delay(10);//复位寄存器
	WriteToAD5420_REG_DATA(0x30,0x0F,AD5420_CONTROL_REG_ADDR,1);HAL_Delay(10);	//控制寄存器
	WriteToAD5420_REG_DATA(0x00,0x00,AD5420_DATA_REG_ADDR,8);HAL_Delay(10);		//数据寄存器 //0mA	
}

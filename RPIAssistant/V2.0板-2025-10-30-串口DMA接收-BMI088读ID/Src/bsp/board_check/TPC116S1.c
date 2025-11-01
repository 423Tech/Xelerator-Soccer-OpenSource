/* 包含头文件 ----------------------------------------------------------------*/
#include "board_DI.h"
#include "usart/bsp_debug_usart.h"
#include "TPC116S1.h"
#include "led/bsp_led.h"
SPI_NSS_TypeDef SPI_NSS1=
{
	GPIOE,GPIO_PIN_10,//NSS1
};
SPI_NSS_TypeDef SPI_NSS2=
{
	GPIOE,GPIO_PIN_11,//NSS2
};
SPI_NSS_TypeDef SPI_NSS3=
{
	GPIOE,GPIO_PIN_12,//NSS3
};
SPI_NSS_TypeDef SPI_NSS4=
{
	GPIOE,GPIO_PIN_13,//NSS4
};
//IIC_初始化
void TPC116S1_GPIO_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	__HAL_RCC_GPIOB_CLK_ENABLE();
	__HAL_RCC_GPIOE_CLK_ENABLE();
//**************  输出	**************
	// E10:NSS1 ; B13:SCLK ; B14:MISO(SDO) ; B15:MOSI(SDIN)  ;
	GPIO_InitStruct.Pin = GPIO_PIN_13|GPIO_PIN_15;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);  	

	GPIO_InitStruct.Pin = GPIO_PIN_14;
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
//	GPIO_InitStruct.Pull = GPIO_PULLDOWN;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);  
	
	GPIO_InitStruct.Pin = GPIO_PIN_10|GPIO_PIN_11|GPIO_PIN_12|GPIO_PIN_13;//LATCH
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);  
	
	TPC116S1_MISO=1;
	
	TPC116S1_NSS1=1;
	TPC116S1_NSS2=1;
	TPC116S1_NSS3=1;
	TPC116S1_NSS4=1;
}
u8 TPC116S1_delay_us =100;
void set_tpc_value(SPI_NSS_TypeDef * NSS,uint16_t val)
{
		uint8_t Buf[3] = {0};
		uint8_t ValueToWrite = 0;
		
		Buf[2] = 0x00; //Normal operation
		Buf[1] = (uint8_t)(val>>8);		//H
		Buf[0] = (uint8_t)(val&0xff);	//L
//		TPC116S1_NSS4=0;
		SPI_NSS(0,NSS);
		HAL_Delay(1);	
		u8 i,j;
		for ( i=3;i>0;i-- )
		{
			ValueToWrite = *(Buf+i-1);
			for (j=0; j<8; j++)
			{
				TPC116S1_SCK=0;
				if(0x80 == (ValueToWrite & 0x80))
				{
					TPC116S1_MOSI=1; //Send one to SDIN pin of AD5420
				}
				else
				{
					TPC116S1_MOSI=0; //Send zero to SDIN pin of AD5420
				}
				My_Delay_us(TPC116S1_delay_us);

				TPC116S1_SCK=1;
				My_Delay_us(TPC116S1_delay_us);
				ValueToWrite <<= 1; //Rotate data
			}
		}
//		HAL_Delay(1);
		TPC116S1_SCK=0;
		My_Delay_us(TPC116S1_delay_us);
//		TPC116S1_NSS4=1;
		SPI_NSS(1,NSS);

}

float cal_current_val(SPI_NSS_TypeDef * NSS,uint16_t val){
		return (float)val/65535.0f*4.096f/3/56.2;
}

void set_tpc_ma_current_value(SPI_NSS_TypeDef * NSS,float cur)
	{
		uint16_t val = (uint16_t)(cur/1000*56.2*3/4.096*65536);
	printf("val is %x\r\n", val);
	set_tpc_value(NSS,val);
}         


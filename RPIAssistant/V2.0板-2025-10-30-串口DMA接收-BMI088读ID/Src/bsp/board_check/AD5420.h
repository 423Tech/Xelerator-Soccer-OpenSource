#ifndef __AD5420_H__
#define __AD5420_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "led/bsp_led.h"

	// A4:CLEAR ; A5:SCLK ; A6:MISO(SDO) ; A7:MOSI(SDIN)  ; C4:LATCH
#define SET_CLEAR() PAout(4)=1
#define CLR_CLEAR() PAout(4)=0
#define SET_LATCH() PCout(4)=1
#define CLR_LATCH() PCout(4)=0
#define SET_SCL() PAout(5)=1
#define CLR_SCL() PAout(5)=0
#define SET_SDO() PAout(7)=1
#define CLR_SDO() PAout(7)=0
#define AD5420_READ PAin(6)

/*! \brief Internal address of DAC CONTROL register.*/
#define AD5420_CONTROL_REG_ADDR  0x55
/*! \brief Internal address of DAC DATA register.*/
#define AD5420_DATA_REG_ADDR     0x01
/*! \brief Internal address of DAC RESET register.*/
#define AD5420_RESET_REG_ADDR    0x56

//Function that writes to the AD5420 via the SPI port.
//--------------------------------------------------------------------------------
void WriteToAD5420(unsigned char count,unsigned char *Buf);
void WriteToAD5420_REG_DATA(u8 data_H,u8 data_L,u8 reg,u8 times);
//Function that reads from the AD7190 via the SPI port.
//--------------------------------------------------------------------------------
void ReadFromAD5420(unsigned char count,unsigned char *buf);
void AD5420_GPIO_Init(void);//IO初始化
void AD5420_Conf_Init(void);//AD5420 模式配置
void delay (int length);


#endif  // __BSP_LED_H__



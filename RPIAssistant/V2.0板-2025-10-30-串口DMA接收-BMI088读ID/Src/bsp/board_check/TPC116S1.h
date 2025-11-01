#ifndef __TPC116S1_H__
#define __TPC116S1_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "led/bsp_led.h"
#include "math.h"
#define SPI_NSS(x,NSS) (x ? HAL_GPIO_WritePin(NSS->NSS_PORT, NSS->NSS_PIN,GPIO_PIN_SET): HAL_GPIO_WritePin(NSS->NSS_PORT, NSS->NSS_PIN,GPIO_PIN_RESET))

typedef	struct
{
	GPIO_TypeDef* 	NSS_PORT;
	uint16_t 		NSS_PIN;
}SPI_NSS_TypeDef;

extern SPI_NSS_TypeDef SPI_NSS1;
extern SPI_NSS_TypeDef SPI_NSS2;
extern SPI_NSS_TypeDef SPI_NSS3;
extern SPI_NSS_TypeDef SPI_NSS4;

#define TPC116S1_SCK PBout(13)
#define TPC116S1_MISO PBout(14)
#define TPC116S1_MOSI PBout(15)

#define TPC116S1_NSS1 PEout(10)
#define TPC116S1_NSS2 PEout(11)
#define TPC116S1_NSS3 PEout(12)
#define TPC116S1_NSS4 PEout(13)


u8 SPI2_ReadWriteByte(u8 TxData);

void TPC116S1_GPIO_Init(void);
//void set_tpc_value(uint16_t val);
//void set_tpc_ma_current_value(float cur);

void set_tpc_value(SPI_NSS_TypeDef * NSS,uint16_t val);
float cal_current_val(SPI_NSS_TypeDef * NSS,uint16_t val);
void set_tpc_ma_current_value(SPI_NSS_TypeDef * NSS,float cur);
void TPC116S1_Init(void);


#endif  



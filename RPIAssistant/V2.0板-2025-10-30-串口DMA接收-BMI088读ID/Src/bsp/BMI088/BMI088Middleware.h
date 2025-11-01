#ifndef BMI088MIDDLEWARE_H
#define BMI088MIDDLEWARE_H

#include "stm32f4xx_hal.h"
#include "system.h"

#define BMI088_USE_SPI
//#define BMI088_USE_IIC

#define BMI088_CS_GYRO 		PDout(12)   	// BMI088_CS_GYRO
#define BMI088_CS_ACC 		PDout(9)   	// BMI088_CS_GYRO
//#define KEY_BMI 	PEin(11)   		//°´¼ü BMI088

void BMI088_GPIO_init(void);
void BMI088_com_init(void);
void BMI088_delay_ms(uint16_t ms);
void BMI088_delay_us(uint16_t us);

#if defined(BMI088_USE_SPI)
extern void BMI088_ACCEL_NS_L(void);
extern void BMI088_ACCEL_NS_H(void);

extern void BMI088_GYRO_NS_L(void);
extern void BMI088_GYRO_NS_H(void);

extern uint8_t BMI088_read_write_byte(uint8_t reg);

#elif defined(BMI088_USE_IIC)

#endif

#endif

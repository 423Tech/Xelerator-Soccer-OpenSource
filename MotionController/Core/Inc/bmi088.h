/*
 * bmi088.h
 *
 *  Created on: Nov 29, 2025
 *      Author: yehui
 */

#ifndef INC_BMI088_H_
#define INC_BMI088_H_

#define BMI088_CAPTURE_DRDY_TIMESTAMP() bmi088_drdy_timestamp = DWT->CYCCNT

extern volatile uint32_t bmi088_drdy_timestamp;
extern float bmi088_gyro_angle[3];

void bmi088_write_gyro(uint8_t reg, uint8_t data);
void bmi088_read_gyro(uint8_t reg, uint8_t *data);
void bmi088_burst_read_gyro(uint8_t reg, int size);
void bmi088_init_gyro(void);
void bmi088_process_gyro_angle(void);

#endif /* INC_BMI088_H_ */

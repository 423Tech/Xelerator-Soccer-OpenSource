/*
 * bmi088.h
 *
 *  Created on: Nov 29, 2025
 *      Author: yehui
 */

#ifndef INC_BMI088_H_
#define INC_BMI088_H_

extern float gyro_angle[3];

void write_gyro(uint8_t reg, uint8_t data);
void read_gyro(uint8_t reg, uint8_t *data);
void burst_read_gyro(uint8_t reg, int size);
void init_gyro(void);
void process_gyro_angle(void);

#endif /* INC_BMI088_H_ */

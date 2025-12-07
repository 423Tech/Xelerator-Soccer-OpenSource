/*
 * bmi088.h
 *
 *  Created on: Nov 29, 2025
 *      Author: yehui
 */

#ifndef INC_BMI088_H_
#define INC_BMI088_H_

extern volatile float bmi088_gyro_angle[3];

void bmi088_init_gyro(void);
void bmi088_calibrate_gyro_zero_bias(int calibration_samples_num);

#endif /* INC_BMI088_H_ */

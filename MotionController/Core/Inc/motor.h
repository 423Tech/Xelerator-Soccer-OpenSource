/*
 * motor.h
 *
 *  Created on: Nov 29, 2025
 *      Author: yehui
 */

#ifndef INC_MOTOR_H_
#define INC_MOTOR_H_

extern volatile float motor_target_wheels_rpm[4];

void motor_init(void);

#endif /* INC_MOTOR_H_ */

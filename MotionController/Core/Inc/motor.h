/*
 * motor.h
 *
 *  Created on: Nov 29, 2025
 *      Author: yehui
 */

#ifndef INC_MOTOR_H_
#define INC_MOTOR_H_

extern float target_wheel_rpm[4];

void init_motor(void);
void wheel_pwm_update(void);

#endif /* INC_MOTOR_H_ */

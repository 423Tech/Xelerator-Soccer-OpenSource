/*
 * motor.h
 *
 *  Created on: Nov 29, 2025
 *      Author: yehui
 */

#ifndef INC_MOTOR_H_
#define INC_MOTOR_H_

#define MOTOR_SET_WHEELS_RPM(wheel_idx, rpm) motor_target_wheels_rpm[wheel_idx] = rpm

extern volatile float motor_target_wheels_rpm[4];

void motor_init(void);
void motor_update_wheels_pwm(void);

#endif /* INC_MOTOR_H_ */

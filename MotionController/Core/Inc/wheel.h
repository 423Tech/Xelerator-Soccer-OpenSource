/*
 * wheel.h
 *
 *  Created on: Jan 13, 2026
 *      Author: yehui
 */

#ifndef INC_WHEEL_H_
#define INC_WHEEL_H_

extern float wheel_target_speed_rpm[4];

void wheel_init(void);
void wheel_update_pwm(void);

#endif /* INC_WHEEL_H_ */

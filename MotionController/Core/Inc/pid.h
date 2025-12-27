/*
 * pid.h
 *
 *  Created on: Dec 27, 2025
 *      Author: yehui
 */

#ifndef INC_PID_H_
#define INC_PID_H_

struct pid_context {
    float kp;
    float ki;
    float kd;

    float last_error;
	float integral;
	float derivative;

    float zero_deadband;
    enum {
        PID_ACTIVE,
		PID_OBSERVING,
		PID_INACTIVE
    } state;
};

void pid_init_context(struct pid_context *context);
void pid_set_gains(struct pid_context *context, float kp, float ki, float kd);
void pid_set_zero_deadband(struct pid_context *context, float zero_deadband);
float pid(struct pid_context *context, float expected, float actual);

#endif /* INC_PID_H_ */

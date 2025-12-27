/*
 * pid.c
 *
 *  Created on: Dec 27, 2025
 *      Author: yehui
 */

#include "pid.h"

void pid_init_context(struct pid_context *context)
{
    context->kp = 0;
    context->ki = 0;
    context->kd = 0;
    context->last_error = 0;
    context->integral = 0;
    context->derivative = 0;
    context->zero_deadband = 0;
    context->state = PID_INACTIVE;
}

void pid_set_gains(struct pid_context *context, float kp, float ki, float kd)
{
    context->kp = kp;
    context->ki = ki;
    context->kd = kd;
}

void pid_set_zero_deadband(struct pid_context *context, float zero_deadband)
{
    context->zero_deadband = zero_deadband;
}

float pid(struct pid_context *context, float expected, float actual)
{
	float error = expected - actual;
	switch(context->state) {
	case PID_ACTIVE:
		if (expected == 0 && error > -context->zero_deadband && error < context->zero_deadband)
			context->state = PID_OBSERVING;
		break;
	case PID_OBSERVING:
		if (expected == 0 && error > -context->zero_deadband && error < context->zero_deadband) {
			context->state = PID_INACTIVE;
			error = 0;
			context->integral = 0;
			context->last_error = 0;
		} else
			context->state = PID_ACTIVE;
		break;
	case PID_INACTIVE:
		if (expected != 0 || error <= -context->zero_deadband || error >= context->zero_deadband)
			context->state = PID_ACTIVE;
		break;
	default:
		break;
	}
	context->integral += error;
	context->derivative = error - context->last_error;
	context->last_error = error;
    return context->kp * error + context->ki * context->integral + context->kd * context->derivative;
}

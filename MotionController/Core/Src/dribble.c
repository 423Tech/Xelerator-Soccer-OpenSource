/*
 * dribble.c
 *
 *  Created on: Jan 9, 2026
 *      Author: yehui
 */

#include "tim.h"

int dribble_speed_level = 0;

uint16_t speed_tabe[] = {
	0,
	21000,
	42000
};

static void start_all_pwm_channels(void)
{
	HAL_TIM_PWM_Start(&htim9, TIM_CHANNEL_1);
	__HAL_TIM_SET_COMPARE(&htim9, TIM_CHANNEL_1, 0);
}

static void set_pwm(uint16_t pwm)
{
	__HAL_TIM_SET_COMPARE(&htim9, TIM_CHANNEL_1, pwm);
}

void dribble_init(void)
{
	start_all_pwm_channels();
}

void dribble_update_pwm(void)
{
	set_pwm(speed_tabe[dribble_speed_level]);
}

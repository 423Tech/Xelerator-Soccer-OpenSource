/*
 * wheel.c
 *
 *  Created on: Jan 13, 2026
 *      Author: yehui
 */

#include "tim.h"
#include "pid.h"

static struct pid_context pid_context_wheels[4];
float wheel_target_speed_rpm[4] = {0, 0, 0, 0};

static void start_all_pwm_channels(void)
{
	HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_2);
	HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_3);
	HAL_TIM_PWM_Start(&htim4, TIM_CHANNEL_4);
	HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_2);
	HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_3);
	HAL_TIM_PWM_Start(&htim8, TIM_CHANNEL_4);

	__HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_1, 0);
	__HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_2, 0);
	__HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_3, 0);
	__HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_4, 0);
	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_1, 0);
	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_2, 0);
	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_3, 0);
	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_4, 0);
}

static void start_all_encoder_channels(void)
{
	HAL_TIM_Encoder_Start(&htim1, TIM_CHANNEL_ALL);
	HAL_TIM_Encoder_Start(&htim2, TIM_CHANNEL_ALL);
	HAL_TIM_Encoder_Start(&htim3, TIM_CHANNEL_ALL);
	HAL_TIM_Encoder_Start(&htim5, TIM_CHANNEL_ALL);

	__HAL_TIM_SET_COUNTER(&htim1, 0);
	__HAL_TIM_SET_COUNTER(&htim2, 0);
	__HAL_TIM_SET_COUNTER(&htim3, 0);
	__HAL_TIM_SET_COUNTER(&htim5, 0);
}

static void init_pid_context(void)
{
	int i;
	for (i = 0; i < 4; i++) {
		pid_init_context(&pid_context_wheels[i]);
		pid_set_gains(&pid_context_wheels[i], 100, 10, 1);
		pid_set_zero_deadband(&pid_context_wheels[i], 1);
	}
}

static void set_pwm(int32_t (*pwm_array_ptr)[4])
{
	int i;
	static const struct {
		TIM_HandleTypeDef * const phtim;
		const unsigned int forward_channel;
		const unsigned int back_channel;
	} wheel_arr[4] = {
		{&htim8, TIM_CHANNEL_1, TIM_CHANNEL_2},
		{&htim8, TIM_CHANNEL_3, TIM_CHANNEL_4},
		{&htim4, TIM_CHANNEL_1, TIM_CHANNEL_2},
		{&htim4, TIM_CHANNEL_3, TIM_CHANNEL_4}
	};

	for (i = 0; i < 4; i++) {
		int32_t pwm_val = (*pwm_array_ptr)[i];
		__HAL_TIM_SET_COMPARE(
				wheel_arr[i].phtim,
				wheel_arr[i].forward_channel,
				pwm_val >= 0 ? pwm_val : 0);
		__HAL_TIM_SET_COMPARE(
				wheel_arr[i].phtim,
				wheel_arr[i].back_channel,
				pwm_val >= 0 ? 0 : -pwm_val);
	}
}

static void get_encoder_count_delta(int32_t (*delta_array_ptr)[4])
{
	int i;
	static int32_t last_count[4] = {0, 0, 0, 0};
	static TIM_HandleTypeDef * const phtim[4] = {&htim1, &htim2, &htim3, &htim5};

	for (i = 0; i < 4; i++) {
		int32_t current_count = __HAL_TIM_GET_COUNTER(phtim[i]);
		int32_t delta = current_count - last_count[i];

		if (delta > 32767)
			delta -= 65536;
		else if (delta < -32768)
			delta += 65536;

		last_count[i] = current_count;
		(*delta_array_ptr)[i] = delta;
	}
}

static void pid_pwm(int32_t (*target_pwm_array_ptr)[4], int32_t (*delta_array_ptr)[4])
{
	int i;
	for (i = 0; i < 4; i++) {
		(*target_pwm_array_ptr)[i] = (int)pid(&pid_context_wheels[i], wheel_target_speed_rpm[i], (float)(*delta_array_ptr)[i] * (100.0f * 60.0f / 8.0f / 4.0f / 20.0f));
		(*target_pwm_array_ptr)[i] = (*target_pwm_array_ptr)[i] > 42000 ? 42000 : (*target_pwm_array_ptr)[i];
		(*target_pwm_array_ptr)[i] = (*target_pwm_array_ptr)[i] < -42000 ? -42000 : (*target_pwm_array_ptr)[i];
	}
}

void wheel_init(void)
{
	start_all_pwm_channels();
	start_all_encoder_channels();
	init_pid_context();
}

void wheel_update_pwm(void)
{
	int32_t target_pwm[4];
	int32_t encoder_count_delta[4];
	get_encoder_count_delta(&encoder_count_delta);
	pid_pwm(&target_pwm, &encoder_count_delta);
	set_pwm(&target_pwm);
}

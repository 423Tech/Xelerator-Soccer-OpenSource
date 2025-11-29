/*
 * motor.c
 *
 *  Created on: Nov 29, 2025
 *      Author: yehui
 */

#include "main.h"

extern TIM_HandleTypeDef htim1;
extern TIM_HandleTypeDef htim2;
extern TIM_HandleTypeDef htim3;
extern TIM_HandleTypeDef htim4;
extern TIM_HandleTypeDef htim5;
extern TIM_HandleTypeDef htim6;
extern TIM_HandleTypeDef htim8;
extern TIM_HandleTypeDef htim9;

float target_wheel_rpm[4] = {0, 0, 0, 0};

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
	HAL_TIM_PWM_Start(&htim9, TIM_CHANNEL_1);
	HAL_TIM_PWM_Start(&htim9, TIM_CHANNEL_2);

	__HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_1, 0);
	__HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_2, 0);
	__HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_3, 0);
	__HAL_TIM_SET_COMPARE(&htim4, TIM_CHANNEL_4, 0);
	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_1, 0);
	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_2, 0);
	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_3, 0);
	__HAL_TIM_SET_COMPARE(&htim8, TIM_CHANNEL_4, 0);
	__HAL_TIM_SET_COMPARE(&htim9, TIM_CHANNEL_1, 0);
	__HAL_TIM_SET_COMPARE(&htim9, TIM_CHANNEL_2, 0);
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

void init_motor(void)
{
	start_all_pwm_channels();
	start_all_encoder_channels();
	__HAL_TIM_SET_COUNTER(&htim6, 0);
	HAL_TIM_Base_Start_IT(&htim6);
}

static void set_wheels_pwm(int32_t (*pwm_array_ptr)[4])
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

void wheel_pwm_update(void)
{
	int i;
	int32_t count_delta_arr[4];
	int32_t target_pwm[4];
	static struct {
		float last_error;
		float integral;
		float derivative;
	} pid_arr[4] = {
		{0, 0, 0},
		{0, 0, 0},
		{0, 0, 0},
		{0, 0, 0}
	};

	get_encoder_count_delta(&count_delta_arr);

	for (i = 0; i < 4; i++) {
		float error = target_wheel_rpm[i] - (float)count_delta_arr[i] * (100.0f * 60.0f / 8.0f / 4.0f / 20.0f);
		pid_arr[i].integral += error;
		pid_arr[i].derivative = error - pid_arr[i].last_error;
		pid_arr[i].last_error = error;
		pid_arr[i].integral = pid_arr[i].integral > 2000 ? 2000 : pid_arr[i].integral;
		pid_arr[i].integral = pid_arr[i].integral < -2000 ? -2000 : pid_arr[i].integral;
		target_pwm[i] = (float)(12.6 * error + 8.4 * pid_arr[i].integral + 42 * pid_arr[i].derivative);
		target_pwm[i] = target_pwm[i] > 42000 ? 42000 : target_pwm[i];
		target_pwm[i] = target_pwm[i] < -42000 ? -42000 : target_pwm[i];
	}

	set_wheels_pwm(&target_pwm);
}

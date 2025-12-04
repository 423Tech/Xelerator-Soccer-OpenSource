/*
 * bmi088.c
 *
 *  Created on: Nov 29, 2025
 *      Author: yehui
 */

#include "bool.h"
#include "main.h"
#include "delay.h"
#include <string.h>

extern SPI_HandleTypeDef hspi2;

static uint8_t tx_buff[6 + 1];
static uint8_t rx_buff[6 + 1];
static bool calibratint_gyro_zero_bias = false;
static int calibration_samples;
static int samples;
static int32_t sum[3];
static float gyro_zero_bias[3] = {0, 0, 0};
volatile uint32_t bmi088_drdy_timestamp = 0;
volatile float bmi088_gyro_angle[3] = {0, 0, 0};

void bmi088_write_gyro(uint8_t reg, uint8_t data)
{
	tx_buff[0] = reg & 0x7F;
	tx_buff[1] = data;
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_RESET);
	HAL_SPI_Transmit(&hspi2, tx_buff, 2, HAL_MAX_DELAY);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_SET);
	delay_us(2);
}

void bmi088_read_gyro(uint8_t reg, uint8_t *data)
{
	tx_buff[0] = reg | 0x80;
	tx_buff[1] = 0xFF;
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_RESET);
	HAL_SPI_TransmitReceive(&hspi2, tx_buff, rx_buff, 2, HAL_MAX_DELAY);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_SET);
	*data = rx_buff[1];
}

void bmi088_burst_read_gyro(uint8_t reg, int size)
{
	tx_buff[0] = reg | 0x80;
	memset(tx_buff + 1, 0xFF, size);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_RESET);
	HAL_SPI_TransmitReceive_DMA(&hspi2, tx_buff, rx_buff, size + 1);
}

void bmi088_init_gyro(void)
{
	delay_init_dwt();

	delay_us(1000);

	bmi088_write_gyro(0x14, 0xB6);
	delay_us(30000);

	bmi088_write_gyro(0x0F, 0x00);
	bmi088_write_gyro(0x10, 0x02);
	bmi088_write_gyro(0x11, 0x00);
	bmi088_write_gyro(0x15, 0x80);
	bmi088_write_gyro(0x16, 0x00);
	bmi088_write_gyro(0x18, 0x01);
}

void bmi088_process_gyro_angle(void)
{
	int i;
	float time_interval;
	uint32_t current_dwt_cycle = bmi088_drdy_timestamp;
	static uint32_t last_dwt_cycle = 0;
	static float rate[3];
	static float last_rate[3] = {0, 0, 0};

	time_interval = (float)(current_dwt_cycle - last_dwt_cycle) / (float)SystemCoreClock;

	for (i = 0; i < 3; i++) {
		int16_t raw = (int16_t)(rx_buff[2 * i + 2] << 8 | rx_buff[2 * i + 1]);
		if (calibratint_gyro_zero_bias && samples < calibration_samples)
			sum[i] += raw;
		rate[i] = ((float)raw - gyro_zero_bias[i]) * (2000.0f / 32767.0f);
		bmi088_gyro_angle[i] += (last_rate[i] + rate[i]) * time_interval * 0.5f;
		last_rate[i] = rate[i];
	}

	last_dwt_cycle = current_dwt_cycle;

	if (calibratint_gyro_zero_bias && samples < calibration_samples)
		samples++;
	if (calibratint_gyro_zero_bias && samples == calibration_samples) {
		for (i = 0; i < 3; i++) {
			gyro_zero_bias[i] = (float)sum[i] / (float)samples;
			bmi088_gyro_angle[i] = 0;
		}
		calibratint_gyro_zero_bias = false;
	}
}

void bmi088_calibrate_gyro_zero_bias(int calibration_samples_num)
{
	samples = 0;
	memset(sum, 0, sizeof(sum));
	calibration_samples = calibration_samples_num;
	calibratint_gyro_zero_bias = true;
	while (calibratint_gyro_zero_bias);
}

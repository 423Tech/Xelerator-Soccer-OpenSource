/*
 * bmi088.c
 *
 *  Created on: Dec 14, 2025
 *      Author: yehui
 */

#include <stdbool.h>
#include <string.h>
#include "spi.h"
#include "delay.h"

#define TX_RX_BUFF_SIZE (6 + 1)

uint8_t tx_buff[TX_RX_BUFF_SIZE];
uint8_t rx_buff[TX_RX_BUFF_SIZE];

static int gyro_target_samples;
static int gyro_calibrated_samples;
static int32_t gyro_offset_sum[3];
static float gyro_offset[3] = {0, 0, 0};
bool is_calibrating_gyro_offset = false;

volatile uint32_t bmi088_drdy_timestamp = 0;
float bmi088_gyro_angle[3] = {0, 0, 0};

static void bmi088_write_gyro(uint8_t reg, uint8_t data)
{
	tx_buff[0] = reg & 0x7F;
	tx_buff[1] = data;
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_RESET);
	HAL_SPI_Transmit(&hspi2, tx_buff, 2, HAL_MAX_DELAY);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_SET);
	delay_us(2);
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
	delay_init();

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
	static bool is_first_call = true;
	uint32_t current_dwt_cycle = bmi088_drdy_timestamp;
	static uint32_t last_dwt_cycle = 0;
	float rate[3];
	static float last_rate[3] = {0, 0, 0};

	if (is_first_call) {
		for (i = 0; i < 3; i++) {
			int16_t raw = (int16_t)(rx_buff[2 * i + 2] << 8 | rx_buff[2 * i + 1]);
			last_rate[i] = ((float)raw - gyro_offset[i]) * (2000.0f / 32767.0f);
		}
		is_first_call = false;
	} else {
		for (i = 0; i < 3; i++) {
			int16_t raw = (int16_t)(rx_buff[2 * i + 2] << 8 | rx_buff[2 * i + 1]);
			if (is_calibrating_gyro_offset && gyro_calibrated_samples < gyro_target_samples)
				gyro_offset_sum[i] += raw;
			rate[i] = ((float)raw - gyro_offset[i]) * (2000.0f / 32767.0f);
			bmi088_gyro_angle[i] += (last_rate[i] + rate[i]) * (float)(current_dwt_cycle - last_dwt_cycle) / (float)SystemCoreClock * 0.5f;
			last_rate[i] = rate[i];
		}
	}

	last_dwt_cycle = current_dwt_cycle;

	if (is_calibrating_gyro_offset && gyro_calibrated_samples < gyro_target_samples)
		gyro_calibrated_samples++;
	if (is_calibrating_gyro_offset && gyro_calibrated_samples == gyro_target_samples) {
		for (i = 0; i < 3; i++) {
			gyro_offset[i] = (float)gyro_offset_sum[i] / (float)gyro_calibrated_samples;
			bmi088_gyro_angle[i] = 0;
		}
		is_calibrating_gyro_offset = false;
		HAL_GPIO_WritePin(GPIOE, GPIO_PIN_10, GPIO_PIN_RESET);
	}
}

void bmi088_calibrate_gyro_offset(int calibration_samples)
{
	gyro_calibrated_samples = 0;
	memset((void *)gyro_offset_sum, 0, sizeof(gyro_offset_sum));
	gyro_target_samples = calibration_samples;
	is_calibrating_gyro_offset = true;
	HAL_GPIO_WritePin(GPIOE, GPIO_PIN_10, GPIO_PIN_SET);
}

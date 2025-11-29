/*
 * bmi088.c
 *
 *  Created on: Nov 29, 2025
 *      Author: yehui
 */

#include "main.h"
#include "delay.h"
#include <string.h>

extern SPI_HandleTypeDef hspi2;

static uint8_t bmi088_tx_buff[6 + 1];
static uint8_t bmi088_rx_buff[6 + 1];
float gyro_angle[3] = {0, 0, 0};

void write_gyro(uint8_t reg, uint8_t data)
{
	bmi088_tx_buff[0] = reg & 0x7F;
	bmi088_tx_buff[1] = data;
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_RESET);
	HAL_SPI_Transmit(&hspi2, bmi088_tx_buff, 2, HAL_MAX_DELAY);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_SET);
	delay_us(2);
}

void read_gyro(uint8_t reg, uint8_t *data)
{
	bmi088_tx_buff[0] = reg | 0x80;
	bmi088_tx_buff[1] = 0xFF;
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_RESET);
	HAL_SPI_TransmitReceive(&hspi2, bmi088_tx_buff, bmi088_rx_buff, 2, HAL_MAX_DELAY);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_SET);
	*data = bmi088_rx_buff[1];
}

void burst_read_gyro(uint8_t reg, int size)
{
	bmi088_tx_buff[0] = reg | 0x80;
	memset(bmi088_tx_buff + 1, 0xFF, size);
	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_RESET);
	HAL_SPI_TransmitReceive_DMA(&hspi2, bmi088_tx_buff, bmi088_rx_buff, size + 1);
}

void init_gyro(void)
{
	dwt_init();

	delay_us(1000);

	write_gyro(0x14, 0xB6);
	delay_us(30000);

	write_gyro(0x0F, 0x00);
	write_gyro(0x10, 0x02);
	write_gyro(0x11, 0x00);
	write_gyro(0x15, 0x80);
	write_gyro(0x16, 0x00);
	write_gyro(0x18, 0x01);
}

void process_gyro_angle(void)
{
	int i;
	float time_interval;
	uint32_t current_dwt_cycle = DWT->CYCCNT;
	static uint32_t last_dwt_cycle = 0;
	static float rate[3];
	static float last_rate[3] = {0, 0, 0};

	if (last_dwt_cycle == 0) {
		for (i = 0; i < 3; i++)
			last_rate[i] = (int16_t)(bmi088_rx_buff[2 * i + 2] << 8 | bmi088_rx_buff[2 * i + 1]) * (2000.0f / 32767.0f);
		last_dwt_cycle = current_dwt_cycle;
		return;
	}

	time_interval = (float)(current_dwt_cycle - last_dwt_cycle) / (float)SystemCoreClock;

	for (i = 0; i < 3; i++) {
		rate[i] = (int16_t)(bmi088_rx_buff[2 * i + 2] << 8 | bmi088_rx_buff[2 * i + 1]) * (2000.0f / 32767.0f);
		gyro_angle[i] += (last_rate[i] + rate[i]) * time_interval * 0.5f;
		last_rate[i] = rate[i];
	}

	last_dwt_cycle = current_dwt_cycle;
}

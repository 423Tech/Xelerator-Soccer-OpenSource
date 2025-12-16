/*
 * protocol.c
 *
 *  Created on: Dec 14, 2025
 *      Author: yehui
 */

#include <string.h>
#include "usart.h"
#include "bmi088.h"
#include "motor.h"

#define TX_MAX_LEN (32)
#define RX_MAX_LEN (32)

static union {
	uint8_t n[TX_MAX_LEN];
	volatile uint8_t v[TX_MAX_LEN];
} tx_buff;

static union {
	uint8_t n[RX_MAX_LEN];
	volatile uint8_t v[RX_MAX_LEN];
} rx_buff;

void protocol_start_receive_host(void)
{
	HAL_UARTEx_ReceiveToIdle_DMA(&huart4, rx_buff.n, RX_MAX_LEN);
}

void protocol_process_received_frame(void)
{
	tx_buff.n[0] = rx_buff.v[0] | 0x80;
	switch(rx_buff.v[0]) {
	case 0x01:
		HAL_UART_Transmit_IT(&huart4, tx_buff.n, 1 + 0);
		break;
	case 0x02:
		memcpy(tx_buff.n + 1, (void*)bmi088_gyro_angle, sizeof(bmi088_gyro_angle));
		memcpy(tx_buff.n + 1 + sizeof(bmi088_gyro_angle), (void*)(&bmi088_drdy_timestamp), sizeof(bmi088_drdy_timestamp));
		HAL_UART_Transmit_IT(&huart4, tx_buff.n, 1 + sizeof(bmi088_gyro_angle) + sizeof(bmi088_drdy_timestamp));
		break;
	case 0x03:
		memcpy((void*)motor_target_wheels_rpm, rx_buff.n + 1, sizeof(motor_target_wheels_rpm));
		break;
	default:
		break;
	}
	
	HAL_UARTEx_ReceiveToIdle_DMA(&huart4, rx_buff.n, RX_MAX_LEN);
}

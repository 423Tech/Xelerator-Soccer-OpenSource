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

#define TX_MAX_LEN 32
#define RX_MAX_LEN 32

static uint8_t tx_buff[TX_MAX_LEN];
static uint8_t rx_buff[RX_MAX_LEN];

void protocol_start_receive_host(void)
{
	HAL_UARTEx_ReceiveToIdle_DMA(&huart4, rx_buff, RX_MAX_LEN);
}

void protocol_process_received_frame(void)
{
	volatile uint8_t *v_rx = (volatile uint8_t *)rx_buff;
	tx_buff[0] = v_rx[0] | 0x80;
	switch(v_rx[0]) {
	case 0x01:
		HAL_UART_Transmit_IT(&huart4, tx_buff, 1 + 0);
		break;
	case 0x02:
		memcpy(tx_buff + 1, bmi088_gyro_angle, sizeof(bmi088_gyro_angle));
		memcpy(tx_buff + 1 + sizeof(bmi088_gyro_angle), &bmi088_drdy_timestamp, sizeof(bmi088_drdy_timestamp));
		HAL_UART_Transmit_IT(&huart4, tx_buff, 1 + sizeof(bmi088_gyro_angle) + sizeof(bmi088_drdy_timestamp));
		break;
	case 0x03:
		memcpy(motor_target_wheels_rpm, rx_buff + 1, sizeof(motor_target_wheels_rpm));
		HAL_UART_Transmit_IT(&huart4, tx_buff, 1 + 0);
		break;
	default:
		break;
	}
	
	HAL_UARTEx_ReceiveToIdle_DMA(&huart4, rx_buff, RX_MAX_LEN);
}

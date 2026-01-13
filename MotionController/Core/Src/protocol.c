/*
 * protocol.c
 *
 *  Created on: Dec 14, 2025
 *      Author: yehui
 */

#include <stdbool.h>
#include <string.h>
#include "usart.h"
#include "bmi088.h"
#include "wheel.h"
#include "kick.h"

#define TX_MAX_LEN (32)
#define RX_MAX_LEN (32)

static uint8_t tx_buff[TX_MAX_LEN];
static uint8_t rx_buff[2][RX_MAX_LEN];
static int current_rx_buff_idx = 0;

void protocol_start_receive_host(void)
{
	current_rx_buff_idx ^= 1;
	HAL_UARTEx_ReceiveToIdle_DMA(&huart4, rx_buff[current_rx_buff_idx], RX_MAX_LEN);
}

static void process_handshake(uint8_t *tx, uint8_t *rx, uint8_t **end_tx, uint8_t **end_rx)
{
	(void)rx;
	tx[1] = is_calibrating_gyro_offset ? 0x01 : 0x00;
	*end_tx += 1 + sizeof(uint8_t);
	*end_rx += 1;
}

static void process_get_bmi088_data(uint8_t *tx, uint8_t *rx, uint8_t **end_tx, uint8_t **end_rx)
{
	(void)rx;
	memcpy(tx + 1, bmi088_gyro_angle, sizeof(bmi088_gyro_angle));
	memcpy(tx + 1 + sizeof(bmi088_gyro_angle), (void *)(&bmi088_drdy_timestamp), sizeof(bmi088_drdy_timestamp));
	*end_tx += 1 + sizeof(bmi088_gyro_angle) + sizeof(bmi088_drdy_timestamp);
	*end_rx += 1;
}

static void process_set_wheels_speed(uint8_t *tx, uint8_t *rx, uint8_t **end_tx, uint8_t **end_rx)
{
	(void)tx;
	memcpy(wheel_target_speed_rpm, rx + 1, sizeof(wheel_target_speed_rpm));
	*end_tx += 1;
	*end_rx += 1 + sizeof(wheel_target_speed_rpm);
}

static void process_kick(uint8_t *tx, uint8_t *rx, uint8_t **end_tx, uint8_t **end_rx)
{
	(void)tx;
	(void)rx;
	kick();
	*end_tx += 1;
	*end_rx += 1;
}

void protocol_process_received_frame(void)
{
	uint8_t *tx_buff_ptr = tx_buff;
	uint8_t *rx_buff_ptr = rx_buff[current_rx_buff_idx];
	bool is_processing_composite_cmd = false;
	do {
		tx_buff_ptr[0] = rx_buff_ptr[0] | 0x80;
		switch(rx_buff_ptr[0]) {
		case 0x00:
			is_processing_composite_cmd ^= true;
			tx_buff_ptr++;
			rx_buff_ptr++;
			break;
		case 0x01:
			process_handshake(tx_buff_ptr, rx_buff_ptr, &tx_buff_ptr, &rx_buff_ptr);
			break;
		case 0x02:
			process_get_bmi088_data(tx_buff_ptr, rx_buff_ptr, &tx_buff_ptr, &rx_buff_ptr);
			break;
		case 0x03:
			process_set_wheels_speed(tx_buff_ptr, rx_buff_ptr, &tx_buff_ptr, &rx_buff_ptr);
			break;
		case 0x04:
			process_kick(tx_buff_ptr, rx_buff_ptr, &tx_buff_ptr, &rx_buff_ptr);
			break;
		default:
			break;
		}
	} while (is_processing_composite_cmd);
	HAL_UART_Transmit_IT(&huart4, tx_buff, tx_buff_ptr - tx_buff);
	protocol_start_receive_host();
}

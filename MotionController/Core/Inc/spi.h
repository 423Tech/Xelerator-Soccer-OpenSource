/*
 * spi.h
 *
 *  Created on: Dec 6, 2025
 *      Author: yehui
 */

#ifndef INC_SPI_H_
#define INC_SPI_H_

#include "main.h"

struct spi_device {
	SPI_HandleTypeDef * const phspi;
	GPIO_TypeDef * const cs_gpio_port;
	const uint16_t cs_gpio_pin;
};

HAL_StatusTypeDef spi_transmit(const struct spi_device *device, const uint8_t *pdata, uint16_t size, uint32_t timeout);
HAL_StatusTypeDef spi_transmit_receive(const struct spi_device *device, const uint8_t *ptxdata, uint8_t *prxdata, uint16_t size, uint32_t timeout);

#endif /* INC_SPI_H_ */

/*
 * spi.c
 *
 *  Created on: Dec 6, 2025
 *      Author: yehui
 */

#include "main.h"
#include "spi.h"

HAL_StatusTypeDef spi_transmit(const struct spi_device *device, const uint8_t *pdata, uint16_t size, uint32_t timeout)
{
	HAL_StatusTypeDef result;
	HAL_GPIO_WritePin(device->cs_gpio_port, device->cs_gpio_pin, GPIO_PIN_RESET);
	result = HAL_SPI_Transmit(device->phspi, pdata, size, timeout);
	HAL_GPIO_WritePin(device->cs_gpio_port, device->cs_gpio_pin, GPIO_PIN_SET);
	return result;
}

HAL_StatusTypeDef spi_transmit_receive(const struct spi_device *device, const uint8_t *ptxdata, uint8_t *prxdata, uint16_t size, uint32_t timeout)
{
	HAL_StatusTypeDef result;
	HAL_GPIO_WritePin(device->cs_gpio_port, device->cs_gpio_pin, GPIO_PIN_RESET);
	result = HAL_SPI_TransmitReceive(device->phspi, ptxdata, prxdata, size, timeout);
	HAL_GPIO_WritePin(device->cs_gpio_port, device->cs_gpio_pin, GPIO_PIN_SET);
	return result;
}
/*
void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi)
{
	switch((uint32_t)hspi->Instance) {
	case (uint32_t)SPI2:
		break;
	default:
		break;
	}
}
*/

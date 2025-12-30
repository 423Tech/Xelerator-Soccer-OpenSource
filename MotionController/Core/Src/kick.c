/*
 * kick.c
 *
 *  Created on: Dec 30, 2025
 *      Author: yehui
 */

#include "gpio.h"

void kick_init(void)
{
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);
}

void kick(void)
{
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
    kick_init();
}

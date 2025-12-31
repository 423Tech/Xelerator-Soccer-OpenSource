/*
 * kick.c
 *
 *  Created on: Dec 30, 2025
 *      Author: yehui
 */

#include "gpio.h"
#include "delay.h"
#include "kick.h"

void kick_reset(void)
{
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_SET);
}

void kick(void)
{
    HAL_GPIO_WritePin(GPIOB, GPIO_PIN_0, GPIO_PIN_RESET);
    delay_task_enqueue(100, DELAY_TASK_KICK_RESET);
}

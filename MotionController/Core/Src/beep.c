/*
 * beep.c
 *
 *  Created on: Jan 1, 2026
 *      Author: yehui
 */

#include "main.h"
#include "delay.h"
#include "beep.h"

void beep(int ms)
{
    HAL_GPIO_WritePin(GPIOE, GPIO_PIN_4, GPIO_PIN_SET);
    delay_task_enqueue(DELAY_TASK_BEEP_RESET, ms);
}

void beep_reset(void)
{
    HAL_GPIO_WritePin(GPIOE, GPIO_PIN_4, GPIO_PIN_RESET);
}

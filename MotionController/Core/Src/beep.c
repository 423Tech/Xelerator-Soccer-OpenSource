/*
 * beep.c
 *
 *  Created on: Jan 1, 2026
 *      Author: yehui
 */

#include <stddef.h>
#include <stdbool.h>
#include "main.h"
#include "delay.h"
#include "delay_task_code.h"
#include "beep.h"

static int beep_cycles_count;
static bool continue_beep = false;
static int continue_beep_ms;
static int continue_interval_ms;
static int continue_cycles;

void beep(int ms)
{
    HAL_GPIO_WritePin(GPIOE, GPIO_PIN_4, GPIO_PIN_SET);
    delay_task_enqueue(DELAY_TASK_BEEP_RESET, ms, NULL);
}

void beep_reset(void)
{
    HAL_GPIO_WritePin(GPIOE, GPIO_PIN_4, GPIO_PIN_RESET);
    if (continue_beep)
        delay_task_enqueue(DELAY_TASK_BEEP_CONTINUE, continue_interval_ms, NULL);
}

void beep_continue(void)
{
    beep(continue_beep_ms);
    beep_cycles_count++;
    if (continue_cycles != BEEP_CYCLES_INFINITE && beep_cycles_count >= continue_cycles)
        continue_beep = false;
}

void beep_cycle(int beep_ms, int interval_ms, int cycles)
{
    continue_beep_ms = beep_ms;
    continue_interval_ms = interval_ms;
    continue_cycles = cycles;
    beep_cycles_count = 0;
    continue_beep = true;
    beep_continue();
}

void beep_stop_cycle(void) {
    continue_beep = false;
}

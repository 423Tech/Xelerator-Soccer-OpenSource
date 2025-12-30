/*
 * delay.c
 *
 *  Created on: Dec 14, 2025
 *      Author: yehui
 */

#include <stdbool.h>
#include "main.h"

#define DELAY_TASK_QUEUE_SIZE (8)

struct delay_task {
	int idx;
	uint32_t call_time;
	void (*call)(void *);
	void *arr;
};

static volatile int read_idx = 0, write_idx = 0;
static volatile struct delay_task delay_task_queue[DELAY_TASK_QUEUE_SIZE];

void delay_init_dwt(void)
{
	static bool dwt_is_initialized = false;
	if (!dwt_is_initialized) {
		CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
		DWT->CYCCNT = 0;
		DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
		dwt_is_initialized = true;
	}
}

void delay_us(uint32_t us)
{
    uint32_t start = DWT->CYCCNT;
    uint32_t cycles = us * (SystemCoreClock / 1000000);

    while (DWT->CYCCNT - start < cycles);
}

void delay_call_after_ms(uint32_t ms, void (*call)(void *), void *arr)
{

}

void delay_call_delay_task(void)
{

}

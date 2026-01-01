/*
 * delay.c
 *
 *  Created on: Dec 14, 2025
 *      Author: yehui
 */

#include <stdbool.h>
#include <stdlib.h>
#include <string.h>
#include "main.h"

#define DELAY_TASK_QUEUE_SIZE (8)

struct delay_task {
	uint32_t start;
	uint32_t delay;
	int code;
	bool active;
};

static volatile struct delay_task delay_task_queue[DELAY_TASK_QUEUE_SIZE];
volatile uint32_t sys_tick_count = 0;

static int compare_delay_task(const void *a, const void *b)
{
	const struct delay_task *ta = a, *tb = b;
	if (ta->active && tb->active) {
		int32_t diff = (int32_t)((ta->start - tb->start) + (ta->delay - tb->delay));
		return (diff > 0) - (diff < 0);
	}
	else
		return tb->active - ta->active;
}

static void delay_init_task_queue(void)
{
	int i;
	for (i = 0; i < DELAY_TASK_QUEUE_SIZE; i++) {
		delay_task_queue[i].start = 0;
		delay_task_queue[i].delay = 0;
		delay_task_queue[i].code = 0;
		delay_task_queue[i].active = false;
	}
}

void delay_init(void)
{
	static bool dwt_is_initialized = false;
	if (!dwt_is_initialized) {
		CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
		DWT->CYCCNT = 0;
		DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
		dwt_is_initialized = true;
	}
	delay_init_task_queue();
}

void delay_us(uint32_t us)
{
    uint32_t start = DWT->CYCCNT;
    uint32_t cycles = us * (SystemCoreClock / 1000000);

    while (DWT->CYCCNT - start < cycles);
}

void delay_task_enqueue(int delay_task_code, int32_t delay_ms)
{
	uint32_t primask = __get_PRIMASK();
	__disable_irq();
	delay_task_queue[DELAY_TASK_QUEUE_SIZE - 1].active = true;
	delay_task_queue[DELAY_TASK_QUEUE_SIZE - 1].start = sys_tick_count;
	delay_task_queue[DELAY_TASK_QUEUE_SIZE - 1].delay = delay_ms;
	delay_task_queue[DELAY_TASK_QUEUE_SIZE - 1].code = delay_task_code;
	qsort((void *)delay_task_queue, DELAY_TASK_QUEUE_SIZE, sizeof(delay_task_queue[0]), compare_delay_task);
	__set_PRIMASK(primask);
}

bool delay_task_available(void)
{
	return delay_task_queue[0].active && sys_tick_count - delay_task_queue[0].start >= delay_task_queue[0].delay;
}

int delay_task_consume(void)
{
	int result = delay_task_queue[0].code;
	delay_task_queue[0].active = false;
	qsort((void *)delay_task_queue, DELAY_TASK_QUEUE_SIZE, sizeof(delay_task_queue[0]), compare_delay_task);
	return result;
}

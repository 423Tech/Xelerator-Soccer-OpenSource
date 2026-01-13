/*
 * task.c
 *
 *  Created on: Dec 30, 2025
 *      Author: yehui
 */

#include <stdbool.h>
#include "main.h"

#define TASK_QUEUE_SIZE (8)

struct task_type {
	int code;
	void *arg;
};

static volatile int read_idx = 0, write_idx = 0;
static volatile struct task_type task_queue[TASK_QUEUE_SIZE];

void task_enqueue(int task_code, void *arg)
{
	uint32_t primask = __get_PRIMASK();
	__disable_irq();
	task_queue[write_idx].code = task_code;
	task_queue[write_idx].arg = arg;
	write_idx = (write_idx + 1) % TASK_QUEUE_SIZE;
	__set_PRIMASK(primask);
}

bool task_available(void)
{
	return read_idx != write_idx;
}

int task_consume(void **get_arg)
{
	int result = task_queue[read_idx].code;
	*get_arg = task_queue[read_idx].arg;
	read_idx = (read_idx + 1) % TASK_QUEUE_SIZE;
	return result;
}

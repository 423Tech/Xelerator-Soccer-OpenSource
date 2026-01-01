/*
 * delay.h
 *
 *  Created on: Dec 14, 2025
 *      Author: yehui
 */

#ifndef INC_DELAY_H_
#define INC_DELAY_H_

#include <stdbool.h>

extern volatile uint32_t sys_tick_count;

void delay_init(void);
void delay_us(uint32_t us);
void delay_task_enqueue(int delay_task_code, uint16_t delay_ms);
bool delay_task_available(void);
int delay_task_consume(void);

#endif /* INC_DELAY_H_ */

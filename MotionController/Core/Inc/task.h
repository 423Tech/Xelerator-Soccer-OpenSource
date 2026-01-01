/*
 * task.h
 *
 *  Created on: Dec 30, 2025
 *      Author: yehui
 */

#ifndef INC_TASK_H_
#define INC_TASK_H_

#include <stdbool.h>

void task_enqueue(int task_code);
bool task_available(void);
int task_consume(void);

#endif /* INC_TASK_H_ */

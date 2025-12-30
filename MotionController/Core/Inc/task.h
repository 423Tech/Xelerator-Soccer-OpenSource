/*
 * task.h
 *
 *  Created on: Dec 30, 2025
 *      Author: yehui
 */

#ifndef INC_TASK_H_
#define INC_TASK_H_

/*
struct task_queue_type {
    volatile int read_idx;
    volatile int write_idx;
    volatile void *queue;
    int size;
};
*/

void task_enqueue(int task_code, void *arr);
bool task_available(void);
int task_consume(void);

#endif /* INC_TASK_H_ */

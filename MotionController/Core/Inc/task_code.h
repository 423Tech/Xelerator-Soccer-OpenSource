/*
 * task_code.h
 *
 *  Created on: Jan 1, 2026
 *      Author: yehui
 */

#ifndef INC_TASK_CODE_H_
#define INC_TASK_CODE_H_

enum task_code {
	TASK_NONE,
	TASK_UPDATE_PWM,
	TASK_PROCESS_GYRO_ANGLE,
	TASK_PROCESS_RECEIVED_FRAME, 
	TASK_PROCESS_DELAY_TASK
};

#endif /* INC_TASK_CODE_H_ */

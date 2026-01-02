/*
 * delay_task_code.h
 *
 *  Created on: Jan 1, 2026
 *      Author: yehui
 */

#ifndef INC_DELAY_TASK_CODE_H_
#define INC_DELAY_TASK_CODE_H_

enum delay_task_code {
    DELAY_TASK_NONE, 
    DELAY_TASK_BMI088_CALIBRATE_OFFSET, 
    DELAY_TASK_KICK_RESET, 
    DELAY_TASK_BEEP_RESET, 
    DELAY_TASK_BEEP_CONTINUE, 
    DELAY_TASK_BATTERY_VOLTAGE_MONITORING
};

#endif /* INC_DELAY_TASK_CODE_H_ */

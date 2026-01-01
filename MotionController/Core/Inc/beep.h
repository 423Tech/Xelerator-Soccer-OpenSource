/*
 * beep.h
 *
 *  Created on: Jan 1, 2026
 *      Author: yehui
 */

#ifndef INC_BEEP_H_
#define INC_BEEP_H_

#define BEEP_CYCLES_INFINITE (-1)

void beep(int ms);
void beep_reset(void);
void beep_continue(void);
void beep_cycle(int beep_ms, int interval_ms, int cycles);
void beep_stop_cycle(void);

#endif /* INC_BEEP_H_ */

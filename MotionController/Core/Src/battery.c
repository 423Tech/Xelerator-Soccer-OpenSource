/*
 * battery.c
 *
 *  Created on: Jan 1, 2026
 *      Author: yehui
 */

#include <stddef.h>
#include <stdbool.h>
#include "main.h"
#include "adc.h"
#include "beep.h"
#include "voltage.h"

#define BATTERY_NOMINAL_VOLTAGE_V (11.1f)
#define BATTERY_VOLTAGE_LOW_THRESHOLD_V (10.5f)
#define VOLTAGE_DIVIDER_RATIO ((100.0f + 10.0f) / 10.0f)

static float get_battery_voltage(int sample_count)
{
	float raw = voltage_get_v(&hadc1, sample_count);
	return raw * VOLTAGE_DIVIDER_RATIO;
}

void battery_monit_voltage(void)
{
	int i;
	static bool alarm = false;
	bool alarm_last_state = alarm;
	static float recent_voltage[] = {
		BATTERY_NOMINAL_VOLTAGE_V, 
		BATTERY_NOMINAL_VOLTAGE_V, 
		BATTERY_NOMINAL_VOLTAGE_V, 
		BATTERY_NOMINAL_VOLTAGE_V, 
		BATTERY_NOMINAL_VOLTAGE_V
	};
	static int voltage_ptr = 0;
	static const int  recent_voltage_size = (sizeof(recent_voltage) / sizeof(recent_voltage[0]));
	recent_voltage[voltage_ptr] = get_battery_voltage(10);
	voltage_ptr = (voltage_ptr + 1) % recent_voltage_size;
	if (alarm) {
		alarm = false;
		for(i = 0; i < recent_voltage_size; i++) {
			if (recent_voltage[i] < BATTERY_VOLTAGE_LOW_THRESHOLD_V) {
				alarm = true;
				break;
			}
		}
	} else {
		alarm = true;
		for (i = 0; i < recent_voltage_size; i++) {
			if (recent_voltage[i] >= BATTERY_VOLTAGE_LOW_THRESHOLD_V) {
				alarm = false;
				break;
			}
		}
	}
	if (alarm ^ alarm_last_state) {
		if (alarm)
			beep_cycle(100, 100, BEEP_CYCLES_INFINITE);
		else
			beep_stop_cycle();
	}
}

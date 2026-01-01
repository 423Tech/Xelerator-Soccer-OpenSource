/*
 * battery.c
 *
 *  Created on: Jan 1, 2026
 *      Author: yehui
 */

#include <stdbool.h>
#include "main.h"
#include "adc.h"
#include "delay.h"
#include "beep.h"
#include "battery.h"

#define BATTERY_VOLTAGE_LOW_THRESHOLD (10.0f)
#define ADC_VREF (3.3f)
#define ADC_RESOLUTIOON (4095.0f)
#define VOLTAGE_DIVIDER_RATIO ((100.0f + 10.0f) / 10.0f)

float get_battery_voltage(void)
{
	HAL_ADC_Start(&hadc1);
	HAL_ADC_PollForConversion(&hadc1, 1);
	HAL_ADC_Stop(&hadc1);
	return (float)HAL_ADC_GetValue(&hadc1) * (ADC_VREF / ADC_RESOLUTIOON) * VOLTAGE_DIVIDER_RATIO;
}

void start_battery_voltage_monitoring(void)
{
	int i;
	bool alarm = false;
	static bool last_alarm_state = false;
	static float recent_voltage[10] = {12.0f, 12.0f, 12.0f, 12.0f, 12.0f, 12.0f, 12.0f, 12.0f, 12.0f, 12.0f};
	static int voltage_ptr = 0;
	static const int  recent_voltage_size = (sizeof(recent_voltage) / sizeof(recent_voltage[0]));
	recent_voltage[voltage_ptr] = get_battery_voltage();
	voltage_ptr = (voltage_ptr + 1) % recent_voltage_size;
	if (alarm) {
		alarm = false;
		for(i = 0; i < recent_voltage_size; i++) {
			if (recent_voltage[i] < BATTERY_VOLTAGE_LOW_THRESHOLD)
				alarm = true;
		}
	} else {
		alarm = true;
		for (i = 0; i < recent_voltage_size; i++) {
			if (recent_voltage[i] >= BATTERY_VOLTAGE_LOW_THRESHOLD)
				alarm = false;
		}
	}
	if (alarm ^ last_alarm_state) {
		if (alarm)
			beep_cycle(100, 100, BEEP_CYCLES_INFINITE);
		else
			beep_stop_cycle();
	}
	last_alarm_state = alarm;
}

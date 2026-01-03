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
#include "delay.h"
#include "delay_task_code.h"
#include "beep.h"

#define BATTERY_VOLTAGE_LOW_THRESHOLD (10.5f)
#define ADC_VREF (3.3f)
#define ADC_RESOLUTIOON (4095.0f)
#define VOLTAGE_DIVIDER_RATIO ((100.0f + 10.0f) / 10.0f)

static float get_battery_voltage(void)
{
	HAL_ADC_Start(&hadc1);
	HAL_ADC_PollForConversion(&hadc1, 1);
	HAL_ADC_Stop(&hadc1);
	return (float)HAL_ADC_GetValue(&hadc1) * (ADC_VREF / ADC_RESOLUTIOON) * VOLTAGE_DIVIDER_RATIO;
}

static float get_average_battery_voltage(int samples)
{
	int i;
	float sum = 0;
	for (i = 0; i < samples; i++)
		sum += get_battery_voltage();
	return sum / samples;
}

void start_battery_voltage_monitoring(void)
{
	int i;
	bool alarm = false;
	static bool alarm_last_state = false;
	static float recent_voltage[3] = {12.0f, 12.0f, 12.0f};
	static int voltage_ptr = 0;
	static const int  recent_voltage_size = (sizeof(recent_voltage) / sizeof(recent_voltage[0]));
	recent_voltage[voltage_ptr] = get_average_battery_voltage(10);
	voltage_ptr = (voltage_ptr + 1) % recent_voltage_size;
	if (alarm) {
		alarm = false;
		for(i = 0; i < recent_voltage_size; i++) {
			if (recent_voltage[i] < BATTERY_VOLTAGE_LOW_THRESHOLD) {
				alarm = true;
				break;
			}
		}
	} else {
		alarm = true;
		for (i = 0; i < recent_voltage_size; i++) {
			if (recent_voltage[i] >= BATTERY_VOLTAGE_LOW_THRESHOLD) {
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
		alarm_last_state = alarm;
	}
	delay_task_enqueue(DELAY_TASK_BATTERY_VOLTAGE_MONITORING, 1000, NULL);
}

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
    return (float)HAL_ADC_GetValue(&hadc1) * (ADC_VREF / ADC_RESOLUTIOON) * VOLTAGE_DIVIDER_RATIO;
}

void start_battery_voltage_monitoring(void)
{

}

/*
 * voltage.c
 *
 *  Created on: Jan 13, 2026
 *      Author: yehui
 */

#include "adc.h"

#define ADC_VREF_V (3.3f)
#define ADC_RESOLUTION (4095.0f)

float voltage_get_v(ADC_HandleTypeDef *hadc, int sample_count)
{
	int i;
	uint32_t sum = 0;
	HAL_ADC_Start(hadc);
	for (i = 0; i < sample_count; i++) {
		HAL_ADC_Start(hadc);
        HAL_ADC_PollForConversion(hadc, 1);
        sum += HAL_ADC_GetValue(hadc);
	}
	HAL_ADC_Stop(hadc);
	return (float)sum / (float)sample_count * (ADC_VREF_V / ADC_RESOLUTION);
}

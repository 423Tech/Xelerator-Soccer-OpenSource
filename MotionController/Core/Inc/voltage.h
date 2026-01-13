/*
 * voltage.h
 *
 *  Created on: Jan 13, 2026
 *      Author: yehui
 */

#ifndef INC_VOLTAGE_H_
#define INC_VOLTAGE_H_

#include "adc.h"

float voltage_get_v(ADC_HandleTypeDef *hadc, int sample_count);

#endif /* INC_VOLTAGE_H_ */

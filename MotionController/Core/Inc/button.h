/*
 * button.h
 *
 *  Created on: Jan 3, 2026
 *      Author: yehui
 */

#ifndef INC_BUTTON_H_
#define INC_BUTTON_H_

#include "main.h"

enum button_event {
    BUTTON_EVENT_NONE, 
    BUTTON_EVENT_RISING_EDGE, 
    BUTTON_EVENT_FALLING_EDGE, 
    BUTTON_EVENT_DEBOUNCING
};

enum button_event button_get_event(GPIO_TypeDef *gpiox, uint16_t gpio_pin);
void button_debounce_end(uint16_t gpio_pin);

#endif /* INC_BUTTON_H_ */

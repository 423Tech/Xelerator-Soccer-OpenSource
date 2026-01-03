/*
 * button.c
 *
 *  Created on: Jan 3, 2026
 *      Author: yehui
 */

#include "main.h"
#include "button.h"
#include "delay.h"
#include "delay_task_code.h"

#define DEBOUNCE_TIME_MS (50)

static uint16_t is_debouncing = 0x00;

enum button_event button_get_event(GPIO_TypeDef *gpiox, uint16_t gpio_pin)
{
    if ((gpio_pin ^ is_debouncing) & gpio_pin) {
        GPIO_PinState pin_state = HAL_GPIO_ReadPin(gpiox, gpio_pin);
        is_debouncing |= gpio_pin;
        delay_task_enqueue(DELAY_TASK_BUTTON_DEBOUNCE_END, DEBOUNCE_TIME_MS, (void*)(uintptr_t)gpio_pin);
        if (pin_state == GPIO_PIN_RESET)
            return BUTTON_EVENT_FALLING_EDGE;
        else
            return BUTTON_EVENT_RISING_EDGE;
    }
    return BUTTON_EVENT_DEBOUNCING;
}

void button_debounce_end(uint16_t gpio_pin)
{
    is_debouncing &= ~gpio_pin;
}

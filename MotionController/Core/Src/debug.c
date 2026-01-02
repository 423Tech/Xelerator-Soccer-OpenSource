/*
 * debug.c
 *
 *  Created on: Jan 2, 2026
 *      Author: yehui
 */

#include <stdarg.h>
#include "stdio.h"
#include "string.h"
#include "main.h"
#include "usart.h"

#define DEBUG_BUFFER_SIZE (64)

int debug_printf(const char *format, ...)
{
    char buffer[DEBUG_BUFFER_SIZE];
    va_list args;
    int len;

    va_start(args, format);
    len = vsnprintf(buffer, DEBUG_BUFFER_SIZE, format, args);
    if (len >= DEBUG_BUFFER_SIZE) {
        len = DEBUG_BUFFER_SIZE - 1;
        buffer[len] = '\0';
    }
    va_end(args);

    HAL_UART_Transmit(&huart4, (uint8_t *)buffer, len, HAL_MAX_DELAY);

    return len;
}

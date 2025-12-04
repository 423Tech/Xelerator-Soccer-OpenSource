/*
 * delay.c
 *
 *  Created on: Nov 29, 2025
 *      Author: yehui
 */

#include "bool.h"
#include "main.h"

void delay_init_dwt(void)
{
	static bool dwt_is_initialized = false;
	if (!dwt_is_initialized) {
		CoreDebug->DEMCR |= CoreDebug_DEMCR_TRCENA_Msk;
		DWT->CYCCNT = 0;
		DWT->CTRL |= DWT_CTRL_CYCCNTENA_Msk;
		dwt_is_initialized = true;
	}
}

void delay_us(uint32_t us)
{
    uint32_t start = DWT->CYCCNT;
    uint32_t cycles = us * (SystemCoreClock / 1000000);

    while (DWT->CYCCNT - start < cycles);
}

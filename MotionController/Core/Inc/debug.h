/*
 * debug.h
 *
 *  Created on: Jan 2, 2026
 *      Author: yehui
 */

#ifndef INC_DEBUG_H_
#define INC_DEBUG_H_

#define DEBUG_ENABLE (1)

#if DEBUG_ENABLE
    int debug_printf(const char *format, ...);
    #define DEBUG_PRINTF(...) debug_printf(__VA_ARGS__)
#else
    #define DEBUG_PRINTF(...)
#endif

#endif /* INC_DEBUG_H_ */

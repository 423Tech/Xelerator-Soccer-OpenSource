#ifndef __USART_H__
#define __USART_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "led.h"
#include <stdio.h>

#define UART4_DMA_RX_BUFFER_MAX_LENGTH        (40)
#define UART4_DMA_TX_BUFFER_MAX_LENGTH        (100)
#define	UART4_RX_MAX 		UART4_DMA_RX_BUFFER_MAX_LENGTH		//串口接收缓冲区


void UART4_Start_Receive(void);					// 启动UART4接收（包含空闲中断使能）
void UART4_Configuration(u32 bound);			//串口4 DMA 初始化
void UART4_Send_str( uint8_t *pData);
void UART4_RX_Buff_CLR(void);       //清除串口接收缓存数据

void UART4_DMA_Tx_Configuration(void);			//配置 UART4 DMA TX
void UART4_DMA_Rx_Configuration(void);			//配置 UART4 DMA RX
void UART4_DMA_Begin_Send(uint8_t *send_buffer , uint16_t nSendBytes);	//通过 串口 DMA 发送数据
void UART4_DMA_RX_Buff_CLR(void);            	//清除 DMA 串口接收缓存数据

void UART4_Send_str( uint8_t *pData);

#endif 



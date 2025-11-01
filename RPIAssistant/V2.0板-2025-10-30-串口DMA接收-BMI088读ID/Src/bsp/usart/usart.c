#include "system.h"
#include "usart.h"
#include "string.h"
#include "led.h"
#include "car_RTU.h"
uint8_t UART4_DMA_RX_Buffer[UART4_DMA_RX_BUFFER_MAX_LENGTH];		//串口 DMA 接收 数组
uint8_t UART4_DMA_TX_Buffer[UART4_DMA_TX_BUFFER_MAX_LENGTH];		//串口 DMA 发送 数组

UART_HandleTypeDef husart_UART4;
DMA_HandleTypeDef hdma_uart4_rx;
void HAL_UART_MspInit(UART_HandleTypeDef* huart)
{
  GPIO_InitTypeDef GPIO_InitStruct;

  if(huart->Instance==UART4)
  {
    /* 串口外设时钟使能 */
    __HAL_RCC_UART4_CLK_ENABLE();
   // 使能DMA时钟
	__HAL_RCC_DMA1_CLK_ENABLE();
    /* 串口外设功能GPIO配置 */
    GPIO_InitStruct.Pin = GPIO_PIN_10;
    GPIO_InitStruct.Mode = GPIO_MODE_AF_PP;
    GPIO_InitStruct.Pull = GPIO_PULLUP;
    GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_VERY_HIGH;
    GPIO_InitStruct.Alternate = GPIO_AF8_UART4;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
    
    GPIO_InitStruct.Pin = GPIO_PIN_11;  
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);  

	// 配置DMA接收中断
	HAL_NVIC_SetPriority(DMA1_Stream2_IRQn, 0, 1);
	HAL_NVIC_EnableIRQ(DMA1_Stream2_IRQn);
	  
	HAL_NVIC_SetPriority(UART4_IRQn, 0, 3);
	HAL_NVIC_EnableIRQ(UART4_IRQn);
  }  
}

void HAL_UART_MspDeInit(UART_HandleTypeDef* huart)
{
  if(huart->Instance==UART4)
  {
    __HAL_RCC_UART4_CLK_DISABLE();
    HAL_GPIO_DeInit(GPIOC, GPIO_PIN_10|GPIO_PIN_11);
    HAL_NVIC_DisableIRQ(UART4_IRQn);
  }
}

//************************  串口4 初始化 ************************
void UART4_Configuration(u32 bound)
{
	/* 使能串口功能引脚GPIO时钟 */
	__HAL_RCC_GPIOC_CLK_ENABLE();

	husart_UART4.Instance = UART4;
	husart_UART4.Init.BaudRate = bound;
	husart_UART4.Init.WordLength = UART_WORDLENGTH_8B;
	husart_UART4.Init.StopBits = UART_STOPBITS_1;
	husart_UART4.Init.Parity = UART_PARITY_NONE;
	husart_UART4.Init.Mode = UART_MODE_TX_RX;
	husart_UART4.Init.HwFlowCtl = UART_HWCONTROL_NONE;
	husart_UART4.Init.OverSampling = UART_OVERSAMPLING_16;
	HAL_UART_Init(&husart_UART4);

//	__HAL_UART_ENABLE_IT(&husart_UART4,UART_IT_RXNE);	  /* 使能接收中断 */	
	
    // 启动UART4 DMA接收（包含空闲中断）
    UART4_Start_Receive();
}
// 启动UART4接收（包含空闲中断使能）
void UART4_Start_Receive(void)
{
    // 先启动DMA接收
    HAL_UART_Receive_DMA(&husart_UART4, UART4_DMA_RX_Buffer, UART4_DMA_RX_BUFFER_MAX_LENGTH);
    // 使能空闲中断
    __HAL_UART_ENABLE_IT(&husart_UART4, UART_IT_IDLE);
    // 清除空闲中断标志（如果有）
    __HAL_UART_CLEAR_IDLEFLAG(&husart_UART4);
}

void UART4_DMA_Rx_Configuration(void)
{
    // DMA控制器时钟使能
    __HAL_RCC_DMA1_CLK_ENABLE();
    
    // 配置DMA接收
    hdma_uart4_rx.Instance = DMA1_Stream2;
    hdma_uart4_rx.Init.Channel = DMA_CHANNEL_4;
    hdma_uart4_rx.Init.Direction = DMA_PERIPH_TO_MEMORY;
    hdma_uart4_rx.Init.PeriphInc = DMA_PINC_DISABLE;
    hdma_uart4_rx.Init.MemInc = DMA_MINC_ENABLE;
    hdma_uart4_rx.Init.PeriphDataAlignment = DMA_PDATAALIGN_BYTE;
    hdma_uart4_rx.Init.MemDataAlignment = DMA_MDATAALIGN_BYTE;
    hdma_uart4_rx.Init.Mode = DMA_CIRCULAR;  // 循环模式
//	hdma_uart4_rx.Init.Mode = DMA_NORMAL;  // 正常模式（非循环）
    hdma_uart4_rx.Init.Priority = DMA_PRIORITY_HIGH;
    hdma_uart4_rx.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    
    HAL_DMA_Init(&hdma_uart4_rx);

    // 关联DMA到UART
    __HAL_LINKDMA(&husart_UART4, hdmarx, hdma_uart4_rx);
}
// DMA Stream2中断服务函数 (UART4_RX)
void DMA1_Stream2_IRQHandler(void)
{
    HAL_DMA_IRQHandler(&hdma_uart4_rx);
}

//***************  重定向c库函数printf到UART4_USARTx  ***************
int fputc(int ch, FILE *f)
{
	HAL_UART_Transmit(&husart_UART4, (uint8_t *)&ch, 1, 1000);
	return ch;
}

//***************  重定向c库函数getchar,scanf到UART4_USARTx  ***************
int fgetc(FILE * f)
{
	uint8_t ch = 0;
	HAL_UART_Receive(&husart_UART4,&ch, 1, 0xffff);
	return ch;
}
////***************  串口中断服务函数  ***************
u32 test_dma_IRQ_times;
u8 UART4_RX_Buff[UART4_RX_MAX]; 	// 接收缓冲区
u16 UART4_RX_Count=0;                  	// 已接收到的字节数
u8 UART4_RX_New_Frame_flag=0;   	// 帧标志：1：一个新的数据帧  0：无数据帧
void UART4_IRQHandler(void)
{
	uint16_t rx_data_length;
    if(__HAL_UART_GET_FLAG(&husart_UART4, UART_FLAG_IDLE) != RESET)		// 检查空闲中断
    {
        __HAL_UART_CLEAR_IDLEFLAG(&husart_UART4);		// 清除空闲中断标志
        
        HAL_UART_DMAStop(&husart_UART4);// 停止DMA传输
        rx_data_length = UART4_DMA_RX_BUFFER_MAX_LENGTH - __HAL_DMA_GET_COUNTER(&hdma_uart4_rx);// 计算接收到的数据长度
		if (rx_data_length > 0)
		{
			UART4_RX_Count=rx_data_length;
			test_dma_IRQ_times++;
			if( test_dma_IRQ_times>0x0fffff)
				test_dma_IRQ_times=0;
			//*******************  UART4_RTU 接收  ******************
			UART4_RTU_Buff_Process();	//UART4_RTU 数据解析，解析出  功能码，数据位，数据段
			UART4_RTU_Buff_Deal();		//RS485 RTU 数据处理(事件处理)
		}
        HAL_UART_Receive_DMA(&husart_UART4, UART4_DMA_RX_Buffer, UART4_DMA_RX_BUFFER_MAX_LENGTH);	// 重新启动DMA接收，准备下一次接收
    }
    HAL_UART_IRQHandler(&husart_UART4);
}


////***************  串口中断服务函数  ***************
//u8 UART4_RX_Buff[UART4_RX_MAX]; 	// 接收缓冲区
//u16 UART4_RX_Count=0;                  	// 已接收到的字节数
//u8 UART4_RX_New_Frame_flag=0;   	// 帧标志：1：一个新的数据帧  0：无数据帧
//void UART4_IRQHandler(void)
//{
//	if(__HAL_USART_GET_FLAG(&husart_UART4,USART_FLAG_RXNE)!= RESET) // 接收中断：接收到数据
//	{
//		uint8_t data;
//		data=READ_REG(husart_UART4.Instance->DR); // 读取数据
//		if(UART4_RX_Count==0) // 如果是重新接收到数据帧，开启串口空闲中断
//		{
//			__HAL_UART_CLEAR_FLAG(&husart_UART4,USART_FLAG_IDLE); // 清除空闲中断标志
//			__HAL_UART_ENABLE_IT(&husart_UART4,UART_IT_IDLE);     // 使能空闲中断	    
//		}
//		if(UART4_RX_Count<UART4_RX_MAX)    // 判断接收缓冲区未满
//		{
//			UART4_RX_Buff[UART4_RX_Count]=data;  // 保存数据
//			UART4_RX_Count++;                // 增加接收字节数计数
//			//*******************  UART4_RTU 接收  ******************
//			UART4_RTU_Buff_Process();	//UART4_RTU 数据解析，解析出  功能码，数据位，数据段
//			UART4_RTU_Buff_Deal();		//RS485 RTU 数据处理(事件处理)
//		}
//		else
//		{
//			UART4_RX_Buff_CLR();//清除串口接收缓存数据
//		}
//	}
//	else if(__HAL_USART_GET_FLAG(&husart_UART4,USART_FLAG_IDLE)!= RESET) // 串口空闲中断
//	{
//		__HAL_UART_CLEAR_FLAG(&husart_UART4,USART_FLAG_IDLE); // 清除空闲中断标志
//		__HAL_UART_DISABLE_IT(&husart_UART4,UART_IT_IDLE);    // 关闭空闲中断
//		UART4_RX_New_Frame_flag=1;		                      // 数据帧置位，标识接收到一个完整数据帧
//	}
//}
void UART4_RX_Buff_CLR(void)            //清除串口接收缓存数据
{
	u16 k;
	for(k=0;k<UART4_RX_MAX;k++){UART4_RX_Buff[k] = 0x00;}
	UART4_RX_Count = 0; 
}

void UART4_Send_str( uint8_t *pData)
{
	u16 len=strlen((const char *)pData);
	HAL_UART_Transmit(&husart_UART4,pData,len,1000);	
} 


#include "system.h"
#include "adc.h"
#include "led.h"

ADC_HandleTypeDef hadcx;
DMA_HandleTypeDef hdma_adcx;

uint32_t ADC_Get_Value[ADC_CHANNEL_NUMBER];

void Adc_Init(void)
{
	ADC_ChannelConfTypeDef sConfig;

	__HAL_RCC_DMA2_CLK_ENABLE();
	/* 外设中断优先级配置和使能中断 */
	HAL_NVIC_SetPriority(DMA2_Stream0_IRQn, 1, 2);
	HAL_NVIC_EnableIRQ(DMA2_Stream0_IRQn); 
	
	hadcx.Instance = ADC1;
	hadcx.Init.ClockPrescaler = ADC_CLOCK_SYNC_PCLK_DIV8;			//4分频,84/4=21MHz
	hadcx.Init.Resolution = ADC_RESOLUTION_10B;					//ADC 12位分辨率
	hadcx.Init.ScanConvMode = ENABLE;								//扫描模式使能
	hadcx.Init.ContinuousConvMode = ENABLE;						//连续转换使能
	hadcx.Init.DiscontinuousConvMode = DISABLE;					//非连续转换失能
	hadcx.Init.ExternalTrigConvEdge = ADC_EXTERNALTRIGCONVEDGE_NONE;//软件触发
	hadcx.Init.ExternalTrigConv = ADC_SOFTWARE_START;				//软件触发
	hadcx.Init.DataAlign = ADC_DATAALIGN_RIGHT;					//数据右对齐
	hadcx.Init.NbrOfConversion = ADC_CHANNEL_NUMBER;				//规则通道数
	hadcx.Init.DMAContinuousRequests = ENABLE;					//DMA连续请求使能
	hadcx.Init.EOCSelection = ADC_EOC_SINGLE_CONV;				//采样完成进入中断

	HAL_ADC_Init(&hadcx);

	// 配置采样通道
	sConfig.Channel = ADC_CHANNEL_4;		// PA4 --> 排针ADC1
	sConfig.Rank = 1;
	sConfig.SamplingTime = ADC_SAMPLETIME_480CYCLES;  
	HAL_ADC_ConfigChannel(&hadcx, &sConfig);

	sConfig.Channel = ADC_CHANNEL_5;		// PA5 --> 排针ADC2
	sConfig.Rank = 2;
	HAL_ADC_ConfigChannel(&hadcx, &sConfig);

	sConfig.Channel = ADC_CHANNEL_6;		// PA6 --> 排针ADC3
	sConfig.Rank = 3;
	HAL_ADC_ConfigChannel(&hadcx, &sConfig);

	sConfig.Channel = ADC_CHANNEL_7;		// PA7 --> 排针ADC4
	sConfig.Rank = 4;
	HAL_ADC_ConfigChannel(&hadcx, &sConfig);

	sConfig.Channel = ADC_CHANNEL_14;		// PC4 --> 排针ADC5
	sConfig.Rank = 5;
	HAL_ADC_ConfigChannel(&hadcx, &sConfig);

	sConfig.Channel = ADC_CHANNEL_15;		// PC5 --> 电池电压
	sConfig.Rank = 6;
	HAL_ADC_ConfigChannel(&hadcx, &sConfig);

	sConfig.Channel = ADC_CHANNEL_12;		// PC2 --> 盘球电流反馈1
	sConfig.Rank = 7;
	HAL_ADC_ConfigChannel(&hadcx, &sConfig);

	sConfig.Channel = ADC_CHANNEL_13;		// PC3 --> 盘球电流反馈2
	sConfig.Rank = 8;
	HAL_ADC_ConfigChannel(&hadcx, &sConfig);

	HAL_ADC_Start_DMA(&hadcx,ADC_Get_Value,ADC_CHANNEL_NUMBER); 
	

}

/**
  * 函数功能: ADC外设初始化配置
  * 输入参数: hadc：AD外设句柄类型指针
  * 返 回 值: 无
  * 说    明: 该函数被HAL库内部调用
  */
void HAL_ADC_MspInit(ADC_HandleTypeDef* hadc)
{
  GPIO_InitTypeDef GPIO_InitStruct;
  if(hadc->Instance==ADC1)
  {
    __HAL_RCC_ADC1_CLK_ENABLE();
    __HAL_RCC_GPIOA_CLK_ENABLE();
	__HAL_RCC_GPIOC_CLK_ENABLE();
    
	//*****************  ADC 引脚初始化  *****************
    GPIO_InitStruct.Pin = GPIO_PIN_4|GPIO_PIN_5|GPIO_PIN_6|GPIO_PIN_7;	//ADC排针 1、2、3、4
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);
	  
    GPIO_InitStruct.Pin = GPIO_PIN_2|GPIO_PIN_3|GPIO_PIN_4|GPIO_PIN_5;	//盘球电流反馈1、盘球电流反馈2、ADC排针 5、电池电压
    GPIO_InitStruct.Mode = GPIO_MODE_ANALOG;
    GPIO_InitStruct.Pull = GPIO_NOPULL;
    HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);

      
    hdma_adcx.Instance = DMA2_Stream0;
    hdma_adcx.Init.Channel = DMA_CHANNEL_0;
    hdma_adcx.Init.Direction = DMA_PERIPH_TO_MEMORY;//外设到内存
    hdma_adcx.Init.PeriphInc = DMA_PINC_DISABLE;//外设地址自增失能
    hdma_adcx.Init.MemInc = DMA_MINC_ENABLE;//存储器地址自增使能
    hdma_adcx.Init.PeriphDataAlignment = DMA_PDATAALIGN_WORD;
    hdma_adcx.Init.MemDataAlignment = DMA_MDATAALIGN_WORD;
    hdma_adcx.Init.Mode = DMA_CIRCULAR;//循环模式
    hdma_adcx.Init.Priority = DMA_PRIORITY_HIGH;
    hdma_adcx.Init.FIFOMode = DMA_FIFOMODE_DISABLE;
    hdma_adcx.Init.FIFOThreshold = DMA_FIFO_THRESHOLD_HALFFULL;
    hdma_adcx.Init.MemBurst = DMA_MBURST_SINGLE;
    hdma_adcx.Init.PeriphBurst = DMA_PBURST_SINGLE;    
    HAL_DMA_Init(&hdma_adcx);
    
    __HAL_LINKDMA(hadc,DMA_Handle,hdma_adcx);
  }
}
void DMA2_Stream0_IRQHandler(void)
{
  HAL_DMA_IRQHandler(&hdma_adcx);
}
/**
  * 函数功能: ADC转换完成回调函数
  * 输入参数: hadc：ADC外设设备句柄
  * 返 回 值: 无
  * 说    明: 无
  */

float ADC_BAT_Voltage;		//电池电压

void HAL_ADC_ConvCpltCallback(ADC_HandleTypeDef* hadc)
{
	ADC_BAT_Voltage=(100+10)/10*ADC_Get_Value[5]*3.3/1023;		//电池电压
}
/******************* (C) COPYRIGHT 2015-2020 硬石嵌入式开发团队 *****END OF FILE****/




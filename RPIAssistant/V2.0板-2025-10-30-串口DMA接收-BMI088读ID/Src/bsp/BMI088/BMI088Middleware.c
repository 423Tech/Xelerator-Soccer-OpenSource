#include "BMI088Middleware.h"
#include "system.h"

extern SPI_HandleTypeDef hspi2;

void BMI088_GPIO_init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct = {0};

	/* GPIO Ports Clock Enable */
	__HAL_RCC_GPIOD_CLK_ENABLE();

	/*Configure GPIO pin Output Level */
	BMI088_CS_ACC=1;
	BMI088_CS_GYRO=1;
	/*Configure GPIO pin : PtPin */
	GPIO_InitStruct.Pin = GPIO_PIN_9|GPIO_PIN_12;	//BMI088_CS_Accel 、BMI088_CS_GYRO
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull = GPIO_PULLUP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);

	/*Configure GPIO pins : PCPin PCPin */
	GPIO_InitStruct.Pin = GPIO_PIN_13|GPIO_PIN_8;	//BMI_INT3_Gyro 、BMI_INT1_Accel
	GPIO_InitStruct.Mode = GPIO_MODE_IT_FALLING;
	GPIO_InitStruct.Pull = GPIO_PULLUP;
	HAL_GPIO_Init(GPIOD, &GPIO_InitStruct);
	
	/* EXTI interrupt init*/
	HAL_NVIC_SetPriority(EXTI9_5_IRQn, 0, 6);
	HAL_NVIC_EnableIRQ(EXTI9_5_IRQn);

	HAL_NVIC_SetPriority(EXTI15_10_IRQn, 0, 7);
	HAL_NVIC_EnableIRQ(EXTI15_10_IRQn);
}
// BMI_INT1_Accel 中断服务程序
void EXTI9_5_IRQHandler(void)
{
  HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_8);
}
// BMI_INT3_Gyro 中断服务程序
void EXTI15_10_IRQHandler(void)
{
  HAL_GPIO_EXTI_IRQHandler(GPIO_PIN_13);
}
void BMI088_com_init(void)
{


}
void BMI088_delay_ms(uint16_t ms)
{
    while(ms--)
    {
        BMI088_delay_us(1000);
    }
}

void BMI088_delay_us(uint16_t us)
{

    uint32_t ticks = 0;
    uint32_t told = 0;
    uint32_t tnow = 0;
    uint32_t tcnt = 0;
    uint32_t reload = 0;
    reload = SysTick->LOAD;
    ticks = us * 168;
    told = SysTick->VAL;
    while (1)
    {
        tnow = SysTick->VAL;
        if (tnow != told)
        {
            if (tnow < told)
            {
                tcnt += told - tnow;
            }
            else
            {
                tcnt += reload - tnow + told;
            }
            told = tnow;
            if (tcnt >= ticks)
            {
                break;
            }
        }
    }


}




void BMI088_ACCEL_NS_L(void)
{
	BMI088_CS_ACC=0; 		// BMI088_CS_GYRO
}
void BMI088_ACCEL_NS_H(void)
{
    BMI088_CS_ACC=1; 		// BMI088_CS_GYRO
}
void BMI088_GYRO_NS_L(void)
{
	BMI088_CS_GYRO=0;		// BMI088_CS_GYRO
}
void BMI088_GYRO_NS_H(void)
{
    BMI088_CS_GYRO=1;		// BMI088_CS_GYRO
}

uint8_t BMI088_read_write_byte(uint8_t txdata)
{
    uint8_t rx_data;
    HAL_SPI_TransmitReceive(&hspi2, &txdata, &rx_data, 1, 1000);
    return rx_data;
}


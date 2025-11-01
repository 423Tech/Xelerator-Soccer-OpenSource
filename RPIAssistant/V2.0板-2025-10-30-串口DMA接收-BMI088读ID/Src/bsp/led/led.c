#include "system.h"
#include "led.h"
void My_Delay_us(u16 us)
{
	uint16_t i;
	/*　
    工作条件：CPU主频168MHz ，MDK编译环境，1级优化
		经测试，循环次数为20~250时都能通讯正常
	*/
	for (i = 0; i < us; i++);
}
void LED_GPIO_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct;
	__HAL_RCC_GPIOB_CLK_ENABLE();
	__HAL_RCC_GPIOC_CLK_ENABLE();
	__HAL_RCC_GPIOE_CLK_ENABLE();
	
	//*********************  LED 、BEEP 输出 初始化  *********************
	GPIO_InitStruct.Pin = GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;	//LED Y、B、R 高电平有效
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull=GPIO_PULLDOWN;          
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);
	
	GPIO_InitStruct.Pin = GPIO_PIN_4|GPIO_PIN_10;				//蜂鸣器 、LED G 高电平有效
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull=GPIO_PULLDOWN;          
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);
	
	//*********************  弹射 输出 初始化  *********************
	GPIO_InitStruct.Pin = GPIO_PIN_0;			//Kick_IO  高电平有效
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull=GPIO_PULLDOWN;          
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);
	
	//*********************  通讯模块 输入 初始化  *********************
	GPIO_InitStruct.Pin = GPIO_PIN_2|GPIO_PIN_3;		//通讯模块 输入1、通讯模块 输入2
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_PULLDOWN;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOE, &GPIO_InitStruct); 
	
	LED_R=1;   	//LED 红灯
	LED_Y=0;   	//LED 黄灯
	LED_B=0;   	//LED 蓝灯
	LED_G=0;   	//LED 绿灯
	Beep=0;   	//蜂鸣器
	Kick_IO=0;	   			//弹射 1:充电 ； 0:放电
}


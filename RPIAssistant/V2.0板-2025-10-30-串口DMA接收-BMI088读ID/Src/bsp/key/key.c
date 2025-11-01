#include "system.h"
#include "key.h"

void KEY_GPIO_Init(void)
{
	GPIO_InitTypeDef GPIO_InitStruct; 
	
	__HAL_RCC_GPIOE_CLK_ENABLE();

//**************  按键输入 初始化  **************
	GPIO_InitStruct.Pin = GPIO_PIN_11|GPIO_PIN_12|GPIO_PIN_13|GPIO_PIN_14|GPIO_PIN_15;	//按键 BMI_KEY、KEY_RUN、KEY_3、KEY_2、KEY_1
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_PULLUP;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOE, &GPIO_InitStruct); 
}

//KEYState_TypeDef KEY1_StateRead(void)
//{
//  /* 读取此时按键值并判断是否是被按下状态，如果是被按下状态进入函数内 */
//  if(HAL_GPIO_ReadPin(KEY1_GPIO,KEY1_GPIO_PIN)==KEY1_DOWN_LEVEL)
//  {
//    /* 延时一小段时间，消除抖动 */
//    HAL_Delay(10);
//    /* 延时时间后再来判断按键状态，如果还是按下状态说明按键确实被按下 */
//    if(HAL_GPIO_ReadPin(KEY1_GPIO,KEY1_GPIO_PIN)==KEY1_DOWN_LEVEL)
//    {
//      /* 等待按键弹开才退出按键扫描函数 */
//      while(HAL_GPIO_ReadPin(KEY1_GPIO,KEY1_GPIO_PIN)==KEY1_DOWN_LEVEL);
//       /* 按键扫描完毕，确定按键被按下，返回按键被按下状态 */
//      return KEY_DOWN;
//    }
//  }
//  /* 按键没被按下，返回没被按下状态 */
//  return KEY_UP;
//}

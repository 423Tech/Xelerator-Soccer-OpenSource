/* 包含头文件 ----------------------------------------------------------------*/
#include "board_DO.h"
#include "board_check.h"
#include "usart/bsp_debug_usart.h"
#include "24cxx.h"
#include "74HC595.h"
extern u8 Board_Check_Result_Buff[Board_Result_Buff_MAX];	//测量板所有数据，反馈结果
//************************  测试项目1，短路检测，3V3、5V   ************************
u8 DO_1_3V3_OK_Flag;	//3V3，短路检测标志位，0;默认 ；1：好的 ； 2：不好
u8 DO_1_5V_OK_Flag;		//5V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
u8 DO_1_Power_OK_Flag;	//短路检测OK，0;默认 ；1：好的 ；
extern u8 Board_Check_Short_Flag;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
void DO_1_Short_Check(void)	//DO板，测试项目1，短路测试，3V3、5V 
{
	if(Power_Supply_3V3_Test==1)
	{
		printf("3v3 ok\n");
		DO_1_3V3_OK_Flag=1;
		Board_Check_Result_Buff[4]=1;	//RTU发送数据
		Board_Check_Result_Buff[5]=1;	//RTU发送数据
		Board_Check_Result_Buff[13]=1;	//RTU发送数据
	}
	else
	{
		printf("3v3 error\n");
		DO_1_3V3_OK_Flag=2;
		Board_Check_Result_Buff[4]=1;	//RTU发送数据
		Board_Check_Result_Buff[5]=0;	//RTU发送数据
		Board_Check_Result_Buff[13]=0;	//RTU发送数据
	}
	if(Power_Supply_5V_Test==1)
	{
		printf("5V ok\n");
		DO_1_5V_OK_Flag=1;
		Board_Check_Result_Buff[2]=1;	//RTU发送数据
		Board_Check_Result_Buff[3]=1;	//RTU发送数据
		Board_Check_Result_Buff[11]=1;	//RTU发送数据
	}
	else
	{
		printf("5V error\n");
		DO_1_5V_OK_Flag=2;
		Board_Check_Result_Buff[2]=1;	//RTU发送数据
		Board_Check_Result_Buff[3]=0;	//RTU发送数据
		Board_Check_Result_Buff[11]=0;	//RTU发送数据
	}
	
	if (DO_1_3V3_OK_Flag==1 && DO_1_5V_OK_Flag==1)
	{
		Power_Supply_3V3_EN=1;	//3V3对外供电，继电器开关
		Power_Supply_5V_EN=1;	//5V对外供电，继电器开关
		DO_1_Power_OK_Flag=1;	//短路检测OK，0;默认 ；1：好的 ；
		Board_Check_Short_Flag=0;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
		HAL_Delay(100);
	}
	else
		Board_Check_Short_Flag=1;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
}

//************************  测试项目2，EEPROM 读写检测   ************************
u8 DO_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
void DO_2_Epprom_Check(void)
{
	u8 DO_2_Epprom_Check_Res;
	DO_2_Epprom_Check_Res=Epprom_Check();
	if(DO_2_Epprom_Check_Res==0)
	{
		DO_2_Epprom_Check_OK_Flag=1;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
		Board_Check_Result_Buff[15]=1;	//RTU发送数据
	}
	else
	{
		DO_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
		Board_Check_Result_Buff[15]=0;	//RTU发送数据
	}
		
}
//************************  测试项目3，16路LED点亮,引脚初始化   ************************
u8 DO_3_LED_All_On[2] = {0xff, 0xff}; //LED灯全灭
u8 DO_3_LED_All_Off[2] = {0x00, 0x00}; //LED灯全亮
void DO_3_LED_ON_Set_ALL(u8 state)	//16 路 5V 全控制
{
	if(state==1)
		HC595_Send_N_Byte(&HC595_1,DO_3_LED_All_On,2);//16路灯全开
	else if(state==0)
		HC595_Send_N_Byte(&HC595_1,DO_3_LED_All_Off,2);//16路灯全灭
}
u8 DO_3_Led_Once_On[2] ={0x00,0x00};//led逐个点亮
void DO_3_LED_ON_Set_Channel(u8 ch)	//单个LED控制
{
	if(ch<=8)
		DO_3_Led_Once_On[1]=(1<<(ch-1));
	else if(ch>8 && ch<=16)
		DO_3_Led_Once_On[0]=(1<<(ch-9));
	
	HC595_Send_N_Byte(&HC595_1,DO_3_Led_Once_On,2);//单独一个灯亮，其他全灭
	DO_3_Led_Once_On[0]=0;
	DO_3_Led_Once_On[1]=0;
}
//************************  测试项目4，16路LED点亮后，通道检测   ************************
//默认低电平，高电平有效
void DO_4_LED_Cut_GPIO_Init(void)	
{
	GPIO_InitTypeDef GPIO_InitStruct;
	__HAL_RCC_GPIOE_CLK_ENABLE();
	__HAL_RCC_GPIOB_CLK_ENABLE();
	__HAL_RCC_GPIOG_CLK_ENABLE();
//**************  输入	**************
	GPIO_InitStruct.Pin = GPIO_PIN_1|GPIO_PIN_0;//1、2
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);  	
	
	GPIO_InitStruct.Pin = GPIO_PIN_9|GPIO_PIN_8|GPIO_PIN_7|GPIO_PIN_6|GPIO_PIN_5|GPIO_PIN_4|GPIO_PIN_3;//3、4、5、6、7、8、9
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOB, &GPIO_InitStruct);  
	
	GPIO_InitStruct.Pin = GPIO_PIN_15|GPIO_PIN_14|GPIO_PIN_13|GPIO_PIN_12|GPIO_PIN_11|GPIO_PIN_10|GPIO_PIN_9;//10、11、12、13、14、15、16
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);  
}

u8 DO_4_LED_Cut_Check(u8 ch)	//测试项目4，16路LED点亮后，单独通道检测
{
	u8 state;
	switch(ch)
	{
		case 1:state= DO_4_LED_Cut_Check_INT_1;break;
		case 2:state= DO_4_LED_Cut_Check_INT_2;break;
		case 3:state= DO_4_LED_Cut_Check_INT_3;break;
		case 4:state= DO_4_LED_Cut_Check_INT_4;break;
		case 5:state= DO_4_LED_Cut_Check_INT_5;break;
		case 6:state= DO_4_LED_Cut_Check_INT_6;break;
		case 7:state= DO_4_LED_Cut_Check_INT_7;break;
		case 8:state= DO_4_LED_Cut_Check_INT_8;break;
		case 9:state= DO_4_LED_Cut_Check_INT_9;break;
		case 10:state= DO_4_LED_Cut_Check_INT_10;break;
		case 11:state= DO_4_LED_Cut_Check_INT_11;break;
		case 12:state= DO_4_LED_Cut_Check_INT_12;break;
		case 13:state= DO_4_LED_Cut_Check_INT_13;break;
		case 14:state= DO_4_LED_Cut_Check_INT_14;break;
		case 15:state= DO_4_LED_Cut_Check_INT_15;break;
		case 16:state= DO_4_LED_Cut_Check_INT_16;break;
	}
	return state;
}
u8 DO_4_LED_Channel_Check_State[17];	//通道检测状态 0 ：不好 ；1：好 
//  这里，因为被测板为干触点，有效时，触点与地导通，所以灯亮，伴随低电平有效
u8 DO_34_LED_Check_OK_Flag;	//	led 通道 检测结果
void DO_34_LED_ON_Check_Channel(u8 ch)//单独点亮某一通道，检测3、4项目 （摄像头检测LED好坏、通道检测、断线检测）
{
	if(ch==0)
	{
		DO_3_LED_ON_Set_ALL(0);	//16 个 LED 全控制	1:全开 ； 0：全关
	}
	else
	{
		DO_3_LED_ON_Set_Channel(ch);	//单个LED控制
//		HAL_Delay(LED_ON_Delay);
		DO_4_LED_Channel_Check_State[ch]= DO_4_LED_Cut_Check(ch);	//测试项目5，16路LED点亮后，单独通道检测
		if(DO_4_LED_Channel_Check_State[ch]==0)
			Board_Check_Result_Buff[ch+RTU_Result_Buf_Num_LED_Cut-1]=1;	//RTU发送数据
		else
			Board_Check_Result_Buff[ch+RTU_Result_Buf_Num_LED_Cut-1]=0;	//RTU发送数据
		printf("LED_CUT %d: %d\r\n",ch,DO_4_LED_Channel_Check_State[ch]);
	}
}

//************************  DO 卡，LED 通道检测、断线检测，结果汇总，全合格才算合格   ************************
void DO_34_LED_Check_Result(void)
{
	u8 ch;
	for(ch=1;ch<=16;ch++)
	{
		if(DO_4_LED_Channel_Check_State[ch]==0)
			DO_34_LED_Check_OK_Flag=1;	//	led 通道 检测结果
		else
		{
			DO_34_LED_Check_OK_Flag=0;	//	led 通道 检测结果
			break;
		}
	}
	Board_Check_Final_Result=Board_Check_Final_Result & DO_34_LED_Check_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
	Board_Check_Result_Buff[RTU_Result_Buf_Num_Final_Result]=Board_Check_Final_Result;	//最终洁检测结果
}

void DO_34_LED_ON_Check_Result_CLR(void)//检测4、5、6项目 （摄像头检测LED好坏、通道检测、断线检测）结果 清零
{
	u8 k;
	for(k=0;k<=16;k++)
	{
		DO_4_LED_Channel_Check_State[k]= 0;	//测试项目5，24路LED点亮后，单独通道检测
	}
}
//************************  DO卡，初始化所有   ************************
void DO_Board_Init_ALL(void)//DO卡，初始化所有
{
	AT24CXX_Init();			//Epprom初始化
	HC595_GPIO_Init(&HC595_1);//DO卡 74HC595 初始化 16路LED
	HC595_GPIO_Init(&HC595_2);//DO卡 74HC595 初始化	复用DO卡的23个触点
	DO_4_LED_Cut_GPIO_Init();//测试项目6，24路LED点亮后，通道检测 ,初始化引脚	
	

}
//************************  DO卡，检测所有,除了LED   ************************
void DO_Board_Check(void)//DO卡，检测所有
{
	DO_1_Short_Check();	//DO板，测试项目1，短路测试，3V3、5V 
	if(Board_Check_Short_Flag==0)//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
	{
		switch(Borad_Single_Check_Type)
		{
			case 0:// 单独测试 类型，正常测试 
				DO_2_Epprom_Check();//DO板，测试项目2，EEPROM 读写检测
				Board_Check_Final_Result=Board_Check_Final_Result & DO_1_Power_OK_Flag & DO_2_Epprom_Check_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;
			case ADIO_Single_Check_Power:	// 单独测试 类型，单独电源
				Board_Check_Final_Result=Board_Check_Final_Result & DO_1_Power_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;
			case ADIO_Single_Check_EPPROM:// 单独测试 类型，单独EPPROM
				DO_2_Epprom_Check();//DO板，测试项目2，EEPROM 读写检测
				Board_Check_Final_Result=Board_Check_Final_Result & DO_1_Power_OK_Flag & DO_2_Epprom_Check_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;		
		}
	}
	Board_Check_Result_Buff[RTU_Result_Buf_Num_Final_Result]=Board_Check_Final_Result;	//最终洁检测结果
}
//************************  DO板 处理所有结果，判断是否全部合格   ************************
void DO_Board_Check_LED_Result_Deal(void)
{
	DO_34_LED_Check_Result();	//DI 卡，LED 通道检测、断线检测，结果汇总，全合格才算合格
}
void DO_Check_Reset(void)	//DO板，测试项目复位
{
	DO_34_LED_ON_Check_Result_CLR();	//检测4、5、6项目 （摄像头检测LED好坏、通道检测、断线检测）结果 清零
	Power_Supply_3V3_EN=0;	//3V3对外供电，继电器开关
	Power_Supply_5V_EN=0;	//5V对外供电，继电器开关
	DO_1_3V3_OK_Flag=0;		//3V3，短路检测标志位，0;默认 ；1：好的 ； 2：不好
	DO_1_5V_OK_Flag=0;		//5V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
	DO_1_Power_OK_Flag=0;	//短路检测OK，0;默认 ；1：好的 ；
	DO_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
	DO_34_LED_Check_OK_Flag=0;	//	led 通道 检测结果
	Board_Check_Final_Result=1;	//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
	Board_Check_Short_Flag=0;	//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
}


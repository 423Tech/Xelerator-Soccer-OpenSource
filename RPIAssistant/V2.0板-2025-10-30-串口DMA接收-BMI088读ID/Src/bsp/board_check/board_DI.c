/* 包含头文件 ----------------------------------------------------------------*/
#include "board_DI.h"
#include "board_check.h"
#include "usart/bsp_debug_usart.h"
#include "24cxx.h"
#include "74HC595.h"
extern u8 Board_Check_Result_Buff[Board_Result_Buff_MAX];	//测量板所有数据，反馈结果
//************************  测试项目1，短路检测，3V3、5V   ************************
u8 DI_1_3V3_OK_Flag;	//3V3，短路检测标志位，0;默认 ；1：好的 ； 2：不好
u8 DI_1_5V_OK_Flag;		//5V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
u8 DI_1_Power_OK_Flag;	//短路检测OK，0;默认 ；1：好的 ；
extern u8 Board_Check_Short_Flag;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
void DI_1_Short_Check(void)	//DI板，测试项目1，短路测试，3V3、5V 
{
	if(Power_Supply_3V3_Test==1)
	{
		printf("3v3 ok\n");
		DI_1_3V3_OK_Flag=1;
		Board_Check_Result_Buff[4]=1;	//RTU发送数据
		Board_Check_Result_Buff[5]=1;	//RTU发送数据
		Board_Check_Result_Buff[13]=1;	//RTU发送数据
	}
	else
	{
		printf("3v3 error\n");
		DI_1_3V3_OK_Flag=2;
		Board_Check_Result_Buff[4]=1;	//RTU发送数据
		Board_Check_Result_Buff[5]=0;	//RTU发送数据
		Board_Check_Result_Buff[13]=0;	//RTU发送数据
	}
	if(Power_Supply_5V_Test==1)
	{
		printf("5V ok\n");
		DI_1_5V_OK_Flag=1;
		Board_Check_Result_Buff[2]=1;	//RTU发送数据
		Board_Check_Result_Buff[3]=1;	//RTU发送数据
		Board_Check_Result_Buff[11]=1;	//RTU发送数据
	}
	else
	{
		printf("5V error\n");
		DI_1_5V_OK_Flag=2;
		Board_Check_Result_Buff[2]=1;	//RTU发送数据
		Board_Check_Result_Buff[3]=0;	//RTU发送数据
		Board_Check_Result_Buff[11]=0;	//RTU发送数据
	}
	
	if (DI_1_3V3_OK_Flag==1 && DI_1_5V_OK_Flag==1)
	{
		Power_Supply_3V3_EN=1;	//3V3对外供电，继电器开关
		Power_Supply_5V_EN=1;	//5V对外供电，继电器开关
		DI_1_Power_OK_Flag=1;	//短路检测OK，0;默认 ；1：好的 ； 2：不好
		Board_Check_Short_Flag=0;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
		HAL_Delay(100);
	}
	else
		Board_Check_Short_Flag=1;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
}

//************************  测试项目2，EEPROM 读写检测   ************************
u8 DI_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
void DI_2_Epprom_Check(void)
{
	u8 DI_2_Epprom_Check_Res;
	DI_2_Epprom_Check_Res=Epprom_Check();
	if(DI_2_Epprom_Check_Res==0)
	{
		DI_2_Epprom_Check_OK_Flag=1;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
		Board_Check_Result_Buff[15]=1;	//RTU发送数据
	}
	else
	{
		DI_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
		Board_Check_Result_Buff[15]=0;	//RTU发送数据
	}	
}
////************************  测试项目3，24路LED点亮   ************************
u8 DI_3_Led_All_On[3] = {0xff, 0xff, 0xff}; //LED灯全灭
u8 DI_3_Led_All_Off[3] = {0x00, 0x00, 0x00}; //LED灯全亮
void DI_3_LED_ON_Set_ALL(u8 state)	//24 个 LED 全控制	1:全开 ； 0：全关
{
	if(state==1)
		HC595_Send_N_Byte(&HC595_2,DI_3_Led_All_On,3);//24路灯全开
	else if(state==0)
		HC595_Send_N_Byte(&HC595_2,DI_3_Led_All_Off,3);//24路灯全灭
}
u8 DI_3_Led_Once_On[3] ={0x00,0x00,0x00};//led逐个点亮
void DI_3_LED_ON_Set_Channel(u8 ch)	//单个LED控制
{
	if(ch<=8)
	{
		DI_3_Led_Once_On[2]=(1<<(ch-1));
	}
	else if(ch>8 && ch<=16)
	{
		DI_3_Led_Once_On[1]=(1<<(ch-9));
	}
	else
	{
		DI_3_Led_Once_On[0]=(1<<(ch-17));
	}
	HC595_Send_N_Byte(&HC595_2,DI_3_Led_Once_On,3);//单独一个灯亮，其他全灭
	DI_3_Led_Once_On[0]=0;
	DI_3_Led_Once_On[1]=0;
	DI_3_Led_Once_On[2]=0;
}

//************************  测试项目5，24路LED点亮后，通道检测   ************************
//默认低电平，高电平有效
void DI_5_LED_Channel_GPIO_Init(void)	//测试项目5，24路LED点亮后，通道检测 ,初始化引脚
{
	GPIO_InitTypeDef GPIO_InitStruct;
	__HAL_RCC_GPIOA_CLK_ENABLE();
	__HAL_RCC_GPIOC_CLK_ENABLE();
	__HAL_RCC_GPIOG_CLK_ENABLE();
	__HAL_RCC_GPIOD_CLK_ENABLE();
//**************  输入	**************
	GPIO_InitStruct.Pin = GPIO_PIN_12|GPIO_PIN_11|GPIO_PIN_10|GPIO_PIN_9|GPIO_PIN_8;//1、2、3、4、5
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOA, &GPIO_InitStruct);  	
	
	GPIO_InitStruct.Pin = GPIO_PIN_9|GPIO_PIN_8|GPIO_PIN_7|GPIO_PIN_6;//6、7、8、9
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOC, &GPIO_InitStruct);  
	
	GPIO_InitStruct.Pin = GPIO_PIN_8|GPIO_PIN_7|GPIO_PIN_6|GPIO_PIN_5|GPIO_PIN_4|GPIO_PIN_3|GPIO_PIN_2;//10、11、12、13、14、15、16
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);  
	
	GPIO_InitStruct.Pin = GPIO_PIN_15|GPIO_PIN_14|GPIO_PIN_13|GPIO_PIN_12|GPIO_PIN_11|GPIO_PIN_10|GPIO_PIN_9|GPIO_PIN_8;//17、18、19、20、21、22、23、24
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOD, &GPIO_InitStruct); 
}

u8 DI_5_LED_Channel_Check(u8 ch)	//测试项目5，24路LED点亮后，单独通道检测
{
	u8 state;
	switch(ch)
	{
		case 1:state= DI_5_LED_Channel_Check_INT_1;break;
		case 2:state= DI_5_LED_Channel_Check_INT_2;break;
		case 3:state= DI_5_LED_Channel_Check_INT_3;break;
		case 4:state= DI_5_LED_Channel_Check_INT_4;break;
		case 5:state= DI_5_LED_Channel_Check_INT_5;break;
		case 6:state= DI_5_LED_Channel_Check_INT_6;break;
		case 7:state= DI_5_LED_Channel_Check_INT_7;break;
		case 8:state= DI_5_LED_Channel_Check_INT_8;break;
		case 9:state= DI_5_LED_Channel_Check_INT_9;break;
		case 10:state= DI_5_LED_Channel_Check_INT_10;break;
		case 11:state= DI_5_LED_Channel_Check_INT_11;break;
		case 12:state= DI_5_LED_Channel_Check_INT_12;break;
		case 13:state= DI_5_LED_Channel_Check_INT_13;break;
		case 14:state= DI_5_LED_Channel_Check_INT_14;break;
		case 15:state= DI_5_LED_Channel_Check_INT_15;break;
		case 16:state= DI_5_LED_Channel_Check_INT_16;break;
		case 17:state= DI_5_LED_Channel_Check_INT_17;break;
		case 18:state= DI_5_LED_Channel_Check_INT_18;break;
		case 19:state= DI_5_LED_Channel_Check_INT_19;break;
		case 20:state= DI_5_LED_Channel_Check_INT_20;break;
		case 21:state= DI_5_LED_Channel_Check_INT_21;break;
		case 22:state= DI_5_LED_Channel_Check_INT_22;break;
		case 23:state= DI_5_LED_Channel_Check_INT_23;break;
		case 24:state= DI_5_LED_Channel_Check_INT_24;break;	
	}
	return state;
}
//************************  测试项目6，24路LED点亮后，断线检测   ************************
//默认低电平，高电平有效
void DI_6_LED_Cut_GPIO_Init(void)	
{
	GPIO_InitTypeDef GPIO_InitStruct;
	__HAL_RCC_GPIOE_CLK_ENABLE();
	__HAL_RCC_GPIOB_CLK_ENABLE();
	__HAL_RCC_GPIOG_CLK_ENABLE();
	__HAL_RCC_GPIOD_CLK_ENABLE();
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
	
	GPIO_InitStruct.Pin = GPIO_PIN_7|GPIO_PIN_6|GPIO_PIN_5|GPIO_PIN_4|GPIO_PIN_3|GPIO_PIN_2|GPIO_PIN_1|GPIO_PIN_1;//17、18、19、20、21、22、23、24
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOD, &GPIO_InitStruct); 
}

u8 DI_6_LED_Cut_Check(u8 ch)	//测试项目6，24路LED点亮后，单独断线检测
{
	u8 state;
	switch(ch)
	{
		case 1:state= DI_6_LED_Cut_Check_INT_1;break;
		case 2:state= DI_6_LED_Cut_Check_INT_2;break;
		case 3:state= DI_6_LED_Cut_Check_INT_3;break;
		case 4:state= DI_6_LED_Cut_Check_INT_4;break;
		case 5:state= DI_6_LED_Cut_Check_INT_5;break;
		case 6:state= DI_6_LED_Cut_Check_INT_6;break;
		case 7:state= DI_6_LED_Cut_Check_INT_7;break;
		case 8:state= DI_6_LED_Cut_Check_INT_8;break;
		case 9:state= DI_6_LED_Cut_Check_INT_9;break;
		case 10:state= DI_6_LED_Cut_Check_INT_10;break;
		case 11:state= DI_6_LED_Cut_Check_INT_11;break;
		case 12:state= DI_6_LED_Cut_Check_INT_12;break;
		case 13:state= DI_6_LED_Cut_Check_INT_13;break;
		case 14:state= DI_6_LED_Cut_Check_INT_14;break;
		case 15:state= DI_6_LED_Cut_Check_INT_15;break;
		case 16:state= DI_6_LED_Cut_Check_INT_16;break;
		case 17:state= DI_6_LED_Cut_Check_INT_17;break;
		case 18:state= DI_6_LED_Cut_Check_INT_18;break;
		case 19:state= DI_6_LED_Cut_Check_INT_19;break;
		case 20:state= DI_6_LED_Cut_Check_INT_20;break;
		case 21:state= DI_6_LED_Cut_Check_INT_21;break;
		case 22:state= DI_6_LED_Cut_Check_INT_22;break;
		case 23:state= DI_6_LED_Cut_Check_INT_23;break;
		case 24:state= DI_6_LED_Cut_Check_INT_24;break;	
	}
	return state;
}
u8 DI_5_LED_Channel_Check_State[25];//通道检测状态 0 ：不好 ；1：好
u8 DI_5_LED_Cut_Check_State[25];	//断线检测状态 0 ：不好 ；1：好 
u16 DI_3_LED_ON_Delay=200;//LED流水灯，延时
u8 DI_3456_LED_Check_OK_Flag;	//	led 断线 检测结果
void DI_3456_LED_ON_Check_Channel(u8 ch)//单独点亮某一通道，检测4、5、6项目 （摄像头检测LED好坏、通道检测、断线检测）
{
	if(ch==0)
	{
		DI_3_LED_ON_Set_ALL(0);	//24 个 LED 全控制	1:全开 ； 0：全关
	}
	else
	{
		DI_3_LED_ON_Set_Channel(ch);	//单个LED控制 亮
//		HAL_Delay(LED_ON_Delay);
		DI_5_LED_Channel_Check_State[ch]= DI_5_LED_Channel_Check(ch);	//测试项目5，24路LED点亮后，单独通道检测
		DI_5_LED_Cut_Check_State[ch]= DI_6_LED_Cut_Check(ch);		//测试项目6，24路LED点亮后，单独断线检测	
		if(DI_5_LED_Channel_Check_State[ch]==1)
			Board_Check_Result_Buff[ch+RTU_Result_Buf_Num_LED_Cut-1]=1;	//RTU发送数据
		else
			Board_Check_Result_Buff[ch+RTU_Result_Buf_Num_LED_Cut-1]=0;	//RTU发送数据
		
		if(DI_5_LED_Cut_Check_State[ch]==1)
			Board_Check_Result_Buff[ch+RTU_Result_Buf_Num_LED_Cut-1]=Board_Check_Result_Buff[ch+RTU_Result_Buf_Num_LED_Cut-1]|0x10;	//RTU发送数据
		else
			Board_Check_Result_Buff[ch+RTU_Result_Buf_Num_LED_Cut-1]=Board_Check_Result_Buff[ch+RTU_Result_Buf_Num_LED_Cut-1]|0x00;	//RTU发送数据
		
		printf("Channel_Check %d: %d\r\n",ch,DI_5_LED_Channel_Check_State[ch]);
		printf("Cut_Check %d: %d\r\n",ch,DI_5_LED_Cut_Check_State[ch]);
	}
}
//************************  DI 卡，LED 通道检测、断线检测，结果汇总，全合格才算合格   ************************
void DI_3456_LED_Check_Result(void)
{
	u8 ch;
	for(ch=1;ch<=24;ch++)
	{
		if(DI_5_LED_Channel_Check_State[ch]==1 && DI_5_LED_Cut_Check_State[ch]==1)
			DI_3456_LED_Check_OK_Flag=1;	//	led 断线 检测结果
		else
		{
			DI_3456_LED_Check_OK_Flag=0;	//	led 断线 检测结果
			break;
		}
	}
	Board_Check_Final_Result=Board_Check_Final_Result & DI_3456_LED_Check_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
	Board_Check_Result_Buff[RTU_Result_Buf_Num_Final_Result]=Board_Check_Final_Result;	//最终洁检测结果
}
void DI_3456_LED_ON_Check_Result_CLR(void)//检测4、5、6项目 （摄像头检测LED好坏、通道检测、断线检测）结果 清零
{
	u8 k;
	for(k=0;k<=24;k++)
	{
		DI_5_LED_Channel_Check_State[k]= 0;	//测试项目5，24路LED点亮后，单独通道检测
		DI_5_LED_Cut_Check_State[k]= 0;		//测试项目6，24路LED点亮后，单独断线检测	
	}
}
//************************  DI初始化所有   ************************
void DI_Board_Init_ALL(void)//DI初始化所有
{
	AT24CXX_Init();			//Epprom初始化
	HC595_GPIO_Init(&HC595_2);//DI卡 74HC595 初始化
	DI_5_LED_Channel_GPIO_Init();//测试项目5，24路LED点亮后，通道检测 ,初始化引脚
	DI_6_LED_Cut_GPIO_Init();//测试项目6，24路LED点亮后，断线检测 ,初始化引脚	
}
//************************  DI板检测所有,除了LED   ************************
void DI_Board_Check(void)//DI板检测所有
{
	DI_1_Short_Check();		//DI板，测试项目1，短路测试，3V3、5V、24V
	if(Board_Check_Short_Flag==0)//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
	{
		switch(Borad_Single_Check_Type)
		{
			case 0:// 单独测试 类型，正常测试 
				DI_2_Epprom_Check();	//DI板，测试项目2，EEPROM 读写检测
				Board_Check_Final_Result=Board_Check_Final_Result & DI_1_Power_OK_Flag & DI_2_Epprom_Check_OK_Flag ;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;
			case ADIO_Single_Check_Power:	// 单独测试 类型，单独电源
				Board_Check_Final_Result=Board_Check_Final_Result & DI_1_Power_OK_Flag ;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;
			case ADIO_Single_Check_EPPROM:// 单独测试 类型，单独EPPROM
				DI_2_Epprom_Check();	//AO板，测试项目2，EEPROM 读写检测
				Board_Check_Final_Result=Board_Check_Final_Result & DI_1_Power_OK_Flag & DI_2_Epprom_Check_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;				
		}
	}
	Board_Check_Result_Buff[RTU_Result_Buf_Num_Final_Result]=Board_Check_Final_Result;	//最终洁检测结果
}
//************************  DI板 处理所有结果，判断是否全部合格   ************************
void DI_Board_Check_LED_Result_Deal(void)
{
	DI_3456_LED_Check_Result();	//DI 卡，LED 通道检测、断线检测，结果汇总，全合格才算合格
}
void DI_Check_Reset(void)	//DI板，测试项目复位
{
	DI_3456_LED_ON_Check_Result_CLR();//检测4、5、6项目 （摄像头检测LED好坏、通道检测、断线检测）结果 清零
	Power_Supply_3V3_EN=0;	//3V3对外供电，继电器开关
	Power_Supply_5V_EN=0;	//5V对外供电，继电器开关
	DI_1_3V3_OK_Flag=0;		//3V3，短路检测标志位，0;默认 ；1：好的 ； 2：不好
	DI_1_5V_OK_Flag=0;		//5V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
	DI_1_Power_OK_Flag=0;	//短路检测OK，0;默认 ；1：好的 ；
	DI_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
	DI_3456_LED_Check_OK_Flag=0;	//	led 断线 检测结果
	Board_Check_Final_Result=1;	//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
	Board_Check_Short_Flag=0;	//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
}


/* 包含头文件 ----------------------------------------------------------------*/
#include "board_AO.h"
#include "board_check.h"
#include "usart/bsp_debug_usart.h"
#include "24cxx.h"
#include "TPC116S1.h"
#include "adc.h"
#include <stdio.h>
#include <string.h>
extern u8 Board_Check_Result_Buff[Board_Result_Buff_MAX];	//测量板所有数据，反馈结果
//************************  测试项目1，短路检测，3V3、5V、24V   ************************
u8 AO_1_3V3_OK_Flag;	//3V3，短路检测标志位，0;默认 ；1：好的 ； 2：不好
u8 AO_1_5V_OK_Flag;		//5V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
u8 AO_1_24V_OK_Flag;	//24V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
u8 AO_1_Power_OK_Flag;	//短路检测OK，0;默认 ；1：好的 ；
extern u8 Board_Check_Short_Flag;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
void AO_1_Short_Check(void)	//AO板，测试项目1，短路测试，3V3、5V、24V
{
	if(Power_Supply_3V3_Test==1)
	{
		printf("3v3 ok\n");
		AO_1_3V3_OK_Flag=1;
		Board_Check_Result_Buff[4]=1;	//RTU发送数据
		Board_Check_Result_Buff[5]=1;	//RTU发送数据
		Board_Check_Result_Buff[13]=1;	//RTU发送数据
	}
	else
	{
		printf("3v3 error\n");
		AO_1_3V3_OK_Flag=2;
		Board_Check_Result_Buff[4]=1;	//RTU发送数据
		Board_Check_Result_Buff[5]=0;	//RTU发送数据
		Board_Check_Result_Buff[13]=0;	//RTU发送数据
	}
	if(Power_Supply_5V_Test==1)
	{
		printf("5V ok\n");
		AO_1_5V_OK_Flag=1;
		Board_Check_Result_Buff[2]=1;	//RTU发送数据
		Board_Check_Result_Buff[3]=1;	//RTU发送数据
		Board_Check_Result_Buff[11]=1;	//RTU发送数据
	}
	else
	{
		printf("5V error\n");
		AO_1_5V_OK_Flag=2;
		Board_Check_Result_Buff[2]=1;	//RTU发送数据
		Board_Check_Result_Buff[3]=0;	//RTU发送数据
		Board_Check_Result_Buff[11]=0;	//RTU发送数据
	}
	if(Power_Supply_24V_Test==1)
	{
		printf("24V ok\n");
		AO_1_24V_OK_Flag=1;
		Board_Check_Result_Buff[0]=1;	//RTU发送数据
		Board_Check_Result_Buff[1]=1;	//RTU发送数据
		Board_Check_Result_Buff[9]=1;	//RTU发送数据
	}
	else
	{
		printf("24V error\n");
		AO_1_24V_OK_Flag=2;
		Board_Check_Result_Buff[0]=1;	//RTU发送数据
		Board_Check_Result_Buff[1]=0;	//RTU发送数据
		Board_Check_Result_Buff[9]=0;	//RTU发送数据
	}
	if (AO_1_3V3_OK_Flag==1 && AO_1_5V_OK_Flag==1 && AO_1_24V_OK_Flag==1)
	{
		Power_Supply_3V3_EN=1;	//3V3对外供电，继电器开关
		Power_Supply_5V_EN=1;	//5V对外供电，继电器开关
		Power_Supply_24V_EN=1;	//24V对外供电，继电器开关
		AO_1_Power_OK_Flag=1;	//短路检测OK，0;默认 ；1：好的 ； 2：不好
		Board_Check_Short_Flag=0;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
		HAL_Delay(100);
	}
	else
		Board_Check_Short_Flag=1;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
}
//************************  测试项目2，EEPROM 读写检测   ************************
u8 AO_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
void AO_2_Epprom_Check(void)
{
	u8 AO_2_Epprom_Check_Res;
	AO_2_Epprom_Check_Res=Epprom_Check();
	if(AO_2_Epprom_Check_Res==0)
	{
		AO_2_Epprom_Check_OK_Flag=1;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
		Board_Check_Result_Buff[15]=1;	//RTU发送数据
	}
	else
	{
		AO_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
		Board_Check_Result_Buff[15]=0;	//RTU发送数据
	}	
}
//************************  测试项目3，4路LED点亮   ************************
void AO_3_LED_GPIO_Init(void)	//测试项目3，4路LED,初始化引脚
{
	GPIO_InitTypeDef GPIO_InitStruct;
	__HAL_RCC_GPIOG_CLK_ENABLE();
	__HAL_RCC_GPIOE_CLK_ENABLE();
//**************  输出  **************	 
	GPIO_InitStruct.Pin = GPIO_PIN_9|GPIO_PIN_8|GPIO_PIN_7;	//1、2、3
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull=GPIO_PULLDOWN;        
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

	GPIO_InitStruct.Pin = GPIO_PIN_1;	//4
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull=GPIO_PULLDOWN;        
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);
	
}
void AO_3_LED_Set_All(u8 state)	////测试项目3，4路LED,全部控制 ,1:亮 ；0：灭
{
	if(state==1)
	{
		AO_3_LED_Channel_1=1;
		AO_3_LED_Channel_2=1;
		AO_3_LED_Channel_3=1;
		AO_3_LED_Channel_4=1;
	}
	else if(state==0)
	{
		AO_3_LED_Channel_1=0;
		AO_3_LED_Channel_2=0;
		AO_3_LED_Channel_3=0;
		AO_3_LED_Channel_4=0;	
	}
	
}
void AO_3_LED_Set_Channel(u8 ch,u8 state)	//测试项目3，4路LED,,单个LED控制,ch:通道1~8 ； state,1亮 ； 0：灭
{
	switch(ch)
	{
		case 1:AO_3_LED_Channel_1=state;break;
		case 2:AO_3_LED_Channel_2=state;break;
		case 3:AO_3_LED_Channel_3=state;break;
		case 4:AO_3_LED_Channel_4=state;break;
	}
}
u16 AO_3_LED_ON_Delay=200;//LED流水灯，延时
u8 AO_LED_Checked_Sum;		//记录 LED灯，测量的数量
void AO_3_LED_Check(u8 ch)	//测试项目3，8路LED,检测
{
	if(ch==0)
	{
		AO_3_LED_Set_All(0);	//首先，全部灭
	}
	else
	{
		AO_3_LED_Set_Channel(ch,1);	//单个LED控制,ch:通道1~8 ； state,1亮 ； 0：灭
	}
}
//************************  测试项目4，被测板上 TPC116S1，输出DAC   ************************
void AO_4_TPC116S1_Set_DAC(u8 ch)	//AO板，测试项目4,被测板上 TPC116S1，输出DAC 
{
	switch(ch)
	{
		case 1:set_tpc_ma_current_value(&SPI_NSS1,12);break;	//
		case 2:set_tpc_ma_current_value(&SPI_NSS2,12);break;	//
		case 3:set_tpc_ma_current_value(&SPI_NSS3,12);break;	//
		case 4:set_tpc_ma_current_value(&SPI_NSS4,12);break;	//
	}
	HAL_Delay(100);
}
//************************  测试项目4，被测板上 TPC116S1，输出DAC 清零   ************************
void AO_4_TPC116S1_Set_DAC_CLR(u8 ch)	//AO板，测试项目4,被测板上 TPC116S1，输出DAC  清零  
{
	switch(ch)
	{
		case 1:set_tpc_ma_current_value(&SPI_NSS1,0);break;	//
		case 2:set_tpc_ma_current_value(&SPI_NSS2,0);break;	//
		case 3:set_tpc_ma_current_value(&SPI_NSS3,0);break;	//
		case 4:set_tpc_ma_current_value(&SPI_NSS4,0);break;	//
	}
	HAL_Delay(100);
}
//************************  测试项目5，被测板上的，SGM58200，初始化   ************************
void AO_5_SGM58200_Init(void)	//AO板，测试项目5，被测板上的，SGM58200，初始化
{
	IIC_Init(&IIC3);		//初始化，对应IIC
	sgm_write_config(&IIC3);//配置 SGM58200
	HAL_Delay(100);
}
//************************  测试项目5，读SGM58200数据   ************************
float AO_5_Current_Read(u8 ch)	//AO板，测试项目5，读SGM58200数据
{
	float current_ma=0;
	switch(ch)
	{
		case 1:current_ma=IIC_readAOFeedback(&IIC3);break;
		case 2:current_ma=IIC_readAOFeedback(&IIC3);break;
		case 3:current_ma=IIC_readAOFeedback(&IIC3);break;
		case 4:current_ma=IIC_readAOFeedback(&IIC3);break;
	}
	return current_ma;
	
}
//************************  测试项目4、5、6，SPI设置电流，IIC电流检测、ADC检测   ************************
float AO_5_Current_Check_Range[2]={10,14};	//标准电流值
u8 AO_5_Current_Check_Result[5];			//电流值检测结果，1：好的

extern uint32_t ADC_ConvertedValue[ADC_CHANNEL_NUMBER];
u16 AO_6_Current_ADC_Range[2]={400,510};	//电流采样ADC正常范围
u16 AO_6_Current_ADC_Check_Result[5];	//电流采样ADC检测结果，1：好的
u8 AO_456_Current_Check_OK_Flag;	//	电流检测结果

float AO_5_Current_Read_Value_Buff[5];	//读SGM58200数据，保存数组
u8 AO_Memcpy_Buff[4];	//复制float 到 数组


void AO_456_Current_AND_ADC_Check(void)		//测试项目4、5、6，SPI设置电流，IIC电流检测、ADC检测
{
	u8 i;
	float current_ma=0;
	for(i=1;i<5;i++)
	{
		AO_4_TPC116S1_Set_DAC(i);	//AO板，测试项目4,被测板上 TPC116S1，输出DAC 
		current_ma=AO_5_Current_Read(i);//AO板，测试项目5，读SGM58200数据
		AO_5_Current_Read_Value_Buff[i]=current_ma;	//读SGM58200数据，保存数组

		memcpy(AO_Memcpy_Buff,&current_ma,4);
		printf("Current_float = 0x%x%x%x%x\r\n",AO_Memcpy_Buff[3],AO_Memcpy_Buff[2],AO_Memcpy_Buff[1],AO_Memcpy_Buff[0]);

		Board_Check_Result_Buff[RTU_Result_Buf_Num_IIC_Current +  (i-1)*4+0 ]=AO_Memcpy_Buff[3];		//RTU发送数据
		Board_Check_Result_Buff[RTU_Result_Buf_Num_IIC_Current +  (i-1)*4+1 ]=AO_Memcpy_Buff[2];		//RTU发送数据
		Board_Check_Result_Buff[RTU_Result_Buf_Num_IIC_Current +  (i-1)*4+2 ]=AO_Memcpy_Buff[1];		//RTU发送数据
		Board_Check_Result_Buff[RTU_Result_Buf_Num_IIC_Current +  (i-1)*4+3 ]=AO_Memcpy_Buff[0];		//RTU发送数据
		
		
		if(AO_5_Current_Check_Range[0]<current_ma && current_ma<AO_5_Current_Check_Range[1])
		{
			AO_5_Current_Check_Result[i]=1;
//			Board_Check_Result_Buff[i+RTU_Result_Buf_Num_IIC_Current-1]=1;	//RTU发送数据
		}
		else
		{
			AO_5_Current_Check_Result[i]=0;
//			Board_Check_Result_Buff[i+RTU_Result_Buf_Num_IIC_Current-1]=0;	//RTU发送数据
		}
		printf("AO_5_Current %d = %f ma\r\n",i,current_ma);		
		printf("AD_INT%d = %d \r\n",i,ADC_ConvertedValue[i-1]);	
		if(AO_6_Current_ADC_Range[0]<ADC_ConvertedValue[i-1] && ADC_ConvertedValue[i-1]<AO_6_Current_ADC_Range[1])
		{
			AO_6_Current_ADC_Check_Result[i]=1;	
			Board_Check_Result_Buff[i+RTU_Result_Buf_Num_ADC-1]=1;	//RTU发送数据
		}
		else
		{
			AO_6_Current_ADC_Check_Result[i]=0;	
			Board_Check_Result_Buff[i+RTU_Result_Buf_Num_ADC-1]=0;	//RTU发送数据
		}
		printf("Current_ADC_Result %d : = %d \r\n",i,AO_6_Current_ADC_Check_Result[i]);
		AO_4_TPC116S1_Set_DAC_CLR(i);		//AO板，测试项目4,被测板上 TPC116S1，输出DAC  清零 
	}
	//*********** 节点 输出结果  ************
	for(i=1;i<5;i++)
	{
		if(AO_5_Current_Check_Result[i]==1 && AO_6_Current_ADC_Check_Result[i]==1)
		{
			AO_456_Current_Check_OK_Flag=1;	//	电流检测结果
		}
		else
		{
			AO_456_Current_Check_OK_Flag=0;	//	电流检测结果
			break;
		}
	}	
}
//************************  AO初始化所有   ************************
void AO_Board_Init_ALL(void)//AO初始化所有
{
	AT24CXX_Init();			//Epprom初始化
	AO_3_LED_GPIO_Init();	//测试项目3，4路LED,初始化引脚
	TPC116S1_GPIO_Init();	//测试项目4，spi DAC，初始化引脚
	AO_5_SGM58200_Init();	//测试项目5，被测板上的，SGM58200，初始化
}

//************************  AO板检测所有   ************************
float AO_5_Current;
void AO_Board_Check(void)//AO板检测所有
{
	AO_1_Short_Check();		//AO板，测试项目1，短路测试，3V3、5V、24V
	if(Board_Check_Short_Flag==0)//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
	{
		switch(Borad_Single_Check_Type)
		{
			case 0:// 单独测试 类型，正常测试 
				AO_2_Epprom_Check();	//AO板，测试项目2，EEPROM 读写检测
				AO_5_SGM58200_Init();	//AI板，测试项目5，被测板上的，SGM58200，初始化
				AO_456_Current_AND_ADC_Check();	//测试项目4、5、6，SPI设置电流，IIC电流检测、ADC检测
				Board_Check_Final_Result=Board_Check_Final_Result & AO_1_Power_OK_Flag & AO_2_Epprom_Check_OK_Flag & AO_456_Current_Check_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;
			case ADIO_Single_Check_Power:	// 单独测试 类型，单独电源
				Board_Check_Final_Result=Board_Check_Final_Result & AO_1_Power_OK_Flag ;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;
			case ADIO_Single_Check_EPPROM:// 单独测试 类型，单独EPPROM
				AO_2_Epprom_Check();	//AO板，测试项目2，EEPROM 读写检测
				Board_Check_Final_Result=Board_Check_Final_Result & AO_1_Power_OK_Flag & AO_2_Epprom_Check_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;	
			case ADIO_Single_Check_Current:// 单独测试 类型，单独EPPROM
				AO_5_SGM58200_Init();	//AI板，测试项目5，被测板上的，SGM58200，初始化
				AO_456_Current_AND_ADC_Check();	//测试项目4、5、6，SPI设置电流，IIC电流检测、ADC检测
				Board_Check_Final_Result=Board_Check_Final_Result & AO_1_Power_OK_Flag & AO_456_Current_Check_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;			
		}
	}
	Board_Check_Result_Buff[RTU_Result_Buf_Num_Final_Result]=Board_Check_Final_Result;	//最终洁检测结果
}
void AO_Check_Reset(void)	//AO板，测试项目复位
{
	Power_Supply_3V3_EN=0;	//3V3对外供电，继电器开关
	Power_Supply_5V_EN=0;	//5V对外供电，继电器开关
	Power_Supply_24V_EN=0;	//24V对外供电，继电器开关
	AO_1_3V3_OK_Flag=0;		//3V3，短路检测标志位，0;默认 ；1：好的 ； 2：不好
	AO_1_5V_OK_Flag=0;		//5V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
	AO_1_24V_OK_Flag=0;		//24V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
	AO_1_Power_OK_Flag=0;	//短路检测OK，0;默认 ；1：好的 ；
	AO_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
	AO_456_Current_Check_OK_Flag=0;	//	电流检测结果
	Board_Check_Final_Result=1;	//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
	Board_Check_Short_Flag=0;	//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
}


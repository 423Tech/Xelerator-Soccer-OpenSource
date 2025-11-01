/* 包含头文件 ----------------------------------------------------------------*/
#include "board_AI.h"
#include "board_check.h"
#include "usart/bsp_debug_usart.h"
#include "24cxx.h"
#include "AD5420.h"
#include <stdio.h>
#include <string.h>
extern u8 Board_Check_Result_Buff[Board_Result_Buff_MAX];	//测量板所有数据，反馈结果
//************************  测试项目1，短路检测，3V3、5V、24V   ************************
u8 AI_1_3V3_OK_Flag;	//3V3，短路检测标志位，0;默认 ；1：好的 ； 2：不好
u8 AI_1_5V_OK_Flag;		//5V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
u8 AI_1_24V_OK_Flag;	//24V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
u8 AI_1_Power_OK_Flag;	//短路检测OK，0;默认 ；1：好的 ；
extern u8 Board_Check_Short_Flag;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
void AI_1_Short_Check(void)	//AI板，测试项目1，短路测试，3V3、5V、24V
{
	if(Power_Supply_3V3_Test==1)
	{
		printf("3v3 ok\n");
		AI_1_3V3_OK_Flag=1;
		Board_Check_Result_Buff[4]=1;	//RTU发送数据
		Board_Check_Result_Buff[5]=1;	//RTU发送数据
		Board_Check_Result_Buff[13]=1;	//RTU发送数据
	}
	else
	{
		printf("3v3 error\n");
		AI_1_3V3_OK_Flag=2;
		Board_Check_Result_Buff[4]=1;	//RTU发送数据
		Board_Check_Result_Buff[5]=0;	//RTU发送数据
		Board_Check_Result_Buff[13]=0;	//RTU发送数据
	}
	if(Power_Supply_5V_Test==1)
	{
		printf("5V ok\n");
		AI_1_5V_OK_Flag=1;
		Board_Check_Result_Buff[2]=1;	//RTU发送数据
		Board_Check_Result_Buff[3]=1;	//RTU发送数据
		Board_Check_Result_Buff[11]=1;	//RTU发送数据
	}
	else
	{
		printf("5V error\n");
		AI_1_5V_OK_Flag=2;
		Board_Check_Result_Buff[2]=1;	//RTU发送数据
		Board_Check_Result_Buff[3]=0;	//RTU发送数据
		Board_Check_Result_Buff[11]=0;	//RTU发送数据
	}
	if(Power_Supply_24V_Test==1)
	{
		printf("24V ok\n");
		AI_1_24V_OK_Flag=1;
		Board_Check_Result_Buff[0]=1;	//RTU发送数据
		Board_Check_Result_Buff[1]=1;	//RTU发送数据
		Board_Check_Result_Buff[9]=1;	//RTU发送数据
	}
	else
	{
		printf("24V error\n");
		AI_1_24V_OK_Flag=2;
		Board_Check_Result_Buff[0]=1;	//RTU发送数据
		Board_Check_Result_Buff[1]=0;	//RTU发送数据
		Board_Check_Result_Buff[9]=0;	//RTU发送数据
	}	
	if (AI_1_3V3_OK_Flag==1 && AI_1_5V_OK_Flag==1 && AI_1_24V_OK_Flag==1)
	{
		AI_1_Power_OK_Flag=1;	//短路检测OK，0;默认 ；1：好的 ； 2：不好
		Power_Supply_3V3_EN=1;	//3V3对外供电，继电器开关
		Power_Supply_5V_EN=1;	//5V对外供电，继电器开关
		Power_Supply_24V_EN=1;	//24V对外供电，继电器开关
		Board_Check_Short_Flag=0;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
		HAL_Delay(100);
	}
	else
		Board_Check_Short_Flag=1;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
}
//************************  测试项目2，EEPROM 读写检测   ************************
u8 AI_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
void AI_2_Epprom_Check(void)
{
	u8 AI_2_Epprom_Check_Res;
	AI_2_Epprom_Check_Res=Epprom_Check();
	if(AI_2_Epprom_Check_Res==0)
	{
		AI_2_Epprom_Check_OK_Flag=1;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
		Board_Check_Result_Buff[15]=1;	//RTU发送数据
	}
	else
	{
		AI_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
		Board_Check_Result_Buff[15]=0;	//RTU发送数据
	}	
}
//************************  测试项目3，8路LED点亮   ************************
void AI_3_LED_GPIO_Init(void)	//测试项目3，8路LED,初始化引脚
{
	GPIO_InitTypeDef GPIO_InitStruct;
	__HAL_RCC_GPIOF_CLK_ENABLE();
	__HAL_RCC_GPIOG_CLK_ENABLE();
	__HAL_RCC_GPIOE_CLK_ENABLE();
//**************  输出  **************	 
	GPIO_InitStruct.Pin = GPIO_PIN_9|GPIO_PIN_8|GPIO_PIN_7;	//1、2、3
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull=GPIO_PULLDOWN;        
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOE, &GPIO_InitStruct);

	GPIO_InitStruct.Pin = GPIO_PIN_1|GPIO_PIN_0;	//4、5
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull=GPIO_PULLDOWN;        
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOG, &GPIO_InitStruct);
	
	GPIO_InitStruct.Pin = GPIO_PIN_15|GPIO_PIN_14|GPIO_PIN_13;	//6、7、8
	GPIO_InitStruct.Mode = GPIO_MODE_OUTPUT_PP;
	GPIO_InitStruct.Pull=GPIO_PULLDOWN;       
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOF, &GPIO_InitStruct);
}
void AI_3_LED_Set_All(u8 state)	////测试项目3，8路LED,全部控制 ,1:亮 ；0：灭
{
	if(state==1)
	{
		AI_3_LED_Channel_1=1;
		AI_3_LED_Channel_2=1;
		AI_3_LED_Channel_3=1;
		AI_3_LED_Channel_4=1;
		AI_3_LED_Channel_5=1;
		AI_3_LED_Channel_6=1;
		AI_3_LED_Channel_7=1;
		AI_3_LED_Channel_8=1;
	}
	else if(state==0)
	{
		AI_3_LED_Channel_1=0;
		AI_3_LED_Channel_2=0;
		AI_3_LED_Channel_3=0;
		AI_3_LED_Channel_4=0;
		AI_3_LED_Channel_5=0;
		AI_3_LED_Channel_6=0;
		AI_3_LED_Channel_7=0;
		AI_3_LED_Channel_8=0;	
	}
	
}
void AI_3_LED_Set_Channel(u8 ch,u8 state)	//测试项目3，8路LED,,单个LED控制,ch:通道1~8 ； state,1亮 ； 0：灭
{
	switch(ch)
	{
		case 1:AI_3_LED_Channel_1=state;break;
		case 2:AI_3_LED_Channel_2=state;break;
		case 3:AI_3_LED_Channel_3=state;break;
		case 4:AI_3_LED_Channel_4=state;break;
		case 5:AI_3_LED_Channel_5=state;break;
		case 6:AI_3_LED_Channel_6=state;break;
		case 7:AI_3_LED_Channel_7=state;break;
		case 8:AI_3_LED_Channel_8=state;break;
	}
}

void AI_3_LED_Check(u8 ch)	//测试项目3，8路LED,检测
{
	if(ch==0)
	{
		AI_3_LED_Set_All(0);	//首先，全部灭
	}
	else
	{
		AI_3_LED_Set_Channel(ch,1);	//单个LED控制,ch:通道1~8 ； state,1亮 ； 0：灭
	}
}
//************************  测试项目4，8路电流输出   ************************
u8 AI_4_Current_Out_Data_Buf[9];
void AI_4_Current_Out_Channel(u8 ch)	//AI板，测试项目4，单通道 电流输出
{
	u8 i;
	for(i=1;i<9;i++)	//清空数据数组
		AI_4_Current_Out_Data_Buf[i]=0x00;
	
	AI_4_Current_Out_Data_Buf[ch]=0x80;//配置通道 ch ，高位 为 80，实际 电流大小数据为 0x80 0x00
	for(i=8;i>0;i--)
	{
		WriteToAD5420_REG_DATA(AI_4_Current_Out_Data_Buf[i],0x00,AD5420_DATA_REG_ADDR,1);HAL_Delay(10);	//数据寄存器 
	}
	HAL_Delay(100);
}
//************************  测试项目4，8路电流输出,清零   ************************
void AI_4_Current_Out_CLR(void)	//AI板，测试项目4，8路电流输出,清零
{
	u8 i;
	for(i=8;i>0;i--)
	{
		WriteToAD5420_REG_DATA(0x00,0x00,AD5420_DATA_REG_ADDR,1);HAL_Delay(10);	//数据寄存器 
	}
	HAL_Delay(100);
}

//************************  测试项目5，被测板上的，SGM58200，初始化   ************************
void AI_5_SGM58200_Init(void)	//AI板，测试项目5，被测板上的，SGM58200，初始化
{
	IIC_Init(&IIC1);		//初始化，对应IIC
	sgm_write_config(&IIC1);//配置 SGM58200
	IIC_Init(&IIC2);		//初始化，对应IIC
	sgm_write_config(&IIC2);//配置 SGM58200	
	HAL_Delay(100);
}
//************************  测试项目5，读SGM58200数据   ************************
float AI_5_Current_Read(u8 ch)	//AI板，测试项目5，读SGM58200数据
{
	float current_ma=0;
	switch(ch)
	{
		case 1:current_ma=IIC_readAI(&IIC1);break;
		case 2:current_ma=IIC_readAI(&IIC2);break;	
//		case 3:current_ma=IIC_readAI(&IIC1);break;
//		case 4:current_ma=IIC_readAI(&IIC2);break;	
//		case 5:current_ma=IIC_readAI(&IIC1);break;
//		case 6:current_ma=IIC_readAI(&IIC2);break;	
//		case 7:current_ma=IIC_readAI(&IIC1);break;
//		case 8:current_ma=IIC_readAI(&IIC2);break;			
	}
	return current_ma;
}
//************************  测试项目4、5，循环检测8路电流值   ************************
float AI_5_Current_Check_Range[2]={10,14};	//标准电流值
u8 AI_5_Current_Check_Result[9];			//电流值检测结果，1：好的
u8 AI_45_Current_Check_OK_Flag;				//	电流检测结果

float AI_5_Current_Read_Value_Buff[9];	//读SGM58200数据，保存数组
u8 AI_Memcpy_Buff[4];	//复制float 到 数组

void AI_45_Current_Check(void)
{
	u8 i;
	float current_ma=0;
	for(i=1;i<9;i++)
	{
		AI_4_Current_Out_Channel(i);	//AI板，测试项目4，单通道 电流输出
		current_ma=AI_5_Current_Read(i);//AI板，测试项目5，读SGM58200数据
		
		AI_5_Current_Read_Value_Buff[i]=current_ma;	//读SGM58200数据，保存数组

		memcpy(AI_Memcpy_Buff,&current_ma,4);
		printf("Current_float = 0x%x%x%x%x\r\n",AI_Memcpy_Buff[3],AI_Memcpy_Buff[2],AI_Memcpy_Buff[1],AI_Memcpy_Buff[0]);
		
		Board_Check_Result_Buff[RTU_Result_Buf_Num_IIC_Current +  (i-1)*4+0 ]=AI_Memcpy_Buff[3];		//RTU发送数据
		Board_Check_Result_Buff[RTU_Result_Buf_Num_IIC_Current +  (i-1)*4+1 ]=AI_Memcpy_Buff[2];		//RTU发送数据
		Board_Check_Result_Buff[RTU_Result_Buf_Num_IIC_Current +  (i-1)*4+2 ]=AI_Memcpy_Buff[1];		//RTU发送数据
		Board_Check_Result_Buff[RTU_Result_Buf_Num_IIC_Current +  (i-1)*4+3 ]=AI_Memcpy_Buff[0];		//RTU发送数据
		
		if(AI_5_Current_Check_Range[0]<current_ma && current_ma<AI_5_Current_Check_Range[1])
		{
			AI_5_Current_Check_Result[i]=1;
//			Board_Check_Result_Buff[i+RTU_Result_Buf_Num_IIC_Current-1]=1;	//RTU发送数据
		}
//		else
//		{
//			Board_Check_Result_Buff[i+RTU_Result_Buf_Num_IIC_Current-1]=0;	//RTU发送数据
//		}
		printf("AI_5_Current %d = %f ma\r\n",i,current_ma);
	}
	for(i=1;i<9;i++)
	{
		if(AI_5_Current_Check_Result[i]==1)
			AI_45_Current_Check_OK_Flag=1;				//	电流检测结果
		else
		{
			AI_45_Current_Check_OK_Flag=0;				//	电流检测结果
			break;
		}
	}		
}


//************************  测试项目6，正负15V电压检测 引脚初始化   ************************
void AI_6_15V_GPIO_Init(void)	//AI板，正负15V电压检测 引脚初始化
{
	GPIO_InitTypeDef GPIO_InitStruct;
	__HAL_RCC_GPIOE_CLK_ENABLE();
//**************  输入	**************
	GPIO_InitStruct.Pin = GPIO_PIN_2|GPIO_PIN_3;//15V+,15V-
	GPIO_InitStruct.Mode = GPIO_MODE_INPUT;
	GPIO_InitStruct.Pull = GPIO_NOPULL;
	GPIO_InitStruct.Speed = GPIO_SPEED_FREQ_HIGH;
	HAL_GPIO_Init(GPIOE, &GPIO_InitStruct); 
}
//************************  测试项目6，正负15V电压检测   ************************
u8 AI_6_15V_Test_A_OK_Flag;//+15V检测OK标志，默认0 ；1：好 ； 2：不好 
u8 AI_6_15V_Test_B_OK_Flag;//-15V检测OK标志，默认0 ；1：好 ； 2：不好 
void AI_6_15V_Test(void)	//AI板，测试项目6，正负15V电压检测
{
	if(AI_6_15V_Test_A==1)
	{
		AI_6_15V_Test_A_OK_Flag=1;//+15V检测OK标志，默认0 ；1：好 ； 2：不好 	
		Board_Check_Result_Buff[6]=1;	//RTU发送数据
	}
	else
	{
		AI_6_15V_Test_A_OK_Flag=0;//+15V检测OK标志，默认0 ；1：好 ； 2：不好 	
		Board_Check_Result_Buff[6]=0;	//RTU发送数据
	}

	if(AI_6_15V_Test_B==1)
	{
		AI_6_15V_Test_B_OK_Flag=1;//-15V检测OK标志，默认0 ；1：好 ； 2：不好 	
		Board_Check_Result_Buff[7]=1;	//RTU发送数据
	}
	else
	{
		Board_Check_Result_Buff[7]=0;	//RTU发送数据
		AI_6_15V_Test_B_OK_Flag=0;//-15V检测OK标志，默认0 ；1：好 ； 2：不好 	
	}
	printf("A:%d ; B:%d\n",AI_6_15V_Test_A_OK_Flag,AI_6_15V_Test_B_OK_Flag);	
}
//************************  AI初始化所有   ************************
void AI_Board_Init_ALL(void)//AI初始化所有
{
	AT24CXX_Init();			//Epprom初始化
	AD5420_GPIO_Init();		//AD5420 IO初始化
	AD5420_Conf_Init(); 	//AD5420 模式配置
	AI_3_LED_GPIO_Init();	//测试项目3，8路LED,初始化引脚
	AI_5_SGM58200_Init();	//AI板，测试项目5，被测板上的，SGM58200，初始化
	AI_6_15V_GPIO_Init();	//AI板，测试项目6，正负15V电压检测 引脚初始化 	
}
//************************  AI板检测所有   ************************
float AI_5_Current;//检测电流，读SGM58200数据
void AI_Board_Check(void)//AI板检测所有
{
	AI_1_Short_Check();			//AI板，测试项目1，短路测试，3V3、5V、24V
	if(Board_Check_Short_Flag==0)//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
	{
		switch(Borad_Single_Check_Type)
		{
			case 0:// 单独测试 类型，正常测试 
				AI_2_Epprom_Check();	//AO板，测试项目2，EEPROM 读写检测
				AI_45_Current_Check();	//AI板，测试项目5，被测板上的，SGM58200，初始化
				AI_6_15V_Test();	//测试项目4、5、6，SPI设置电流，IIC电流检测、ADC检测
				Board_Check_Final_Result=Board_Check_Final_Result & AI_1_Power_OK_Flag & AI_2_Epprom_Check_OK_Flag & AI_45_Current_Check_OK_Flag & AI_6_15V_Test_B_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;
			case ADIO_Single_Check_Power:	// 单独测试 类型，单独电源
				AI_6_15V_Test();	//测试项目4、5、6，SPI设置电流，IIC电流检测、ADC检测
				Board_Check_Final_Result=Board_Check_Final_Result & AI_1_Power_OK_Flag & AI_6_15V_Test_B_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;
			case ADIO_Single_Check_EPPROM:// 单独测试 类型，单独EPPROM
				AI_2_Epprom_Check();	//AO板，测试项目2，EEPROM 读写检测
				Board_Check_Final_Result=Board_Check_Final_Result & AI_1_Power_OK_Flag & AI_2_Epprom_Check_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;	
			case ADIO_Single_Check_Current:// 单独测试 类型，单独EPPROM
				AI_45_Current_Check();	//AI板，测试项目5，被测板上的，SGM58200，初始化
				Board_Check_Final_Result=Board_Check_Final_Result & AI_1_Power_OK_Flag & AI_45_Current_Check_OK_Flag;//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
				break;			
		}
	}
	Board_Check_Result_Buff[RTU_Result_Buf_Num_Final_Result]=Board_Check_Final_Result;	//最终洁检测结果

}
void AI_Check_Reset(void)	//AI板，测试项目复位
{
	AI_4_Current_Out_CLR();	//AI板，测试项目4，8路电流输出,清零
	Power_Supply_3V3_EN=0;	//3V3对外供电，继电器开关
	Power_Supply_5V_EN=0;	//5V对外供电，继电器开关
	Power_Supply_24V_EN=0;	//24V对外供电，继电器开关
	AI_1_3V3_OK_Flag=0;		//3V3，短路检测标志位，0;默认 ；1：好的 ； 2：不好
	AI_1_5V_OK_Flag=0;		//5V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
	AI_1_24V_OK_Flag=0;		//24V ，短路检测标志位，0;默认 ；1：好的 ； 2：不好
	AI_1_Power_OK_Flag=0;	//短路检测OK，0;默认 ；1：好的 ；
	AI_2_Epprom_Check_OK_Flag=0;//EEPROM检测结果标志位，0：默认 ； 1：好 ； 2：不好 
	AI_45_Current_Check_OK_Flag=0;				//	电流检测结果
	AI_6_15V_Test_A_OK_Flag=0;//+15V检测OK标志，默认0 ；1：好 ； 2：不好 
	AI_6_15V_Test_B_OK_Flag=0;//-15V检测OK标志，默认0 ；1：好 ； 2：不好 
	Board_Check_Final_Result=1;	//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
	Board_Check_Short_Flag=0;	//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
}


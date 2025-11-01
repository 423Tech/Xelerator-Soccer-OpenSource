/* 包含头文件 ----------------------------------------------------------------*/
#include "board_AI.h"
#include "board_AO.h"
#include "board_DI.h"
#include "board_DO.h"
#include "usart/bsp_debug_usart.h"
#include "24cxx.h"
#include "board_check.h"
#include "myiic.h"
#include "74HC595.h"
#include "string.h"
u8 Board_Check_Type = 0;//所选的被测板 0：默认（无效）1：AI ; 2：AO ; 3：DI ; 4：DO ;

//*******************  RS485参数  *******************
extern u8 RS485_RX_Buff[RS485_RX_MAX]; 	// 接收缓冲区
extern u16 RS485_RX_Count;                  	// 已接收到的字节数
extern u8 RS485_RX_New_Frame_flag;   	// 帧标志：1：一个新的数据帧  0：无数据帧
u8 RS485_RTU_TX_Buff[RS485_RTU_TX_MAX]; 	// 发送缓冲区
u8 RS485_RTU_TX_ON_1[2]={0x00,0x01};	//调理卡，发送开启指令，专用的数组，0x0001
u8 RS485_RTU_TX_ON_2[2]={0x00,0x02};	//调理卡，发送LED就绪指令，专用的数组，0x0001
u8 RS485_RTU_TX_Message[10]={0x00,0x02,0x01,0x00,0x24,0x01,0x00,0x00};//ADIO 卡件调理卡上电完成，ADIO 信息  8位
u8 RS485_RTU_RX_Function;	// RS485_RTU 接收数据分析 ，功能码
u8 RS485_RTU_RX_Len;		// RS485_RTU 接收数据分析 ，数据位
u8 RS485_RTU_RX_Data[20];	// RS485_RTU 接收数据分析 ，数据段
u8 RS485_RTU_Buff_New_Event_Flag;// RS485_RTU 新的事件 标志位
u8 RS485_RTU_Board_Check_Others_Start_Flag;	// RS485_RTU 传达的开始除了LED其他检测，标志位 0:默认；1：开始检测 ；2：检测完成
u8 RS485_RTU_Board_Check_LED_Start_Flag;	// 开始LED检测，标志位，标志位 0:默认；1：开始检测 ；2：检测完成
u8 Board_Check_Result_Buff[Board_Result_Buff_MAX];	//测量板所有数据，反馈结果
u8 Board_Check_Final_Result;	//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
u16 Borad_Single_Check_Type;	// 单独测试 类型 
u8 Board_Check_Short_Flag;		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
//**************************************  RS485 RTU 数据发送  **************************************
//帧头	目标地址码	源地址码		功能码	  数据位             数据段 		帧尾
//0xAA	1字节       1字节        1字节     1字节（2~126) 	 DATA(Len) 	    0x55
void RS485_RTU_TX_Data(u8 aim_address,u8 function,u8 len,u8 *pData)	//目标地址，功能码，数据段内容
{
	u8 rtu_buff[100];
	rtu_buff[0]=RS485_RTU_FH;			//帧头
	rtu_buff[1]=aim_address;			//目标地址码
	rtu_buff[2]=RS485_RTU_ADDRES_MINE;	//源地址码	
	rtu_buff[3]=function;				//功能码	
	rtu_buff[4]=len;					//数据位(多少位)
	memcpy(&rtu_buff[5],pData,len);		//数据段(内容)
	rtu_buff[5+len]=RS485_RTU_FE; 		//帧尾
	RS485_TX_EN;		//485发送使能
	RS485_Delay(10000);		//稍作延时，注意延时的长短根据波特率来定，波特率越小，延时应该越长
	HAL_UART_Transmit(&husart_RS485,rtu_buff,len+6,1000);	
	RS485_RX_EN;  		//485接收使能
	RS485_Delay(100); 		//稍作延时，注意延时的长短根据波特率来定，波特率越小，延时应该越长
}

void RS485_RTU_Buff_CLR(void)	//清空RTU发送buff
{
	u16 k;
	for(k=0;k<RS485_RTU_TX_MAX;k++){RS485_RTU_TX_Buff[k] = 0x00;}
	RS485_RX_Count = 0; 
}
	// 
//*******************  RS485 RTU 数据解析，解析出  功能码，数据位，数据段  ******************
void RS485_RTU_Buff_Analysis(void)
{
	u8 i;
	if(RS485_RX_New_Frame_flag==1)  	// 新的帧标志：1：一个新的数据帧  0：无数据帧
	{
		if(RS485_RX_Buff[0]==0XAA && RS485_RX_Buff[1]==RS485_RTU_ADDRES_MINE)	//帧头对，并且 ，是跟我说话
		{
			RS485_RTU_RX_Function=RS485_RX_Buff[3];	// RS485_RTU 接收数据分析 ，功能码
			RS485_RTU_RX_Len=RS485_RX_Buff[4];		// RS485_RTU 接收数据分析 ，数据位
			for(i=0;i<RS485_RTU_RX_Len;i++)
				RS485_RTU_RX_Data[i]=RS485_RX_Buff[5+i];					// RS485_RTU 接收数据分析 ，数据段
			
//			RS485_Send_Data(RS485_RX_Buff,RS485_RX_Count);
			RS485_RX_Buff_CLR();//清除接收buff
			RS485_RX_New_Frame_flag=0;	// 新的帧标志：1：一个新的数据帧  0：无数据帧
			RS485_RTU_Buff_New_Event_Flag=1;// RS485_RTU 新的事件 标志位
		}
		else//有帧头，但是目标地址不是我
		{
			RS485_RX_Buff_CLR();//清除接收buff
			RS485_RX_New_Frame_flag=0;	// 新的帧标志：1：一个新的数据帧  0：无数据帧
		}
	}
}
u8 RS485_RTU_LED_Check_CH;		//算力卡通过 RS485发下来的 亮灯序号
//*******************  RS485 RTU 数据处理(事件处理)  ******************
void RS485_RTU_Buff_Deal(void)
{
	if(RS485_RTU_Buff_New_Event_Flag==1)// RS485_RTU 新的事件 标志位
	{
		if(RS485_RTU_RX_Len==2)
		{
			if( Board_AI_A<=RS485_RTU_RX_Function && RS485_RTU_RX_Function<=Board_DO)	//如果功能码为 卡件类型（这里要区分LED功能码） 
			{
				switch(RS485_RTU_RX_Data[1])
				{
					case 0x01:	//选择 AI 卡件测试 1,做好准备
						Board_Check_Type=RS485_RTU_RX_Function;	//对 功能码 进行 分别操作
						RS485_RTU_TX_Buff[0]=0x00;RS485_RTU_TX_Buff[1]=0x01;
						RS485_RTU_TX_Data(0X01,RS485_RTU_RX_Function,2,RS485_RTU_TX_Buff);//AI 准备就绪
						RS485_RTU_Buff_CLR();
						break;
					case 0x02:	//AI 板卡已放到位可以测试；
						Board_Init();//对应板子初始化
						RS485_RTU_Buff_CLR();
						Board_Check_Result_Buff_CLR();				//清除 测量板所有数据，反馈结果
						Board_Check_Final_Result=1;	//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
						RS485_RTU_Board_Check_Others_Start_Flag=1;	// RS485_RTU 传达的开始除了LED其他检测，标志位 0:默认；1：开始检测 ；2：检测完成
						RS485_RTU_Board_Check_LED_Start_Flag=0;				// 开始LED检测，标志位	 0:默认；1：开始检测 ；2：检测完成
						break;
					case ADIO_Single_Check_Power:case ADIO_Single_Check_EPPROM:case ADIO_Single_Check_Current:case ADIO_Single_Check_LED_Shine:	//单独测试（单独测灯也要先测其他功能，因为不论怎样都要侧电源短路）
						Board_Init();//对应板子初始化
						Borad_Single_Check_Type=RS485_RTU_RX_Data[1];	
						RS485_RTU_Board_Check_Others_Start_Flag=1;	// RS485_RTU 传达的开始除了LED其他检测，标志位 0:默认；1：开始检测 ；2：检测完成
						RS485_RTU_Buff_CLR();
						break;
				}			
			}
			else if(RS485_RTU_RX_Function == Board_Check_LED)
			{
				RS485_RTU_Board_Check_LED_Start_Flag=1;				// 开始LED检测，标志位	 0:默认；1：开始检测 ；2：检测完成
				RS485_RTU_LED_Check_CH=RS485_RTU_RX_Data[1];		//算力卡通过 RS485发下来的 亮灯序号
				Board_LED_Check();			//对应板子 LED点亮、测量	
				RS485_RTU_Buff_CLR();
			}
		}
		RS485_RTU_Buff_New_Event_Flag=0;// RS485_RTU 新的事件 标志位
	}
}
//*******************  对应板子初始化  ******************
void Board_Init(void)
{
	switch(Board_Check_Type)
	{
		case Board_AI_A:case Board_AI_B :
			AI_Board_Init_ALL();	//AI卡，初始化所有
			break;
		case Board_AO_A:case Board_AO_B:
			AO_Board_Init_ALL();	//AO卡，初始化所有
			break;
		case Board_DI:
			DI_Board_Init_ALL();	//DI卡，初始化所有
			break;
		case Board_DO:
			DO_Board_Init_ALL();	//DO卡，初始化所有
			break;		
	}
	HAL_Delay(100);
}

//*******************  对应板子 测量,除了LED的功能  ******************
void Board_Check_Others(void)
{
	if(RS485_RTU_Board_Check_Others_Start_Flag==1)// RS485_RTU 传达的开始除了LED其他检测，标志位 0:默认；1：开始检测 ；2：检测完成
	{
		switch(Board_Check_Type)
		{
			case Board_AI_A:case Board_AI_B :
				AI_Board_Check();	//AI卡，检测所有,除了LED
				break;
			case Board_AO_A:case Board_AO_B:
				AO_Board_Check();	//AO卡，检测所有,除了LED
				break;
			case Board_DI:
				DI_Board_Check();	//DI卡，检测所有,除了LED
				break;
			case Board_DO:
				DO_Board_Check();	//DO卡，检测所有,除了LED
				break;	
		}
		HAL_Delay(100);
		
		if(Board_Check_Short_Flag==0)		//短路标志，如果存在短路，就不用测LED了，1：短路 ；0：不短路
		{
			switch(Borad_Single_Check_Type)
			{
				case 0:case ADIO_Single_Check_LED_Shine:		// 单独测试 类型，正常测试 和 单独检测 LED
					RS485_RTU_TX_Data(0X01,Board_NO_SHORT,2,RS485_RTU_TX_ON_1);//上报给 算力卡 ：不短路，（灯测准备就绪）其他都测完了
					break;
				case ADIO_Single_Check_Power:case ADIO_Single_Check_EPPROM:case ADIO_Single_Check_Current:	//单独检测，非 LED
					RS485_RTU_Board_Check_Result_Send();//发送检测结果
					break;
			}
		}
		else //短路
			RS485_RTU_Board_Check_Result_Send();//发送检测结果
			
		RS485_RTU_Board_Check_Others_Start_Flag=2;	// RS485_RTU 传达的开始除了LED其他检测，标志位 0:默认；1：开始检测 ；2：检测完成
	}
}

//*******************  对应板子 LED点亮、测量  ******************
u8 Board_LED_Checked_Sum;	//记录 检测过的 LED数量 
u8 Board_LED_Set_Num;		//传递参数，哪一个卡，几个灯
void Board_LED_Check(void)
{
	u8 buff[2]={0x00,0x00};
	if(RS485_RTU_Board_Check_LED_Start_Flag==1)	// 开始LED检测，标志位 0:默认；1：开始检测 ；2：检测完成
	{
		switch(Board_Check_Type)
		{
			case Board_AI_A:case Board_AI_B :
				AI_3_LED_Check(RS485_RTU_LED_Check_CH);	//AI卡，检测单个通道LED
				Board_LED_Set_Num=AI_LED_Num;	//传递参数，哪一个卡，几个灯
				break;
			case Board_AO_A:case Board_AO_B:
				AO_3_LED_Check(RS485_RTU_LED_Check_CH);	//AO卡，检测单个通道LED
				Board_LED_Set_Num=AO_LED_Num;	//传递参数，哪一个卡，几个灯
				break;
			case Board_DI:
				DI_3456_LED_ON_Check_Channel(RS485_RTU_LED_Check_CH);	//DI卡，检测单个通道LED
				Board_LED_Set_Num=DI_LED_Num;		//传递参数，哪一个卡，几个灯
				break;
			case Board_DO:
				DO_34_LED_ON_Check_Channel(RS485_RTU_LED_Check_CH);		//DO卡，检测单个通道LED
				Board_LED_Set_Num=DO_LED_Num;		//传递参数，哪一个卡，几个灯
				break;	
		}
		buff[1]=RS485_RTU_LED_Check_CH;
		HAL_Delay(300);
		RS485_RTU_TX_Data(0X01,Board_Check_LED,2,buff);	//上报给 算力卡 ：单独通道灯 点亮、测试完成
		if(RS485_RTU_LED_Check_CH==0)
			Board_LED_Checked_Sum++;					//记录 检测过的 LED数量 ,这里逻辑是这样的：算力卡先开灯，再关灯，记录关灯次数
		RS485_RTU_Board_Check_LED_Start_Flag=0;		// 开始LED检测，标志位 0:默认；1：开始检测 ；2：检测完成
		if(Board_LED_Checked_Sum==Board_LED_Set_Num)	//所有的灯都检测完了一遍
		{
			RS485_RTU_Board_Check_LED_Start_Flag=2;		// 开始LED检测，标志位 0:默认；1：开始检测 ；2：检测完成
			Board_LED_Checked_Sum=0;					//记录 检测过的 LED数量 
			Board_Check_LED_Result_Deal();				//特别地：DI\DO卡，LED不单点亮，还有点亮后的 断线、通道检测，所以要跟其他的结果再处理一次
			RS485_RTU_Board_Check_Result_Send();		//发送检测结果
		}
	}
}
//*******************  特别地：DI\DO卡，LED不单点亮，还有点亮后的 断线、通道检测，所以要跟其他的结果再处理一次  ******************
void Board_Check_LED_Result_Deal(void)
{
	switch(Board_Check_Type)
	{
		case Board_DI:
			DI_Board_Check_LED_Result_Deal();		//DI板 处理所有结果，判断是否全部合格
			break;
		case Board_DO:
			DO_Board_Check_LED_Result_Deal();		//DO卡，处理所有结果，判断是否全部合格
			break;	
	}

}
//*******************  对应板子 检测动作复位  ******************
void Board_Check_Reset(void)
{
	switch(Board_Check_Type)
	{
		case Board_AI_A:case Board_AI_B :
			AI_Check_Reset();		//AI板，测试项目复位
			break;
		case Board_AO_A:case Board_AO_B:
			AO_Check_Reset();		//AI板，测试项目复位
			break;
		case Board_DI:
			DI_Check_Reset();		//DI板，测试项目复位
			break;
		case Board_DO:
			DO_Check_Reset();		//DO板，测试项目复位
			break;	
	}
}
void Board_Check_Result_Buff_CLR(void)//清除 测量板所有数据，反馈结果
{
	u16 k;
	for(k=0;k<Board_Result_Buff_MAX;k++)
		Board_Check_Result_Buff[k]=0xFF;	//测量板所有数据，反馈结果
	Board_LED_Checked_Sum=0;
}
	
void RS485_RTU_Board_Check_Result_Send(void)//发送检测结果
{
	HAL_Delay(200);
	RS485_RTU_TX_Data(0X01,Board_Check_Type,Board_Result_Number,Board_Check_Result_Buff);//发送检测结果
	Board_Check_Result_Buff_CLR();				//清除 测量板所有数据，反馈结果	
	RS485_RTU_Board_Check_Others_Start_Flag=0;	// RS485_RTU 传达的开始除了LED其他检测，标志位 0:默认；1：开始检测 ；2：检测完成
	RS485_RTU_Board_Check_LED_Start_Flag=0;		// 开始LED检测，标志位 0:默认；1：开始检测 ；2：检测完成
	Board_Check_Reset();						// 对应板子 检测动作复位
	Board_LED_Checked_Sum=0;					//记录 检测过的 LED数量 
			
}

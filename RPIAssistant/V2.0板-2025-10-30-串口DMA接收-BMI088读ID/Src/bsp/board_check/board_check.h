#ifndef __BOARD_CHECK_H__
#define __BOARD_CHECK_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"
#include "led/bsp_led.h"

// 功能码 卡件类型信息
#define Board_AI_A 	0x02
#define Board_AI_B 	0x03
#define Board_AO_A 	0x04
#define Board_AO_B 	0x05
#define Board_DI 	0x06
#define Board_DO 	0x07

#define Board_Check_LED 	0x0D	//功能码 点亮单个LED
#define Board_NO_SHORT 		0x0C	//功能码 不短路
//ADIO卡 单独测试
#define ADIO_Single_Check_Power 		0x03	//单独检测 ADIO 电源
#define ADIO_Single_Check_EPPROM 		0x04	//单独检测 EPPROM
#define ADIO_Single_Check_LED_Shine 	0x05	//单独检测 LED检测，包含 断线、亮灭等
#define ADIO_Single_Check_Current 		0x06	//单独检测 电流检测

//******************************  RTU 测试结果 数组的第几项，代表的含义  ******************************
#define	RTU_Result_Buf_Num_0		0	//

#define	RTU_Result_Buf_Num_LED_Cut		16	//断线检测（LED从动）


#define	RTU_Result_Buf_Num_IIC_Current		56	//电流输入, I2C ADC读出
#define	RTU_Result_Buf_Num_ADC		88	//输出电流, 模拟量检测
#define	RTU_Result_Buf_Num_Final_Result		93	//最终结果


#define Board_Result_Buff_MAX 	100
#define Board_Result_Number 	94	//需要发送的数据量

#define LED_ON_Delay 200 		//LED流水灯，延时点亮，先延时再点亮

//LED数量 汇总
#define AI_LED_Num  8  		// AO板，待测LED数量 
#define AO_LED_Num  4  		// AO板，待测LED数量 
#define DI_LED_Num  24  		// AO板，待测LED数量 
#define DO_LED_Num  16  		// AO板，待测LED数量 



extern u8 RS485_RTU_TX_ON_1[2];	//调理卡，发送开启指令，专用的数组，0x0001
extern u8 RS485_RTU_TX_ON_2[2];	//调理卡，发送LED就绪指令，专用的数组，0x0001
extern u8 Board_Check_Final_Result;	//最终检测结果，全对，才对，1：全部正确 ； 0 ：错误
extern u16 Borad_Single_Check_Type;	// 单独测试 类型 

void RS485_RTU_TX_Data(u8 aim_address,u8 function,u8 len,u8 *pData);
void RS485_RTU_Buff_CLR(void);	//清空RTU发送buff
void RS485_RTU_Buff_Analysis(void);	// RS485 RTU 数据解析，解析出  功能码，数据位，数据段
void RS485_RTU_Buff_Deal(void);	//RS485 RTU 数据处理(事件处理) 

void Board_Init(void);			//对应板子初始化
void Board_LED_Check(void);		//对应板子 LED点亮、测量

void Board_Check_Others(void);	//对应板子 测量
void Board_Check_Reset(void);	//对应板子 检测动作复位

void Board_Check_LED_Result_Deal(void);		//特别地：DI\DO卡，LED不单点亮，还有点亮后的 断线、通道检测，所以要跟其他的结果再处理一次
void Board_Check_Result_Buff_CLR(void);//清除 测量板所有数据，反馈结果
void RS485_RTU_Board_Check_Result_Send(void);//发送检测结果
#endif  // __BSP_LED_H__



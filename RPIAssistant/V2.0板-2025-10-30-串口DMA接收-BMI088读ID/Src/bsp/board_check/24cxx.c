#include "24cxx.h"
#include "stm32f4xx_hal.h"
#include "myiic.h"
#include "board_check.h"

u16 EE24C64_WRITE_ADDRESS;
u16 EE24C64_READ_ADDRESS;
extern u8 Board_Check_Type;//所选的被测板 0：默认（无效）
void AT24CXX_Init(void)
{
	IIC_Init(&IIC4);//IIC初始化
	if(Board_Check_Type== Board_AI_A | Board_Check_Type== Board_AO_A)//所选的被测板 0：默认（无效）
	{
		EE24C64_WRITE_ADDRESS=	0XA2; 	//A 卡
	}
	else if(Board_Check_Type== Board_AI_B | Board_Check_Type== Board_AO_B)//所选的被测板 0：默认（无效）
	{
		EE24C64_WRITE_ADDRESS=	0XA6 ;	//B 卡
	}
	EE24C64_READ_ADDRESS=	EE24C64_WRITE_ADDRESS|0X01 	;
}
//在AT24CXX指定地址读出一个数据
//ReadAddr:开始读数的地址  
//返回值  :读到的数据
u8 AT24CXX_ReadOneByte(u16 ReadAddr)
{				  
	u8 temp=0;		  	    																 
    IIC_Start(&IIC4);  
	if(EE_TYPE>AT24C16)
	{
		IIC_Send_Byte(&IIC4,EE24C64_WRITE_ADDRESS);	   //发送写命令
		IIC_Wait_Ack(&IIC4);
		IIC_Send_Byte(&IIC4,ReadAddr>>8);//发送高地址	    
	}else IIC_Send_Byte(&IIC4,EE24C64_WRITE_ADDRESS+((ReadAddr/256)<<1));   //发送器件地址0XA0,写数据 	   
	IIC_Wait_Ack(&IIC4); 
    IIC_Send_Byte(&IIC4,ReadAddr%256);   //发送低地址
	IIC_Wait_Ack(&IIC4);	    
	IIC_Start(&IIC4);  	 	   
	IIC_Send_Byte(&IIC4,EE24C64_READ_ADDRESS);           //进入接收模式			   
	IIC_Wait_Ack(&IIC4);	 
    temp=IIC_Read_Byte(&IIC4,0);		   
    IIC_Stop(&IIC4);//产生一个停止条件	    
	return temp;
}
//在AT24CXX指定地址写入一个数据
//WriteAddr  :写入数据的目的地址    
//DataToWrite:要写入的数据
void AT24CXX_WriteOneByte(u16 WriteAddr,u8 DataToWrite)
{				   	  	    																 
    IIC_Start(&IIC4);  
	if(EE_TYPE>AT24C16)
	{
		IIC_Send_Byte(&IIC4,EE24C64_WRITE_ADDRESS);	    //发送写命令
		IIC_Wait_Ack(&IIC4);
		IIC_Send_Byte(&IIC4,WriteAddr>>8);//发送高地址	  
	}else IIC_Send_Byte(&IIC4,EE24C64_WRITE_ADDRESS+((WriteAddr/256)<<1));   //发送器件地址0XA0,写数据 	 
	IIC_Wait_Ack(&IIC4);	   
    IIC_Send_Byte(&IIC4,WriteAddr%256);   //发送低地址
	IIC_Wait_Ack(&IIC4); 	 										  		   
	IIC_Send_Byte(&IIC4,DataToWrite);     //发送字节							   
	IIC_Wait_Ack(&IIC4);  		    	   
    IIC_Stop(&IIC4);//产生一个停止条件 
	HAL_Delay(10);	 
}
//在AT24CXX里面的指定地址开始写入长度为Len的数据
//该函数用于写入16bit或者32bit的数据.
//WriteAddr  :开始写入的地址  
//DataToWrite:数据数组首地址
//Len        :要写入数据的长度2,4
void AT24CXX_WriteLenByte(u16 WriteAddr,u32 DataToWrite,u8 Len)
{  	
	u8 t;
	for(t=0;t<Len;t++)
	{
		AT24CXX_WriteOneByte(WriteAddr+t,(DataToWrite>>(8*t))&0xff);
	}												    
}

//在AT24CXX里面的指定地址开始读出长度为Len的数据
//该函数用于读出16bit或者32bit的数据.
//ReadAddr   :开始读出的地址 
//返回值     :数据
//Len        :要读出数据的长度2,4
u32 AT24CXX_ReadLenByte(u16 ReadAddr,u8 Len)
{  	
	u8 t;
	u32 temp=0;
	for(t=0;t<Len;t++)
	{
		temp<<=8;
		temp+=AT24CXX_ReadOneByte(ReadAddr+Len-t-1); 	 				   
	}
	return temp;												    
}
//在AT24CXX里面的指定地址开始读出指定个数的数据
//ReadAddr :开始读出的地址 对24c02为0~255
//pBuffer  :数据数组首地址
//NumToRead:要读出数据的个数
void AT24CXX_Read(u16 ReadAddr,u8 *pBuffer,u16 NumToRead)
{
	while(NumToRead)
	{
		*pBuffer++=AT24CXX_ReadOneByte(ReadAddr++);	
		NumToRead--;
	}
}  
//在AT24CXX里面的指定地址开始写入指定个数的数据
//WriteAddr :开始写入的地址 对24c02为0~255
//pBuffer   :数据数组首地址
//NumToWrite:要写入数据的个数
void AT24CXX_Write(u16 WriteAddr,u8 *pBuffer,u16 NumToWrite)
{
	while(NumToWrite--)
	{
		AT24CXX_WriteOneByte(WriteAddr,*pBuffer);
		WriteAddr++;
		pBuffer++;
	}
}

//************************  通用 测试项目2，EEPROM 读写检测   ************************
#define Epprom_Check_Start_Address 0000
#define Epprom_Check_Buffer_SIZE 10
u8 Epprom_Check_Send_Buffer[Epprom_Check_Buffer_SIZE];
u8 Epprom_Check_Read_Buffer[Epprom_Check_Buffer_SIZE];	
u16 Epprom_Check_Buffer_Count;//对比 发送和读取 正确的次数
u8 Epprom_Check(void)
{
	u16 i;	
	Epprom_Check_Buffer_Count=0;//对比 发送和读取 正确的次数
	for(i=0;i<Epprom_Check_Buffer_SIZE;i++)
		Epprom_Check_Send_Buffer[i]=i;
	printf("Send Data To EPPROM....\n");
	AT24CXX_Write(Epprom_Check_Start_Address,(u8*)Epprom_Check_Send_Buffer,Epprom_Check_Buffer_SIZE);//发送EEPROM数据	
	AT24CXX_Read(Epprom_Check_Start_Address,Epprom_Check_Read_Buffer,Epprom_Check_Buffer_SIZE);//读取EEPROM数据
	for(i=0;i<Epprom_Check_Buffer_SIZE;i++)
	{
		if(Epprom_Check_Send_Buffer[i]==Epprom_Check_Read_Buffer[i])
			Epprom_Check_Buffer_Count++;
		else
			printf("ERROR!\n");
	}	
	if(Epprom_Check_Buffer_Count!=Epprom_Check_Buffer_SIZE) 
	{
		printf("EPPROM Check Failed!\n");
		return 1;
	}		
	printf("EPPROM Check OK!\n");
	return 0;
}

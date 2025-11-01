#include "system.h"
#include "myiic.h"
#include "led.h"
#include "stm32f4xx_hal.h"

IIC_TypeDef IIC1=
{
	GPIOB,GPIO_PIN_12,//SCL
	GPIOD,GPIO_PIN_11,//SDA
};
//IIC_初始化
void IIC_Init(IIC_TypeDef * IIC)
{
    GPIO_InitTypeDef GPIO_Initure;
    __HAL_RCC_GPIOB_CLK_ENABLE();   
	__HAL_RCC_GPIOD_CLK_ENABLE();       
	
    GPIO_Initure.Pin=IIC->SCL_PIN;
	GPIO_Initure.Pin=IIC->SCL_PIN;
    GPIO_Initure.Mode=GPIO_MODE_OUTPUT_PP;  //推挽输出
    GPIO_Initure.Pull=GPIO_NOPULL;          //上拉
    GPIO_Initure.Speed=GPIO_SPEED_FAST;     //快速
    HAL_GPIO_Init(IIC->SCL_PORT,&GPIO_Initure);	

    GPIO_Initure.Pin=IIC->SDA_PIN;
    GPIO_Initure.Mode=GPIO_MODE_OUTPUT_PP;  //推挽输出
    GPIO_Initure.Pull=GPIO_NOPULL;          //上拉
    GPIO_Initure.Speed=GPIO_SPEED_FAST;     //快速
    HAL_GPIO_Init(IIC->SDA_PORT,&GPIO_Initure);		
    IIC_Stop(IIC);
}
void IIC_SDA_IN(IIC_TypeDef * IIC)
{
	GPIO_InitTypeDef GPIO_Initure;
    GPIO_Initure.Pin=IIC->SDA_PIN;
    GPIO_Initure.Mode=GPIO_MODE_INPUT;  //推挽输出
    GPIO_Initure.Pull=GPIO_PULLUP;          //上拉
    GPIO_Initure.Speed=GPIO_SPEED_FAST;     //快速
    HAL_GPIO_Init(IIC->SDA_PORT,&GPIO_Initure);
}
void IIC_SDA_OUT(IIC_TypeDef * IIC)
{
	GPIO_InitTypeDef GPIO_Initure;
    GPIO_Initure.Pin=IIC->SDA_PIN;
    GPIO_Initure.Mode=GPIO_MODE_OUTPUT_PP;  //推挽输出
//    GPIO_Initure.Pull=GPIO_PULLUP;          //上拉
    GPIO_Initure.Speed=GPIO_SPEED_FAST;     //快速
    HAL_GPIO_Init(IIC->SDA_PORT,&GPIO_Initure);
}





//产生IIC起始信号
u8 IIC_delay=100;
void IIC_Start(IIC_TypeDef * IIC)
{
	IIC_SDA_OUT(IIC);     //sda线输出
	IIC_SDA(1,IIC);
	IIC_SCL(1,IIC);
	My_Delay_us(IIC_delay);
 	IIC_SDA(0,IIC);
	My_Delay_us(IIC_delay);
	IIC_SCL(0,IIC);
	My_Delay_us(IIC_delay);
}	  
//产生IIC停止信号
void IIC_Stop(IIC_TypeDef * IIC)
{
	IIC_SDA_OUT(IIC);//sda线输出
	IIC_SDA(0,IIC);
	IIC_SCL(1,IIC);
 	My_Delay_us(IIC_delay);
	IIC_SDA(1,IIC);//发送I2C总线结束信号
	My_Delay_us(IIC_delay);							   	
}
//等待应答信号到来
//返回值：1，接收应答失败
//        0，接收应答成功
u8 IIC_Wait_Ack(IIC_TypeDef * IIC)
{
	u8 re;
	IIC_SDA_IN(IIC);      //SDA设置为输入  
	IIC_SDA(1,IIC);My_Delay_us(IIC_delay);	   
	IIC_SCL(1,IIC);My_Delay_us(IIC_delay);	 
	if (READ_SDA(IIC))
		re=1;
	else
		re=0;	
	IIC_SCL(0,IIC);//时钟输出0 
	My_Delay_us(IIC_delay);		
	return re;  
} 
//产生ACK应答
void IIC_Ack(IIC_TypeDef * IIC)
{
	IIC_SDA_OUT(IIC);
	IIC_SDA(0,IIC);
	My_Delay_us(IIC_delay);
	IIC_SCL(1,IIC);
	My_Delay_us(IIC_delay);
	IIC_SCL(0,IIC);
	My_Delay_us(IIC_delay);
	IIC_SDA(1,IIC);
}
//不产生ACK应答		    
void IIC_NAck(IIC_TypeDef * IIC)
{
	IIC_SDA_OUT(IIC);
	IIC_SDA(1,IIC);
	My_Delay_us(IIC_delay);
	IIC_SCL(1,IIC);
	My_Delay_us(IIC_delay);
	IIC_SCL(0,IIC);
	My_Delay_us(IIC_delay);
}					 				     
//IIC发送一个字节
//返回从机有无应答
//1，有应答
//0，无应答			  
void IIC_Send_Byte(IIC_TypeDef * IIC,u8 txd)
{                        
    u8 t;   
	IIC_SDA_OUT(IIC); 	    
    for(t=0;t<8;t++)
    {             
		if(txd & 0x80)
			IIC_SDA(1,IIC);
		else
			IIC_SDA(0,IIC);
		My_Delay_us(IIC_delay);   //对TEA5767这三个延时都是必须的
		IIC_SCL(1,IIC);
		My_Delay_us(IIC_delay); 
		IIC_SCL(0,IIC);	
		if(t==7)
			IIC_SDA(1,IIC);
		txd <<= 1;
		My_Delay_us(IIC_delay);
    }	 
} 	    
//读1个字节，ack=1时，发送ACK，ack=0，发送nACK   
u8 IIC_Read_Byte(IIC_TypeDef * IIC,unsigned char ack)
{
	unsigned char i,receive=0;
	IIC_SDA_IN(IIC);//SDA设置为输入
    for(i=0;i<8;i++ )
	{
        receive<<=1;
		IIC_SCL(1,IIC);
		My_Delay_us(IIC_delay);
        if(READ_SDA(IIC))
			receive++; 
		IIC_SCL(0,IIC);
		My_Delay_us(IIC_delay); 
    }					  
    return receive;
}



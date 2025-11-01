#ifndef __MOTOR_H__
#define __MOTOR_H__

/* 包含头文件 ----------------------------------------------------------------*/
#include "stm32f4xx_hal.h"


#define ENCODER_RESOLUTION 8    	//编码器一圈的物理脉冲数*/	黑皮370:8对级 ； 普通370：11对级
#define ENCODER_MULTIPLE 4       	//编码器倍频，通过定时器的编码器模式设置*/
#define MOTOR_REDUCTION_RATIO 20 	//电机的减速比*/			黑皮370:减速比20 ； 普通370：减速比21.3

/*电机转一圈总的脉冲数(定时器能读到的脉冲数) = 编码器物理脉冲数*编码器倍频*电机减速比 */
/* 11*4*34= 1496*/
#define TOTAL_RESOLUTION ( ENCODER_RESOLUTION*ENCODER_MULTIPLE*MOTOR_REDUCTION_RATIO ) 

#define PWM_Max 1000					// 设置PWM 上限
#define PID_Target_Speed_MAX  1000		// 目标速度的最大值 转/分钟,这个是检查上位机设置的参数，确保发送有误，别太大了，限制一下

void TIM8_Motor_Init(u16 arr,u16 psc);	//定时器8 PWM 电机1、2 初始化
void TIM4_Motor_Init(u16 arr,u16 psc);	//定时器4 PWM 电机3、BMI088 Heat 初始化
void TIM10_Motor_Init(u16 arr,u16 psc);	//定时器10 PWM 电机4- 初始化
void TIM11_Motor_Init(u16 arr,u16 psc);	//定时器11 PWM 电机4+ 初始化
void TIM9_Motor_Init(u16 arr,u16 psc);	//定时器9 PWM 盘球1、2 初始化
void Set_Ball_PWM(u8 ball_ch,u16 ball_pwm);	//盘球输出 PWM 

void BMI088_Heat_PWM(u16 pwm);			//BMI088加热

void Set_Motor_PWM(u8 motor_ch,int motor_pwm);//电机输出 PWM
void SetTargetMaxSpeed(int speed);
int GetTargetMaxSpeed(void);
void Speed_Protect(u8 ch,float *speed_val);		//目标速度值限制 单位 转/秒（这里限制的是期望值，达到期望值后，就控制住）
void Set_Target_Expect_Speed(int speed_1,int speed_2,int speed_3,int speed_4);	//上位机设置期望目标速度 接口
void Set_Target_Expect_Location(int position_1,int position_2,int position_3,int position_4);	//上位机设置期望目标位置 接口
void Motor_Cascade_Set_Control(u8 motor_ch);	//电机 串级（位置+速度） PID 控制输出
void Motor_Speed_Set_Control(u8 motor_ch);		//电机 速度 PID 控制输出
#endif 



#include "pid.h"

/*定义一个PID结构体型的全局变量*/

extern PID PID_Location;
extern PID PID_Speed;
/**
  * @brief  PID参数初始化
  *	@note 	无
  * @retval 无
  */

extern int PID_Target_Expect_Speed[5];		// 目标速度的期望值 转/分钟（期望转速达到多少，这个从上位机获取）
extern int PID_Target_Expect_Location[5];	// 目标位置的期望值 脉冲个数（期望位置达到多少，这个从上位机获取）
void PID_param_init()
{
	u8 i;
	for(i=0;i<5;i++)
	{
//		PID_Target_Expect_Speed[i]=500;
//**************  位置相关初始化参数  **************
		PID_Location.target_val[i] = PID_Target_Expect_Location[i];			
		PID_Location.output_val[i] = 0.0;
		PID_Location.err[i] = 0.0;
		PID_Location.err_last[i] = 0.0;
		PID_Location.integral[i] = 0.0;

//**************  速度相关初始化参数  **************
		PID_Speed.target_val[i]=PID_Target_Expect_Speed[i];		// 目标速度的最大值 转/分钟		
		PID_Speed.output_val[i]=0.0;
		PID_Speed.err[i]=0.0;
		PID_Speed.err_last[i]=0.0;
		PID_Speed.integral[i]=0.0;
	}
//**************  速度PID 初始化参数  **************  
		PID_Speed.Kp = PID_Speed_P_Default_Value;
		PID_Speed.Ki = PID_Speed_I_Default_Value;
		PID_Speed.Kd = PID_Speed_D_Default_Value;
//**************  位置PID 初始化参数  **************  
		PID_Location.Kp = PID_Location_P_Default_Value;
		PID_Location.Ki = PID_Speed_I_Default_Value;
		PID_Location.Kd = PID_Speed_D_Default_Value;
}

extern float det_plus;
//********************************************   PID 设置目标值  ********************************************
void Pid_Set_Target(u8 ch,PID *pid, float temp_val)
{  
	pid->target_val[ch] = temp_val;    // 设置当前的目标值
}

//********************************************   PID 获取目标值  ********************************************
float Pid_Get_Target(u8 ch,PID *pid)
{
  return pid->target_val[ch];    // 获取当前的目标值
}

/**
  * @brief  设置比例、积分、微分系数
  * @param  p：比例系数 P
  * @param  i：积分系数 i
  * @param  d：微分系数 d
  *	@note 	无
  * @retval 无
  */
//********************************************   设置比例、积分、微分系数  ********************************************
void PID_Set_p_i_d(PID *pid, float p, float i, float d)
{
	pid->Kp = p;    // 设置比例系数 P
	pid->Ki = i;    // 设置积分系数 I
	pid->Kd = d;    // 设置微分系数 D
}

//********************************************   位置PID  ********************************************
u8 LOC_DEAD_ZONE_Flag[5];		//位置环死区标志位。1：死区了（已经到位置了） ； 0：没死（没到位置）
#define LOC_DEAD_ZONE 10 /*位置环死区*/
//在 abs(目标- LOC_INTEGRAL_START_ERR) 区间内，积分开始起作用，积分的作用是在接近目标值区间时，电机吱吱响但不转,加大积分可以避免这个现象
//分段的意义在于，低速的时候用积分，高速，不用，但其实可以不分段也行。
#define LOC_INTEGRAL_START_ERR 3000 /*积分分离时对应的误差范围*/	
#define LOC_INTEGRAL_MAX_VAL 500   /*积分范围限定，防止积分饱和*/	// 积分上限设置，与 PWM 成正比
float PID_Location_Realize(u8 ch,PID *pid, float actual_val)
{

	/*计算目标值与实际值的误差*/
	pid->err[ch] = pid->target_val[ch]  - actual_val ;

	/* 设定闭环死区 */
	if((pid->err[ch]  >= -LOC_DEAD_ZONE) && (pid->err[ch]  <= LOC_DEAD_ZONE))
	{
		pid->err[ch]  = 0;
		pid->integral[ch]  = 0;
		pid->err_last[ch]  = 0;
		LOC_DEAD_ZONE_Flag[ch]=1;	//位置环死区标志位。1：死区了（已经到位置了） ； 0：没死（没到位置）
	}
	else
	{
		LOC_DEAD_ZONE_Flag[ch]=0;
	}
	pid->integral[ch]  += pid->err[ch] ;  
	
	/*积分范围限定，防止积分饱和*/
	if(pid->integral[ch]  > LOC_INTEGRAL_MAX_VAL)
		pid->integral[ch]  = LOC_INTEGRAL_MAX_VAL;
	else if(pid->integral[ch]  < -LOC_INTEGRAL_MAX_VAL)
		pid->integral[ch]  = -LOC_INTEGRAL_MAX_VAL;
	
	/*PID算法实现*/
	pid->output_val[ch]  = 	pid->Kp * pid->err[ch]  +
							pid->Ki * pid->integral[ch]  +
							pid->Kd * (pid->err[ch]  - pid->err_last[ch] );
	/*误差传递*/
	pid->err_last[ch] = pid->err[ch];
	/*返回当前实际值*/
	return pid->output_val[ch];
}

//********************************************   速度PID  ********************************************
#define SPE_DEAD_ZONE 1.0f /*速度环死区*/
#define SPE_INTEGRAL_START_ERR 10 /*积分分离时对应的误差范围*/
#define SPE_INTEGRAL_MAX_VAL 2000   /*积分范围限定，防止积分饱和*/

u16 SPEED_ZERO_DEAD_TIME= 20;   //速度为零时，持续一定时间后，认为可以停止PID校正了，单位10ms
extern u8 TIM6_DEAD_ZONE_Start[5];	//定时器 - 误差死区 持续时间 开始
extern u16 TIM6_DEAD_ZONE_Count[5];	//定时器 - 误差死区 持续时间 计数

float PID_Speed_Realize(u8 ch,PID *pid, float actual_val)
{
	/*计算目标值与实际值的误差*/
	pid->err[ch] = pid->target_val[ch] - actual_val;
	/* 设定闭环死区 */
	if(pid->target_val[ch] == 0 && (pid->err[ch] > - SPE_DEAD_ZONE) && (pid->err[ch] < SPE_DEAD_ZONE ) )
	{
		TIM6_DEAD_ZONE_Start[ch]=1;	//定时器 - 误差死区 持续时间 开始
		if(TIM6_DEAD_ZONE_Count[ch]>SPEED_ZERO_DEAD_TIME)
		{
			pid->err[ch] = 0;
			pid->integral[ch] = 0;
			pid->err_last[ch] = 0;
			TIM6_DEAD_ZONE_Start[ch]=0;	//定时器 - 误差死区 持续时间 开始
			TIM6_DEAD_ZONE_Count[ch]=0;	//定时器 - 误差死区 持续时间 计数
			if(TIM6_DEAD_ZONE_Count[ch]>65530)
			{
				TIM6_DEAD_ZONE_Count[ch]=0;	//定时器 - 误差死区 持续时间 计数
			}
		}
	}
	else
	{
		TIM6_DEAD_ZONE_Start[ch]=0;	//定时器 - 误差死区 持续时间 开始
		TIM6_DEAD_ZONE_Count[ch]=0;	//定时器 - 误差死区 持续时间 计数
	}

#if 0
	/*积分项*/
	pid->integral[ch] += pid->err[ch];
#else	
	/*积分项，积分分离，偏差较大时去掉积分作用*/
//	if(pid->err > -SPE_INTEGRAL_START_ERR && pid->err < SPE_INTEGRAL_START_ERR)
	{
		pid->integral[ch] += pid->err[ch];  
        /*积分范围限定，防止积分饱和*/
		if(pid->integral[ch] > SPE_INTEGRAL_MAX_VAL)
			pid->integral[ch] = SPE_INTEGRAL_MAX_VAL;
		else if(pid->integral[ch] < -SPE_INTEGRAL_MAX_VAL)
			pid->integral[ch] = -SPE_INTEGRAL_MAX_VAL;
	}	
#endif
	/*PID算法实现*/
	pid->output_val[ch]  = 	pid->Kp * pid->err[ch] +
							pid->Ki * pid->integral[ch] +
							pid->Kd *(pid->err[ch] - pid->err_last[ch]);
	/*误差传递*/
	pid->err_last[ch] = pid->err[ch];

	return pid->output_val[ch];	/*返回当前实际值*/
}

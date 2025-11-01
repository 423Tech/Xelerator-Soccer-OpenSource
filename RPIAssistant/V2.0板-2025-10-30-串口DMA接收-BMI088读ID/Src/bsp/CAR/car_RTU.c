#include "motor.h"
#include "pid.h"
#include "string.h"		
#include <stdarg.h>
#include <stdio.h>
#include <math.h>
#include <stdlib.h>
#include "usart.h"
#include "car_RTU.h"
#include "pid.h"
#include "car.h"
#include "Encoder.h"
extern PID PID_Location;
extern PID PID_Speed;


//*******************  ´®¿Ú ²ÎÊı  *******************
extern u16 UART4_RX_Count;						// ÒÑ½ÓÊÕµ½µÄ×Ö½ÚÊı
extern u8 UART4_RX_BUF[UART4_RX_MAX];			// ´®¿Ú½ÓÊÕ»º³å
extern uint8_t UART4_DMA_RX_Buffer[UART4_DMA_RX_BUFFER_MAX_LENGTH];


u8 UART4_RTU_RX_Function;						// UART4_RTU ½ÓÊÕÊı¾İ·ÖÎö £¬¹¦ÄÜÂë
u8 UART4_RTU_RX_Len;							// UART4_RTU ½ÓÊÕÊı¾İ·ÖÎö £¬Êı¾İÎ»
u8 UART4_RTU_RX_Data[UART4_RTU_RX_Data_MAX];	// UART4_RTU ½ÓÊÕÊı¾İ·ÖÎö £¬Êı¾İ¶Î
u8 UART4_RTU_Buff_New_Event_Flag;				// UART4_RTU ĞÂµÄÊÂ¼ş ±êÖ¾Î»



void UART4_RTU_RX_Data_Buff_CLR(void)	//Çå¿Õ RTU Êı¾İ¶Î µÄÊı¾İ
{
	u16 k;
	for(k=0;k<UART4_RTU_RX_Data_MAX;k++){UART4_RTU_RX_Data[k] = 0x00;}
}

u32 RTU_RX_Times;
extern uint8_t UART4_DMA_RX_Buffer[UART4_DMA_RX_BUFFER_MAX_LENGTH];
//u8 UART4_RTU_Responce_Flag;				//UART4_RTU ·¢ËÍ ·µ»ØĞÅºÅ to ÉÏÎ»»ú
//*******************  UART4_RTU Êı¾İ½âÎö£¬½âÎö³ö  ¹¦ÄÜÂë£¬Êı¾İÎ»£¬Êı¾İ¶Î  ******************
void UART4_RTU_Buff_Process(void)
{
	int i;
	int j;

	if(UART4_RX_Count>=7)
	{
		if(UART4_DMA_RX_Buffer[UART4_RX_Count-1]==UART4_RTU_FE_L && UART4_DMA_RX_Buffer[UART4_RX_Count-2]==UART4_RTU_FE_H)	//ÕÒµ½ÁËÖ¡Î²
		{
			for(i=UART4_RX_Count-3;i>=0;i--)	//ÍùÇ°ÕÒÖ¡Í·
			{
				if(UART4_DMA_RX_Buffer[i]==UART4_RTU_FH_H && UART4_DMA_RX_Buffer[i+1]==UART4_RTU_FH_L)
				{
					UART4_RTU_RX_Function=UART4_DMA_RX_Buffer[i+3];						// UART4 ½ÓÊÕÊı¾İ·ÖÎö £¬¹¦ÄÜÂë
					UART4_RTU_RX_Len=UART4_DMA_RX_Buffer[i+4];								// UART4 ½ÓÊÕÊı¾İ·ÖÎö £¬Êı¾İÎ»
					for(j=0;j<UART4_RTU_RX_Len;j++)
						UART4_RTU_RX_Data[j]=UART4_DMA_RX_Buffer[5+j+i];					// UART4 ½ÓÊÕÊı¾İ·ÖÎö £¬Êı¾İ¶Î
					RTU_RX_Times++;	
					UART4_RTU_Buff_New_Event_Flag=1;// UART4 ĞÂµÄÊÂ¼ş ±êÖ¾Î»
					break;					
				}
			}
		}
	}
}
u16 Motor_PWM_or_RPM_Mode=1;			//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½

u8 UART4_RTU_Function_To_Car_Move;		//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
extern u8 Car_Move_Aim_Time_State_Flag;	//³µÔË¶¯¡°Ò»¶ÎÊ±¼ä¡±º¯Êı·µ»Ø×´Ì¬ 0£º¿ÕÏĞ£¨Íê³É£©£»2£ºÕıÔÚÔËĞĞ £» 3£ºÍê³É
extern u8 Car_Turn_State_Flag;			//Ğı×ª·µ»Ø×´Ì¬±êÖ¾ ¡£0£º¿ÕÏĞ£¨ÊÖ¶¯ÖÃÎ»£© £»1£º¼¤»î¹¦ÄÜ £»2£ºÕıÔÚ½øĞĞĞı×ª£»3£ºÍê³ÉÈÎÎñ
extern u8 Car_Keep_Angle_Location_Move_State_Flag;			//Î»ÖÃ¿ØÖÆ·½Ê½ÖĞ£¬Î»ÖÃ¡¢½Ç¶Èµ½Î»ÁËµÄ±êÖ¾¡£0£º¿ÕÏĞ£¨Íê³É£©£»1£ºÕıÔÚ×öÎ»ÖÃÈÎÎñ:£»2£ºÎ»ÖÃÍê³É£¬ÕıÔÚ×öÔ­µØĞ£Õı £» 3£ºËùÓĞ¶¯×÷Íê³É
u8 UART4_RTU_Responce_Data = 0;		// Ã¿´Î½ÓÊÕµ½´®¿ÚÏûÏ¢£¬Õâ¸öÖµ±äÎª FE £¬·¢ËÍ¸øÉÏÎ»»úºó£¬ÏÂÒ»´Î·¢ËÍ±äÎªÄ¬ÈÏÖµ 0 
extern u16 UART4_RTU_Send_Message_Timer;	//¼ÆÊıÔö¼Ó¶àÉÙ´ÎÖ®ºó£¬ÔÙ·¢ËÍĞÅÏ¢£¨´úÌæ¶¨Ê±Æ÷»òÑÓÊ±£©
//*******************  RS485 RTU Êı¾İ´¦Àí(ÊÂ¼ş´¦Àí)  ******************
void UART4_RTU_Buff_Deal(void)
{
	if(UART4_RTU_Buff_New_Event_Flag==1)// UART4 ĞÂµÄÊÂ¼ş ±êÖ¾Î»
	{
		switch(UART4_RTU_RX_Function)
		{
		//*******************  ÉèÖÃµç»ú²ÎÊı  ******************
			case UART4_RTU_Function_Speed_PID_1:		//µ¥¶ÀÉèÖÃ µç»ú1 PID²ÎÊı
				break;
			case UART4_RTU_Function_Speed_PID_2:		//µ¥¶ÀÉèÖÃ µç»ú2 PID²ÎÊı
				break;
			case UART4_RTU_Function_Speed_PID_3:		//µ¥¶ÀÉèÖÃ µç»ú3 PID²ÎÊı
				break;
			case UART4_RTU_Function_Speed_PID_4:		//µ¥¶ÀÉèÖÃ µç»ú4 PID²ÎÊı
				break;
			case UART4_RTU_Function_Set_PWM:	//Ò»´ÎĞÔÉèÖÃ4¸öµç»úµÄPWM£¬µ¥Î»£ºPWM
				if(UART4_RTU_RX_Len == 8)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					Motor_PWM_or_RPM_Mode=2;	//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½
					UART4_RTU_SET_PWM_Data(UART4_RTU_RX_Data);		//UART4_RTU ½«½ÓÊÕµ½µÄ PWM ×ª»¯£¨ÒòÎª·Å´óÁË£©
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Speed_PID_ALL:	//Í³Ò»ÉèÖÃ µç»ú PID²ÎÊı
				if(UART4_RTU_RX_Len == 6)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Speed_PID_Data(UART4_RTU_RX_Data);		//UART4_RTU ½«½ÓÊÕµ½µÄ PIDÊı¾İ ×ª»¯£¨ÒòÎª·Å´óÁË£©
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Set_RPM:	//Ò»´ÎĞÔÉèÖÃ4¸öµç»úµÄ×ªËÙ£¬µ¥Î»£ºRPM
				if(UART4_RTU_RX_Len == 8)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					Motor_PWM_or_RPM_Mode=1;	//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½
					UART4_RTU_SET_RPM_Data(UART4_RTU_RX_Data);		//UART4_RTU ½«½ÓÊÕµ½µÄ ×ªËÙ ×ª»¯£¨ÒòÎª·Å´óÁË£©
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Encoder_Resolution:		//ÅäÖÃ´Å»·¼«¶ÔÊı
				if(UART4_RTU_RX_Len == 2)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Encoder_Resolution(UART4_RTU_RX_Data);		//UART4_RTU ÉèÖÃÈíÆô¶¯Ê±¼ä
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Motor_Reduction_Ratio:	//ÅäÖÃµç»úµÄ¼õËÙ±È
				if(UART4_RTU_RX_Len == 2)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Motor_Reduction_Ratio(UART4_RTU_RX_Data);		//UART4_RTU ÉèÖÃÈíÆô¶¯Ê±¼ä
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Location_PID_ALL:	//Í³Ò»ÉèÖÃ µç»ú Î»ÖÃPID²ÎÊı
				if(UART4_RTU_RX_Len == 6)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Location_PID_Data(UART4_RTU_RX_Data);		//UART4_RTU ½«½ÓÊÕµ½µÄ Î»ÖÃPIDÊı¾İ ×ª»¯£¨ÒòÎª·Å´óÁË£©
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Motor_Type:	//ÉèÖÃµç»úĞÍºÅ£¨1£º370 ; 2£ºÆÕÍ¨310£©	
				if(UART4_RTU_RX_Len == 2)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Motor_Type(UART4_RTU_RX_Data);		//ÉèÖÃµç»úĞÍºÅ£¨1£º370 ; 2£ºÆÕÍ¨310£©	
					UART4_RTU_Function_Clear();			
				}
				break;
		//*******************  ÉèÖÃÕû³µ²ÎÊı  ******************
			case UART4_RTU_Function_Soft_Starter_Set_Time:	//ÅäÖÃµç»úÈíÆô¶¯Ê±¼ä
				if(UART4_RTU_RX_Len == 2)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Soft_Starter_Set_Time(UART4_RTU_RX_Data);		//UART4_RTU ÉèÖÃÈíÆô¶¯Ê±¼ä
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Soft_Stop_Set_Time:		//ÅäÖÃ ÈíÍ£Ö¹Ê±¼ä
				if(UART4_RTU_RX_Len == 2)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Soft_Stop_Set_Time(UART4_RTU_RX_Data);		//UART4_RTU ÉèÖÃÈíÍ£Ö¹Ê±¼ä
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Timeout_Set_Time:		//ÅäÖÃ ×èÈûÊ±¼ä
				if(UART4_RTU_RX_Len == 2)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Car_Move_Timeout(UART4_RTU_RX_Data);			//UART4_RTU ÉèÖÃ×èÈûÊ±¼ä 
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Car_Move_Fix:		//ÅäÖÃ Õû³µÔË¶¯¹ı³ÌÖĞ£¬³µÍ·ĞŞÕı²ÎÊı
				if(UART4_RTU_RX_Len == 4)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Car_Move_Fix_Value(UART4_RTU_RX_Data);			//UART4_RTU ÉèÖÃÕû³µÔË¶¯¹ı³ÌÖĞ£¬³µÍ·ĞŞÕı²ÎÊı
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Car_Turn_Fix:		//ÅäÖÃ Õû³µÔ­µØĞı×ª¹ı³ÌÖĞ£¬³µÍ·ĞŞÕı²ÎÊı
				if(UART4_RTU_RX_Len == 8)
				{
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Car_Turn_Fix_Value(UART4_RTU_RX_Data);			//UART4_RTU ÉèÖÃÕû³µÔ­µØĞı×ª¹ı³ÌÖĞ£¬³µÍ·ĞŞÕı²ÎÊı
					UART4_RTU_Function_Clear();			
				}
				break;
			case UART4_RTU_Function_Data_Reset:		//ÅäÖÃ ¸´Î»ËùÓĞ²ÎÊı
				if(UART4_RTU_RX_Len == 1)
				{
					Motor_PWM_or_RPM_Mode=1;	//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Car_Reset_Value(UART4_RTU_RX_Data);			//ÅäÖÃ ¸´Î»ËùÓĞ²ÎÊı
					UART4_RTU_Function_Clear();			
				}
				break;
		//*******************  ÉèÖÃÕû³µÔË¶¯º¯Êı²ÎÊı  ******************
			case UART4_RTU_Function_Car_Z_Speed:		//ÅäÖÃ Õû³µ ³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÔË¶¯
				if(UART4_RTU_RX_Len == 6)
				{
					Motor_PWM_or_RPM_Mode=1;	//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½
					UART4_RTU_Function_To_Car_Move = UART4_RTU_RX_Function;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Car_Keep_Angle_Z_Speed_Move(UART4_RTU_RX_Data);//UART4_RTU Õû³µ¿ØÖÆ£¬³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÔË¶¯
					UART4_RTU_Function_Clear();			
				}
				break;	
			case UART4_RTU_Function_Car_Z_Speed_Time:	//ÅäÖÃ Õû³µ ³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÔË¶¯
				if(UART4_RTU_RX_Len == 8)
				{
					Motor_PWM_or_RPM_Mode=1;	//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½
					UART4_RTU_Function_To_Car_Move = UART4_RTU_RX_Function;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Car_Keep_Angle_Z_Speed_Move_Time(UART4_RTU_RX_Data);//UART4_RTU Õû³µ¿ØÖÆ£¬³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÔË¶¯Ò»¶ÎÊ±¼ä
					UART4_RTU_Function_Clear();			
				}
				break;	
			case UART4_RTU_Function_Car_XY_Speed:	//ÅäÖÃ Õû³µ ³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬¸ø¶¨xyËÙ¶ÈÔË¶¯£¬x->³µÉíÓÒ²àÕı£¬y->³µÍ·Ç°Õı
				if(UART4_RTU_RX_Len == 6)
				{
					Motor_PWM_or_RPM_Mode=1;	//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½
					UART4_RTU_Function_To_Car_Move = UART4_RTU_RX_Function;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Car_Keep_Angle_XY_Speed_Move(UART4_RTU_RX_Data);		//UART4_RTU Õû³µ¿ØÖÆ£¬³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬¸ø¶¨xyËÙ¶ÈÔË¶¯£¬x->³µÉíÓÒ²àÕı£¬y->³µÍ·Ç°Õı
					UART4_RTU_Function_Clear();			
				}
				break;	
			case UART4_RTU_Function_Car_Turn:	//ÅäÖÃ Õû³µ ³µÔ­µØĞı×ª½Ç¶È£¨½Ç¶È±Õ»·£©
				if(UART4_RTU_RX_Len == 2)
				{
					Motor_PWM_or_RPM_Mode=1;	//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½
					UART4_RTU_Function_To_Car_Move = UART4_RTU_RX_Function;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Car_Turn(UART4_RTU_RX_Data);							//UART4_RTU Õû³µ¿ØÖÆ£¬³µÔ­µØĞı×ª½Ç¶È£¨½Ç¶È±Õ»·£©
					UART4_RTU_Function_Clear();			
				}
				break;	
			case UART4_RTU_Function_Car_Location:	//ÅäÖÃ Õû³µ ³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÎ»ÒÆ ¾àÀë
				if(UART4_RTU_RX_Len == 10)
				{
					Motor_PWM_or_RPM_Mode=1;	//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½
					UART4_RTU_Function_To_Car_Move = UART4_RTU_RX_Function;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Car_Keep_Angle_Location_Move(UART4_RTU_RX_Data);		//UART4_RTU Õû³µ¿ØÖÆ£¬³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÎ»ÒÆ ¾àÀë
					UART4_RTU_Function_Clear();			
				}
				break;	
			case UART4_RTU_Function_Car_Stop:	//ÅäÖÃ Õû³µ Í£Ö¹ÒÆ¶¯
				if(UART4_RTU_RX_Len == 1)
				{
					Motor_PWM_or_RPM_Mode=1;	//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½
					UART4_RTU_Function_To_Car_Move = 0;	//UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ
					UART4_RTU_Car_Stop(UART4_RTU_RX_Data);		//UART4_RTU Õû³µ¿ØÖÆ£¬Í£Ö¹ÒÆ¶¯
					UART4_RTU_Function_Clear();			
				}
				break;	
		}
		UART4_RTU_Buff_New_Event_Flag=0;// UART4 ĞÂµÄÊÂ¼ş ±êÖ¾Î
//		UART4_RTU_Responce_Data = 0XFE;		// Ã¿´Î½ÓÊÕµ½´®¿ÚÏûÏ¢£¬Õâ¸öÖµ±äÎª FE £¬·¢ËÍ¸øÉÏÎ»»úºó£¬ÏÂÒ»´Î·¢ËÍ±äÎªÄ¬ÈÏÖµ 0 
//		UART4_RTU_Send_Message();					//UART4_RTU ·¢ËÍĞÅÏ¢ to ÉÏÎ»»ú
//		UART4_RTU_Responce_Data = 0;		// Ã¿´Î½ÓÊÕµ½´®¿ÚÏûÏ¢£¬Õâ¸öÖµ±äÎª FE £¬·¢ËÍ¸øÉÏÎ»»úºó£¬ÏÂÒ»´Î·¢ËÍ±äÎªÄ¬ÈÏÖµ 0 
//		UART4_RTU_Send_Message_Timer=0;	//¼ÆÊıÔö¼Ó¶àÉÙ´ÎÖ®ºó£¬ÔÙ·¢ËÍĞÅÏ¢£¨´úÌæ¶¨Ê±Æ÷»òÑÓÊ±£©
		
	}
}
//*******************  UART4_RTU ½ÓÊÕµ½ÕıÈ·¹¦ÄÜÂëºó£¬Çå³ıÒ»Ğ©±êÖ¾Î»  ******************
void UART4_RTU_Function_Clear(void)
{
	UART4_RTU_RX_Function=0;
	UART4_RTU_RX_Len=0;
	UART4_RTU_RX_Data_Buff_CLR();
	Car_Move_Aim_Time_State_Flag=0;	//³µÔË¶¯¡°Ò»¶ÎÊ±¼ä¡±º¯Êı·µ»Ø×´Ì¬ 0£º¿ÕÏĞ£¨Íê³É£©£»2£ºÕıÔÚÔËĞĞ £» 3£ºÍê³É
	Car_Turn_State_Flag=0;			//Ğı×ª·µ»Ø×´Ì¬±êÖ¾ ¡£0£º¿ÕÏĞ£¨ÊÖ¶¯ÖÃÎ»£© £»1£º¼¤»î¹¦ÄÜ £»2£ºÕıÔÚ½øĞĞĞı×ª£»3£ºÍê³ÉÈÎÎñ
	Car_Keep_Angle_Location_Move_State_Flag=0;			//Î»ÖÃ¿ØÖÆ·½Ê½ÖĞ£¬Î»ÖÃ¡¢½Ç¶Èµ½Î»ÁËµÄ±êÖ¾¡£0£º¿ÕÏĞ£¨Íê³É£©£»1£ºÕıÔÚ×öÎ»ÖÃÈÎÎñ:£»2£ºÎ»ÖÃÍê³É£¬ÕıÔÚ×öÔ­µØĞ£Õı £» 3£ºËùÓĞ¶¯×÷Íê³É
}
//*******************  UART4_RTU ½«½ÓÊÕµ½µÄ PWM ×ª»¯£¨ÒòÎª·Å´óÁË£©  ******************
extern u8 TIM6_Car_Soft_Starter_Start[5];		//¶¨Ê±Æ÷ - Õû³µÈíÆô¶¯ ¿ªÊ¼
extern u32 TIM6_Car_Soft_Starter_Count[5];		//¶¨Ê±Æ÷ - Õû³µÈíÆô¶¯ ¼ÆÊı
extern u8 Soft_Starter_OK_Flag[5];				//µç»úÈíÆô¶¯ Íê³É±êÖ¾ 0£ºÎ´Íê³É£»1£ºÍê³É
extern int PID_Target_Expect_Speed[5];	// Ä¿±êËÙ¶ÈµÄÆÚÍûÖµ ×ª/·ÖÖÓ£¨ÆÚÍû×ªËÙ´ïµ½¶àÉÙ£¬Õâ¸ö´ÓÉÏÎ»»ú»ñÈ¡£©
int motor_value[5];
void UART4_RTU_SET_PWM_Data(u8 *buf)
{
	u8 i;
	motor_value[1] = (buf[0]<<8 | buf[1])-10000;
	motor_value[2] = (buf[2]<<8 | buf[3])-10000;
	motor_value[3] = (buf[4]<<8 | buf[5])-10000;
	motor_value[4] = (buf[6]<<8 | buf[7])-10000;
	
	//************  ÇĞ»»³É PWMÄ£Ê½Ê±£¬½« RPM ÈíÆô¶¯µÄ²ÎÊıÇåÁã  ************
	for(i=1;i<5;i++)
	{
		TIM6_Car_Soft_Starter_Start[i]=0;	//¶¨Ê±Æ÷ - µç»úÈíÆô¶¯ ¿ªÊ¼
		TIM6_Car_Soft_Starter_Count[i]=0;	//¶¨Ê±Æ÷ - µç»úÈíÆô¶¯ ¼ÆÊı
		Soft_Starter_OK_Flag[i]=0;		//µç»úÈíÆô¶¯ Íê³É±êÖ¾ 0£ºÎ´Íê³É£»1£ºÍê³É
		/*
		ÏÂÃæÕâ¾ä»°£¬ÕâÀïÕâÑùÉèÖÃÆäÊµÃ»Ê²Ã´Ö±½ÓÒâÒå£¬PWMºÍ×ªËÙ±¾À´¾ÍÊÇÁ½»ØÊÂ£¬
		µ«ÊÇÎªÁË,´ÓPWMÇĞ»»³É×ªËÙ£¨RPM£©Ê±£¬²»ÏÔµÃÄÇÃ´Í»Ø££¬ËùÒÔÕâÑù¸³Öµ
		ÀıÈç£ºÊ×ÏÈPWM£¬500£¬È»ºó¸ø×ªËÙ£¬0£¬ÒòÎªÎó²îÖµºÜ´ó£¨PWMÎª500Ê±µÄ×ªËÙÖµ£©£¬ËùÒÔ×ªËÙÍ»È»¸ø0Ê±£¬²»ÄÜÁ¢¿Ì±§ËÀ£¬Ëû»áµ÷Ò»¶ÎÊ±¼ä
		*/
		PID_Target_Expect_Speed[i]=motor_value[i]*2;
	}
	Set_Motor_PWM(1,motor_value[1]);	//µç»úÊä³ö PWM
	Set_Motor_PWM(2,motor_value[2]);	//µç»úÊä³ö PWM
	Set_Motor_PWM(3,motor_value[3]);	//µç»úÊä³ö PWM
	Set_Motor_PWM(4,motor_value[4]);	//µç»úÊä³ö PWM

}
//*******************  UART4_RTU ½«½ÓÊÕµ½µÄ ËÙ¶ÈPIDÊı¾İ ×ª»¯£¨ÒòÎª·Å´óÁË£©  ******************
void UART4_RTU_Speed_PID_Data(u8 *buf)
{
	float p,i,d;
	p = (float)(buf[0]<<8 | buf[1])/1000 ;
	i = (float)(buf[2]<<8 | buf[3])/1000 ;
	d = (float)(buf[4]<<8 | buf[5])/1000 ;
	PID_Set_p_i_d(&PID_Speed,p,i,d);
}
//*******************  UART4_RTU ½«½ÓÊÕµ½µÄ ×ªËÙ£¨RPM£© ×ª»¯£¨ÒòÎª·Å´óÁË£©  ******************
void UART4_RTU_SET_RPM_Data(u8 *buf)
{
//	int motor_value[5];
	motor_value[1] = (buf[0]<<8 | buf[1])-10000;
	motor_value[2] = (buf[2]<<8 | buf[3])-10000;
	motor_value[3] = (buf[4]<<8 | buf[5])-10000;
	motor_value[4] = (buf[6]<<8 | buf[7])-10000;
	Set_Target_Expect_Speed(motor_value[1],motor_value[2],motor_value[3],motor_value[4]);	//ÉÏÎ»»úÉèÖÃÆÚÍûÄ¿±êËÙ¶È ½Ó¿Ú
}

//*******************  UART4_RTU ÉèÖÃ±àÂëÆ÷´Å»· ¼«¶ÔÊı  ******************
extern float Encoder_Total_Resolution;			//±àÂëÆ÷×Ü·Ö±æÂÊ
extern u16 Encoder_Resolution;					//±àÂëÆ÷ ¼«¶ÔÊı
extern float Motor_Reduction_Ratio;				//µç»ú ¼õËÙ±È
void UART4_RTU_Encoder_Resolution(u8 *buf)
{
	Encoder_Resolution = (buf[0]<<8 | buf[1]);

	Encoder_Total_Resolution = Encoder_Resolution*ENCODER_MULTIPLE*Motor_Reduction_Ratio;//µç»ú×ªÒ»È¦×ÜµÄÂö³åÊı(¶¨Ê±Æ÷ÄÜ¶Áµ½µÄÂö³åÊı) = ±àÂëÆ÷ÎïÀíÂö³åÊı*±àÂëÆ÷±¶Æµ*µç»ú¼õËÙ±È */
}
//*******************  UART4_RTU ÉèÖÃµç»ú ¼õËÙ±È  ******************
void UART4_RTU_Motor_Reduction_Ratio(u8 *buf)
{
	Motor_Reduction_Ratio = (float)(buf[0]<<8 | buf[1]) /100;
	Encoder_Total_Resolution = Encoder_Resolution*ENCODER_MULTIPLE*Motor_Reduction_Ratio;//µç»ú×ªÒ»È¦×ÜµÄÂö³åÊı(¶¨Ê±Æ÷ÄÜ¶Áµ½µÄÂö³åÊı) = ±àÂëÆ÷ÎïÀíÂö³åÊı*±àÂëÆ÷±¶Æµ*µç»ú¼õËÙ±È */
}
//*******************  UART4_RTU ½«½ÓÊÕµ½µÄ Î»ÖÃPIDÊı¾İ ×ª»¯£¨ÒòÎª·Å´óÁË£©  ******************
void UART4_RTU_Location_PID_Data(u8 *buf)
{
	float p,i,d;
	p = (float)(buf[0]<<8 | buf[1])/1000 ;
	i = (float)(buf[2]<<8 | buf[3])/1000 ;
	d = (float)(buf[4]<<8 | buf[5])/1000 ;
	PID_Set_p_i_d(&PID_Location,p,i,d);
}
//*******************  UART4_RTU ÉèÖÃµç»úĞÍºÅ£¨310 / 370£©  ******************
//extern u16 Motor_Type ;	//ÉèÖÃµç»úĞÍºÅ£¨310 / 370£©	
void UART4_RTU_Motor_Type(u8 *buf)
{
	u16 data;
	data =  (buf[0]<<8 | buf[1]);
	if( data==310 || data==370 )
	{
//		if( Motor_Type != data)
//		{
//			Motor_Type =data;	//ÉèÖÃµç»úĞÍºÅ£¨310 / 370£©
//			Motor_Type_Write_Flash(Motor_Type); 		//FLASH Ğ´Èë µç»úÀàĞÍ
//			TIM4_Encoder_Init(ENCODER_TIM_PERIOD-1,ENCODER_TIM_PSC);	//¶¨Ê±Æ÷4 ±àÂëÆ÷1 ³õÊ¼»¯
//			TIM2_Encoder_Init(ENCODER_TIM_PERIOD-1,ENCODER_TIM_PSC);	//¶¨Ê±Æ÷4 ±àÂëÆ÷2 ³õÊ¼»¯
//			TIM3_Encoder_Init(ENCODER_TIM_PERIOD-1,ENCODER_TIM_PSC);	//¶¨Ê±Æ÷4 ±àÂëÆ÷3 ³õÊ¼»¯
//			TIM5_Encoder_Init(ENCODER_TIM_PERIOD-1,ENCODER_TIM_PSC);	//¶¨Ê±Æ÷4 ±àÂëÆ÷4 ³õÊ¼»¯
//		}
	}
}


//*******************  UART4_RTU ÉèÖÃÈíÆô¶¯Ê±¼ä  ******************
extern u16 Car_Soft_Starter_Time_Set_Value;		//³µÒÆ¶¯£¬Éè¶¨µÄ ÈíÆô¶¯Ê±¼ä£¬µ¥Î»£¨ms£©
void UART4_RTU_Soft_Starter_Set_Time(u8 *buf)
{
	Car_Soft_Starter_Time_Set_Value = (buf[0]<<8 | buf[1]);
}

//*******************  UART4_RTU ÉèÖÃÈíÍ£Ö¹Ê±¼ä  ******************
extern u16 Car_Soft_Stop_Time_Set_Value;				//³µÒÆ¶¯£¬Éè¶¨µÄ ÈíÍ£Ö¹Ê±¼ä£¬µ¥Î»£¨ms£©
void UART4_RTU_Soft_Stop_Set_Time(u8 *buf)
{
	Car_Soft_Stop_Time_Set_Value = (buf[0]<<8 | buf[1]);
}

//*******************  UART4_RTU ÉèÖÃ×èÈûÊ±¼ä  ******************
extern u16 Car_Move_Timeout_Set_Value;			//³µÒÆ¶¯£¬Éè¶¨µÄ ×èÈûÊ±¼ä£¬µ¥Î»£¨ms£©£¬Î»ÒÆÊ±¼ä¡¢Î»ÒÆ¾àÀëº¯ÊıÊÊÓÃ
void UART4_RTU_Car_Move_Timeout(u8 *buf)
{
	Car_Move_Timeout_Set_Value = (buf[0]<<8 | buf[1]);
}

//*******************  UART4_RTU ÉèÖÃÕû³µÔË¶¯¹ı³ÌÖĞ£¬³µÍ·ĞŞÕı²ÎÊı  ******************
extern float Car_Keep_Angle_Move_Set_Fix_k;				//Í³Ò»ÉèÖÃ£¬ÒÆ¶¯¹ı³ÌÖĞ£¬ĞèÒªĞ£Õı³µÍ·µÄ£¬k
extern float Car_Keep_Angle_Move_Set_Fix_b;				//Í³Ò»ÉèÖÃ£¬ÒÆ¶¯¹ı³ÌÖĞ£¬ĞèÒªĞ£Õı³µÍ·µÄ£¬k
			
void UART4_RTU_Car_Move_Fix_Value(u8 *buf)
{
	Car_Keep_Angle_Move_Set_Fix_k = (float)(buf[0]<<8 | buf[1]) /1000;
	Car_Keep_Angle_Move_Set_Fix_b = (float)(buf[2]<<8 | buf[3]) /1000;		
}

//*******************  UART4_RTU ÉèÖÃÕû³µÔ­µØĞı×ª¹ı³ÌÖĞ£¬³µÍ·ĞŞÕı²ÎÊı  ******************
extern float Car_Keep_Angle_Turn_Set_Fix_k;				//Í³Ò»ÉèÖÃ£¬Ô­µØĞı×ª¹ı³ÌÖĞ£¬ĞèÒªĞ£Õı³µÍ·µÄ£¬k
extern float Car_Keep_Angle_Turn_Set_Fix_b;				//Í³Ò»ÉèÖÃ£¬Ô­µØĞı×ª¹ı³ÌÖĞ£¬ĞèÒªĞ£Õı³µÍ·µÄ£¬k
extern float Car_Keep_Angle_Turn_Set_Angle_range;		//Í³Ò»ÉèÖÃ£¬Ô­µØĞı×ª¹ı³ÌÖĞ£¬±£³ÖÄ¿±ê½Ç¶È ãĞÖµ
extern u16 Car_Keep_Angle_Turn_Set_keep_time;			//Í³Ò»ÉèÖÃ£¬Ô­µØĞı×ª¹ı³ÌÖĞ£¬±£³ÖÄ¿±ê½Ç¶È Ê±¼ä
void UART4_RTU_Car_Turn_Fix_Value(u8 *buf)
{
	Car_Keep_Angle_Turn_Set_Fix_k = (float)(buf[0]<<8 | buf[1]) /1000;
	Car_Keep_Angle_Turn_Set_Fix_b = (float)(buf[2]<<8 | buf[3]) /1000;		
	Car_Keep_Angle_Turn_Set_Angle_range = (float)((buf[4]<<8 | buf[5])-10000)/10;
	Car_Keep_Angle_Turn_Set_keep_time = (buf[6]<<8 | buf[7]);	
}

//*******************  UART4_RTU ¸´Î»ËùÓĞ²ÎÊı  ******************
extern u8 Car_Turn_State_Flag;			//Ğı×ª·µ»Ø×´Ì¬±êÖ¾ ¡£0£º¿ÕÏĞ£¨ÊÖ¶¯ÖÃÎ»£© £»1£º¼¤»î¹¦ÄÜ £»2£ºÕıÔÚ½øĞĞĞı×ª£»3£ºÍê³ÉÈÎÎñ
extern u8 Car_Keep_Angle_Location_Move_State_Flag;			//Î»ÖÃ¿ØÖÆ·½Ê½ÖĞ£¬Î»ÖÃ¡¢½Ç¶Èµ½Î»ÁËµÄ±êÖ¾¡£0£º¿ÕÏĞ£¨Íê³É£©£»1£ºÕıÔÚ×öÎ»ÖÃÈÎÎñ:£»2£ºÎ»ÖÃÍê³É£¬ÕıÔÚ×öÔ­µØĞ£Õı £» 3£ºËùÓĞ¶¯×÷Íê³É
void UART4_RTU_Car_Reset_Value(u8 *buf)
{
	if( buf[0]==1)
	{
		Motor_PWM_or_RPM_Mode=1;									//µç»ú¹¤×÷Ä£Ê½£¬1£º×ªËÙÄ£Ê½£¨Ä¬ÈÏ£© £» 2,£ºÕ¼¿Õ±ÈÄ£Ê½
		PID_Set_p_i_d(&PID_Speed,PID_Speed_P_Default_Value,PID_Speed_I_Default_Value,PID_Speed_D_Default_Value);			//µç»úPID²ÎÊı
		PID_Set_p_i_d(&PID_Location,PID_Location_P_Default_Value,PID_Location_I_Default_Value,PID_Location_D_Default_Value);//Î»ÖÃPID²ÎÊı

		Encoder_Resolution=ENCODER_RESOLUTION;						//±àÂëÆ÷ ¼«¶ÔÊı
		Motor_Reduction_Ratio=MOTOR_REDUCTION_RATIO;				//µç»ú ¼õËÙ±È
		Encoder_Total_Resolution = TOTAL_RESOLUTION;			//±àÂëÆ÷×Ü·Ö±æÂÊ
		Car_Stop();													//³µÍ£Ö¹ÔË¶¯
		Car_Soft_Starter_Time_Set_Value=Car_Soft_Starter_Default_Value;					//³µÒÆ¶¯£¬Éè¶¨µÄ ÈíÆô¶¯Ê±¼ä£¬µ¥Î»£¨ms£©
		Car_Soft_Stop_Time_Set_Value=Car_Soft_Stop_Default_Value;						//³µÒÆ¶¯£¬Éè¶¨µÄ ÈíÍ£Ö¹Ê±¼ä£¬µ¥Î»£¨ms£©
		
		Car_Keep_Angle_Move_Set_Fix_k=Car_Keep_Angle_Move_Default_Fix_k;				//Í³Ò»ÉèÖÃ£¬ÒÆ¶¯¹ı³ÌÖĞ£¬ĞèÒªĞ£Õı³µÍ·µÄ£¬k
		Car_Keep_Angle_Move_Set_Fix_b=Car_Keep_Angle_Move_Default_Fix_b;				//Í³Ò»ÉèÖÃ£¬ÒÆ¶¯¹ı³ÌÖĞ£¬ĞèÒªĞ£Õı³µÍ·µÄ£¬k
		Car_Keep_Angle_Turn_Set_Fix_k=Car_Keep_Angle_Turn_Default_Fix_k;				//Í³Ò»ÉèÖÃ£¬Ô­µØĞı×ª¹ı³ÌÖĞ£¬ĞèÒªĞ£Õı³µÍ·µÄ£¬k
		Car_Keep_Angle_Turn_Set_Fix_b=Car_Keep_Angle_Turn_Default_Fix_b;				//Í³Ò»ÉèÖÃ£¬Ô­µØĞı×ª¹ı³ÌÖĞ£¬ĞèÒªĞ£Õı³µÍ·µÄ£¬k
		Car_Keep_Angle_Turn_Set_Angle_range=Car_Keep_Angle_Turn_Default_Angle_range;	//Í³Ò»ÉèÖÃ£¬Ô­µØĞı×ª¹ı³ÌÖĞ£¬±£³ÖÄ¿±ê½Ç¶È ãĞÖµ
		Car_Keep_Angle_Turn_Set_keep_time=Car_Keep_Angle_Turn_Default_keep_time;		//Í³Ò»ÉèÖÃ£¬Ô­µØĞı×ª¹ı³ÌÖĞ£¬±£³ÖÄ¿±ê½Ç¶È Ê±¼ä
		
		Car_Turn_State_Flag=0;								//Ğı×ª·µ»Ø×´Ì¬±êÖ¾ ¡£0£º¿ÕÏĞ£¨ÊÖ¶¯ÖÃÎ»£© £»1£º¼¤»î¹¦ÄÜ £»2£ºÕıÔÚ½øĞĞĞı×ª£»3£ºÍê³ÉÈÎÎñ
		Car_Keep_Angle_Location_Move_State_Flag=0;			//Î»ÖÃ¿ØÖÆ·½Ê½ÖĞ£¬Î»ÖÃ¡¢½Ç¶Èµ½Î»ÁËµÄ±êÖ¾¡£0£º¿ÕÏĞ£¨Íê³É£©£»1£ºÕıÔÚ×öÎ»ÖÃÈÎÎñ:£»2£ºÎ»ÖÃÍê³É£¬ÕıÔÚ×öÔ­µØĞ£Õı £» 3£ºËùÓĞ¶¯×÷Íê³É	
	}
}

//*******************  UART4_RTU Õû³µ¿ØÖÆ£¬³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÔË¶¯  ******************
float UART4_RTU_Car_Aim_angle;			//Í¨¹ı UART4_RTU ÉèÖÃµÄ ±£³ÖµÄ³µÍ··½Ïò ½Ç¶È
float UART4_RTU_Car_Move_angle;			//Í¨¹ı UART4_RTU ÉèÖÃµÄ ³µÒÆ¶¯·½Ïò ½Ç¶È
int UART4_RTU_Car_Speed;				//Í¨¹ı UART4_RTU ÉèÖÃµÄ ³µËÙ¶È´óĞ¡
void UART4_RTU_Car_Keep_Angle_Z_Speed_Move(u8 *buf)
{
	UART4_RTU_Car_Aim_angle = (float)((buf[0]<<8 | buf[1])-10000)/10;	//Í¨¹ı UART4_RTU ÉèÖÃµÄ ±£³ÖµÄ³µÍ··½Ïò ½Ç¶È
	UART4_RTU_Car_Move_angle = (float)((buf[2]<<8 | buf[3])-10000)/10;	//Í¨¹ı UART4_RTU ÉèÖÃµÄ ³µÒÆ¶¯·½Ïò ½Ç¶È
	UART4_RTU_Car_Speed = (buf[4]<<8 | buf[5])-10000;					//Í¨¹ı UART4_RTU ÉèÖÃµÄ ³µËÙ¶È´óĞ¡
}

//*******************  UART4_RTU Õû³µ¿ØÖÆ£¬³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÔË¶¯Ò»¶ÎÊ±¼ä  ******************
u16 UART4_RTU_Car_Move_Time;				//Í¨¹ı UART4_RTU ÉèÖÃµÄ ÔË¶¯Ê±¼ä
void UART4_RTU_Car_Keep_Angle_Z_Speed_Move_Time(u8 *buf)
{
	UART4_RTU_Car_Aim_angle = (float)((buf[0]<<8 | buf[1])-10000)/10;	//Í¨¹ı UART4_RTU ÉèÖÃµÄ ±£³ÖµÄ³µÍ··½Ïò ½Ç¶È
	UART4_RTU_Car_Move_angle = (float)((buf[2]<<8 | buf[3])-10000)/10;	//Í¨¹ı UART4_RTU ÉèÖÃµÄ ³µÒÆ¶¯·½Ïò ½Ç¶È
	UART4_RTU_Car_Speed = (buf[4]<<8 | buf[5])-10000;					//Í¨¹ı UART4_RTU ÉèÖÃµÄ ³µËÙ¶È´óĞ¡
	UART4_RTU_Car_Move_Time = (buf[6]<<8 | buf[7]);						//Í¨¹ı UART4_RTU ÉèÖÃµÄ ÔË¶¯Ê±¼ä
}

//*******************  UART4_RTU Õû³µ¿ØÖÆ£¬³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬¸ø¶¨xyËÙ¶ÈÔË¶¯£¬x->³µÉíÓÒ²àÕı£¬y->³µÍ·Ç°Õı  ******************
int UART4_RTU_Car_X_Speed;					//Í¨¹ı UART4_RTU ÉèÖÃµÄ x·½ÏòËÙ¶È´óĞ¡
int UART4_RTU_Car_Y_Speed;					//Í¨¹ı UART4_RTU ÉèÖÃµÄ y·½ÏòËÙ¶È´óĞ¡
void UART4_RTU_Car_Keep_Angle_XY_Speed_Move(u8 *buf)
{
	UART4_RTU_Car_Aim_angle = (float)((buf[0]<<8 | buf[1])-10000)/10;	//Í¨¹ı UART4_RTU ÉèÖÃµÄ ±£³ÖµÄ³µÍ··½Ïò ½Ç¶È
	UART4_RTU_Car_X_Speed = (buf[2]<<8 | buf[3])-10000;					//Í¨¹ı UART4_RTU ÉèÖÃµÄ ³µÒÆ¶¯·½Ïò ½Ç¶È
	UART4_RTU_Car_Y_Speed = (buf[4]<<8 | buf[5])-10000;					//Í¨¹ı UART4_RTU ÉèÖÃµÄ ³µËÙ¶È´óĞ¡
}

//*******************  UART4_RTU Õû³µ¿ØÖÆ£¬³µÔ­µØĞı×ª½Ç¶È£¨½Ç¶È±Õ»·£©  ******************
void UART4_RTU_Car_Turn(u8 *buf)
{
	UART4_RTU_Car_Aim_angle = (float)((buf[0]<<8 | buf[1])-10000)/10;	//Í¨¹ı UART4_RTU ÉèÖÃµÄ ±£³ÖµÄ³µÍ··½Ïò ½Ç¶È
}
int UART4_RTU_Car_Location;					//Í¨¹ı UART4_RTU ÉèÖÃµÄ Ä¿±êÒÆ¶¯¾àÀë
//*******************  UART4_RTU Õû³µ¿ØÖÆ£¬³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÎ»ÒÆ ¾àÀë  ******************
void UART4_RTU_Car_Keep_Angle_Location_Move(u8 *buf)
{
	UART4_RTU_Car_Aim_angle = (float)((buf[0]<<8 | buf[1])-10000)/10;	//Í¨¹ı UART4_RTU ÉèÖÃµÄ ±£³ÖµÄ³µÍ··½Ïò ½Ç¶È
	UART4_RTU_Car_Move_angle = (float)((buf[2]<<8 | buf[3])-10000)/10;	//Í¨¹ı UART4_RTU ÉèÖÃµÄ ³µÒÆ¶¯·½Ïò ½Ç¶È
	UART4_RTU_Car_Speed = (buf[4]<<8 | buf[5])-10000;					//Í¨¹ı UART4_RTU ÉèÖÃµÄ ³µËÙ¶È´óĞ¡
	UART4_RTU_Car_Location = (buf[6]<<24|buf[7]<<16|buf[8]<<8|buf[9])-0x7FFFFFFF;	//Í¨¹ı UART4_RTU ÉèÖÃµÄ Ä¿±êÒÆ¶¯¾àÀë
}

//*******************  UART4_RTU Õû³µ¿ØÖÆ£¬Í£Ö¹ÒÆ¶¯  ******************
void UART4_RTU_Car_Stop(u8 *buf)
{
	if( buf[0]==1)
	{
		Car_Stop();											//³µÍ£Ö¹ÔË¶¯
		Car_Turn_State_Flag=0;								//Ğı×ª·µ»Ø×´Ì¬±êÖ¾ ¡£0£º¿ÕÏĞ£¨ÊÖ¶¯ÖÃÎ»£© £»1£º¼¤»î¹¦ÄÜ £»2£ºÕıÔÚ½øĞĞĞı×ª£»3£ºÍê³ÉÈÎÎñ
		Car_Keep_Angle_Location_Move_State_Flag=0;			//Î»ÖÃ¿ØÖÆ·½Ê½ÖĞ£¬Î»ÖÃ¡¢½Ç¶Èµ½Î»ÁËµÄ±êÖ¾¡£0£º¿ÕÏĞ£¨Íê³É£©£»1£ºÕıÔÚ×öÎ»ÖÃÈÎÎñ:£»2£ºÎ»ÖÃÍê³É£¬ÕıÔÚ×öÔ­µØĞ£Õı £» 3£ºËùÓĞ¶¯×÷Íê³É	
	}
}


//*******************  UART4_RTU µÄ¹¦ÄÜÂë£¬¶ÔÓ¦ ³µÒÆ¶¯µÄ·½Ê½¡£ÔÚF103Ö÷³ÌĞò´óÑ­»·ÀïÓÃ  ******************
//extern u8 Car_Move_Aim_Time_State_Flag;	//³µÔË¶¯¡°Ò»¶ÎÊ±¼ä¡±º¯Êı·µ»Ø×´Ì¬ 0£º¿ÕÏĞ£¨Íê³É£©£»2£ºÕıÔÚÔËĞĞ £» 3£ºÍê³É
//extern u8 Car_Turn_State_Flag;			//Ğı×ª·µ»Ø×´Ì¬±êÖ¾ ¡£0£º¿ÕÏĞ£¨ÊÖ¶¯ÖÃÎ»£© £»1£º¼¤»î¹¦ÄÜ £»2£ºÕıÔÚ½øĞĞĞı×ª£»3£ºÍê³ÉÈÎÎñ
//extern u8 Car_Keep_Angle_Location_Move_State_Flag;			//Î»ÖÃ¿ØÖÆ·½Ê½ÖĞ£¬Î»ÖÃ¡¢½Ç¶Èµ½Î»ÁËµÄ±êÖ¾¡£0£º¿ÕÏĞ£¨Íê³É£©£»1£ºÕıÔÚ×öÎ»ÖÃÈÎÎñ:£»2£ºÎ»ÖÃÍê³É£¬ÕıÔÚ×öÔ­µØĞ£Õı £» 3£ºËùÓĞ¶¯×÷Íê³É
void UART4_RTU_Car_Move(void)
{

	switch(UART4_RTU_Function_To_Car_Move)
	{
	//*******************  ÉèÖÃÕû³µÔË¶¯º¯Êı²ÎÊı  ******************
		case UART4_RTU_Function_Car_Z_Speed:		//ÅäÖÃ Õû³µ ³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÔË¶¯
			Car_Keep_Angle_Z_Speed_Move(UART4_RTU_Car_Aim_angle,UART4_RTU_Car_Move_angle,UART4_RTU_Car_Speed);	//	³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÔË¶¯
			break;	
		case UART4_RTU_Function_Car_Z_Speed_Time:	//ÅäÖÃ Õû³µ ³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÔË¶¯
			if(Car_Move_Aim_Time_State_Flag<3)
				Car_Keep_Angle_Z_Speed_Move_Time(UART4_RTU_Car_Aim_angle,UART4_RTU_Car_Move_angle,UART4_RTU_Car_Speed,UART4_RTU_Car_Move_Time);	//³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÔË¶¯ Ò»¶ÎÊ±¼ä
			break;	
		case UART4_RTU_Function_Car_XY_Speed:		//ÅäÖÃ Õû³µ ³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬¸ø¶¨xyËÙ¶ÈÔË¶¯£¬x->³µÉíÓÒ²àÕı£¬y->³µÍ·Ç°Õı
			Car_Keep_Angle_XY_Speed_Move(UART4_RTU_Car_Aim_angle,UART4_RTU_Car_X_Speed,UART4_RTU_Car_Y_Speed);	//	³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬¸ø¶¨xyËÙ¶ÈÔË¶¯£¬x->³µÉíÓÒ²àÕı£¬y->³µÍ·Ç°Õı
			break;	
		case UART4_RTU_Function_Car_Turn:			//ÅäÖÃ Õû³µ ³µÔ­µØĞı×ª½Ç¶È£¨½Ç¶È±Õ»·£©
			if(Car_Turn_State_Flag<3)
				Car_Turn(UART4_RTU_Car_Aim_angle);									//³µÔ­µØĞı×ª½Ç¶È£¨½Ç¶È±Õ»·£©
			break;	
		case UART4_RTU_Function_Car_Location:		//ÅäÖÃ Õû³µ ³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÎ»ÒÆ ¾àÀë
			if(Car_Keep_Angle_Location_Move_State_Flag<3)
				Car_Keep_Angle_Location_Move(UART4_RTU_Car_Aim_angle,UART4_RTU_Car_Move_angle,UART4_RTU_Car_Speed,UART4_RTU_Car_Location);	//³µÍ·±£³ÖÔÚÄ¿±ê½Ç¶È£¬ÏòÈÎÒâ½Ç¶ÈÎ»ÒÆ ¾àÀë
			break;	
		
	}




}






u8 UART4_RTU_TX_Data[UART4_RTU_TX_MAX]; 		// UART4_RTU Êı¾İ¶Î ·¢ËÍ»º³åÇø
//**************************************  UART4_RTU Êı¾İ·¢ËÍ  **************************************
//Ö¡Í·		Ä¿±êµØÖ·Âë	¹¦ÄÜÂë	  Êı¾İÎ»          Êı¾İ¶Î 			Ö¡Î²	
//0x55		1×Ö½Ú       1×Ö½Ú     1×Ö½Ú£¨2~126) 	 DATA(Len)  	0xAA
void UART4_RTU_TX_Mesage(u8 function,u8 len,u8 *pData)	//¹¦ÄÜÂë£¬Êı¾İ³¤¶È£¬ÄÚÈİ
{
	u8 rtu_buff[100];
	rtu_buff[0]=UART4_RTU_FH_H;			//Ö¡Í· ¸ßÎ»
	rtu_buff[1]=UART4_RTU_FH_L;			//Ö¡Í· µÍÎ»
	rtu_buff[2]=UART4_RTU_ADDRES_H750;	//Ä¿±êµØÖ·Âë
	rtu_buff[3]=function;				//¹¦ÄÜÂë	
	rtu_buff[4]=len;					//Êı¾İÎ»(¶àÉÙÎ»)
	memcpy(&rtu_buff[5],pData,len);		//Êı¾İ¶Î(ÄÚÈİ)
	rtu_buff[len+5]=UART4_RTU_FE_H;		//Ö¡Î² ¸ßÎ»
	rtu_buff[len+6]=UART4_RTU_FE_L;		//Ö¡Î² µÍÎ»
//	UART4_DMA_Begin_Send(rtu_buff , len+7);
}
void UART4_RTU_TX_Data_Buff_CLR(void)	//Çå¿ÕRTU·¢ËÍbuff
{
	u16 k;
	for(k=0;k<UART4_RTU_TX_MAX;k++){UART4_RTU_TX_Data[k] = 0x00;}
	UART4_RX_Count = 0; 
}


//*******************  UART4_RTU ·¢ËÍĞÅÏ¢ to ÉÏÎ»»ú  ******************
extern float Compass_Value;  			//ÓÃ»§ÓÃµÄ½Ç¶È£¨Õı±±ĞŞÕıºó£©
extern float Rotate_Speed_Now[5];  	 	//µ±Ç°Êµ¼Ê×ªËÙ µ¥Î» ×ª/·ÖÖÓ
//*******************  UART4_RTU ·¢ËÍ ·µ»ØĞÅºÅ to ÉÏÎ»»ú  ******************


u16 test_send_value;
void UART4_RTU_Send_Message(void)
{

	//*******************  ·¢ËÍ ÍÓÂİÒÇÊıÖµ  ******************
	UART4_RTU_TX_Data[0]=(u16)(Compass_Value*10+10000)>>8;
	UART4_RTU_TX_Data[1]=(u16)(Compass_Value*10+10000) & 0x00FF;
	//*******************  ·¢ËÍ ³µÔË¶¯¡°Ò»¶ÎÊ±¼ä¡±º¯Êı·µ»Ø×´Ì¬  ******************	
	UART4_RTU_TX_Data[2]=Car_Move_Aim_Time_State_Flag;//³µÔË¶¯¡°Ò»¶ÎÊ±¼ä¡±º¯Êı·µ»Ø×´Ì¬ 0£º¿ÕÏĞ£¨Íê³É£©£»2£ºÕıÔÚÔËĞĞ £» 3£ºÍê³É
	UART4_RTU_TX_Data[3]=Car_Turn_State_Flag;//Ğı×ª·µ»Ø×´Ì¬±êÖ¾ ¡£0£º¿ÕÏĞ£¨ÊÖ¶¯ÖÃÎ»£© £»1£º¼¤»î¹¦ÄÜ £»2£ºÕıÔÚ½øĞĞĞı×ª£»3£ºÍê³ÉÈÎÎñ	
	UART4_RTU_TX_Data[4]=Car_Keep_Angle_Location_Move_State_Flag;//Î»ÖÃ¿ØÖÆ·½Ê½ÖĞ£¬Î»ÖÃ¡¢½Ç¶Èµ½Î»ÁËµÄ±êÖ¾¡£0£º¿ÕÏĞ£¨Íê³É£©£»1£ºÕıÔÚ×öÎ»ÖÃÈÎÎñ:£»2£ºÎ»ÖÃÍê³É£¬ÕıÔÚ×öÔ­µØĞ£Õı £» 3£ºËùÓĞ¶¯×÷Íê³É
	UART4_RTU_TX_Mesage(UART4_RTU_Function_Responce,5,UART4_RTU_TX_Data);	//ÉÏµç´òÓ¡²âÊÔĞÅÏ¢
}





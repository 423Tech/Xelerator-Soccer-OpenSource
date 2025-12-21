/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "dma.h"
#include "spi.h"
#include "tim.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include "bmi088.h"
#include "motor.h"
#include "protocol.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */
enum task_type {
	TASK_NONE,
	TASK_UPDATE_WHEELS_PWM,
	TASK_PROCESS_GYRO_ANGLE,
	TASK_PROCESS_RECEIVED_FRAME
};
/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */
#define TASK_QUEUE_SIZE (8)
/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */
volatile int read_idx = 0, write_idx = 0;
volatile enum task_type task_queue[TASK_QUEUE_SIZE];
/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */
#include <stdio.h> /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */
#include <string.h> /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */
char uart_buff[64]; /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */
/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */
	uint32_t time; /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */
  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_SPI2_Init();
  MX_TIM1_Init();
  MX_TIM2_Init();
  MX_TIM3_Init();
  MX_TIM4_Init();
  MX_TIM5_Init();
  MX_TIM6_Init();
  MX_TIM8_Init();
  MX_TIM9_Init();
  MX_UART4_Init();
  /* USER CODE BEGIN 2 */
  bmi088_init_gyro();
  motor_init();
  protocol_start_receive_host();
  HAL_Delay(500);
  bmi088_calibrate_gyro_offset(3000);
  time = DWT->CYCCNT; /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */
  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1) {
	  if (read_idx != write_idx) {
		  switch (task_queue[read_idx]) {
	  	  case TASK_UPDATE_WHEELS_PWM:
		  	  motor_update_wheels_pwm();
		  	  break;
	  	  case TASK_PROCESS_GYRO_ANGLE:
		  	  bmi088_process_gyro_angle();
		  	  break;
	  	  case TASK_PROCESS_RECEIVED_FRAME:
	  		  if (!is_calibrating_gyro_offset)
	  			  protocol_process_received_frame();
		  	  break;
	  	  default:
		  	  break;
	  	  }
	  	  read_idx = (read_idx + 1) % TASK_QUEUE_SIZE;
	  }
	  /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */
	  if (DWT->CYCCNT - time > 168000000 && !is_calibrating_gyro_offset) {
  	  	  sprintf(uart_buff, "x: %d, y: %d, z: %d\r\n", (int)(bmi088_gyro_angle[0] * 1000), (int)(bmi088_gyro_angle[1] * 1000), (int)(bmi088_gyro_angle[2] * 1000));
  	  	  HAL_UART_Transmit_IT(&huart4, (uint8_t *)uart_buff, strlen(uart_buff));
  	  	  time = DWT->CYCCNT;
	  }
	  /* !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! */
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;
  RCC_OscInitStruct.HSIState = RCC_HSI_ON;
  RCC_OscInitStruct.HSICalibrationValue = RCC_HSICALIBRATION_DEFAULT;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSI;
  RCC_OscInitStruct.PLL.PLLM = 8;
  RCC_OscInitStruct.PLL.PLLN = 168;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */
void add_task(enum task_type task)
{
	uint32_t primask = __get_PRIMASK();
	__disable_irq();
	task_queue[write_idx] = task;
	write_idx = (write_idx + 1) % TASK_QUEUE_SIZE;
	__set_PRIMASK(primask);
}

void HAL_TIM_PeriodElapsedCallback(TIM_HandleTypeDef *htim)
{
	switch ((uint32_t)htim->Instance) {
	case (uint32_t)TIM6:
		add_task(TASK_UPDATE_WHEELS_PWM);
		break;
	default:
		break;
	}
}

void HAL_GPIO_EXTI_Callback(uint16_t GPIO_Pin)
{
    switch(GPIO_Pin)
    {
    case GPIO_PIN_8:
    	BMI088_CAPTURE_DRDY_TIMESTAMP();
    	bmi088_burst_read_gyro(0x02, 6);
        break;
    default:
        break;
    }
}

void HAL_SPI_TxRxCpltCallback(SPI_HandleTypeDef *hspi)
{
    switch ((uint32_t)hspi->Instance)
    {
    case (uint32_t)SPI2:
    	HAL_GPIO_WritePin(GPIOD, GPIO_PIN_12, GPIO_PIN_SET);
    	add_task(TASK_PROCESS_GYRO_ANGLE);
        break;
    default:
        break;
    }
}

void HAL_UARTEx_RxEventCallback(UART_HandleTypeDef *huart, uint16_t Size)
{
	switch((uint32_t)huart->Instance) {
	case (uint32_t)UART4:
		if (huart->RxEventType == HAL_UART_RXEVENT_IDLE)
			add_task(TASK_PROCESS_RECEIVED_FRAME);
		break;
	default:
		break;
	}
}
/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */

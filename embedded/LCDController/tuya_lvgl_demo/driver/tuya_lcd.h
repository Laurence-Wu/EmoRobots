/**
 * @file tuya_lcd.h
 * @brief LCD driver header for ST7789V controller on T5-E1 IPEX Development Board
 * @author TuyaOS Development Team
 * @date 2025
 */

#ifndef __TUYA_LCD_H__
#define __TUYA_LCD_H__

/* Includes ------------------------------------------------------------------*/
#include "lvgl.h"
#include "tuya_spi.h"
#include "tuya_gpio.h"

/* Exported constants --------------------------------------------------------*/
#define LCD_WIDTH   240
#define LCD_HEIGHT  320

/* LCD Pin Configuration */
#define LCD_CS_PIN  P8
#define LCD_DC_PIN  P9
#define LCD_RST_PIN P10
#define LCD_BL_PIN  P11

/* Exported function prototypes ----------------------------------------------*/

/**
 * @brief Initialize the ST7789V LCD controller
 * @retval None
 */
void lcd_init(void);

/**
 * @brief LVGL compatible flush callback function
 * @param drv: Display driver
 * @param area: Area to flush
 * @param color_p: Color data buffer
 * @retval None
 */
void lcd_flush(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p);

#endif /* __TUYA_LCD_H__ */

/**
 * @file tuya_app_main.c
 * @brief Main application entry point for TuyaOS LVGL demo
 * @author TuyaOS Development Team
 * @date 2025
 */

/* Includes ------------------------------------------------------------------*/
#include "lvgl.h"
#include "tuya_lcd.h"
#include "ui.h"

/* Private defines -----------------------------------------------------------*/
#define DISP_BUF_SIZE (LCD_WIDTH * 10)

/* Private variables ---------------------------------------------------------*/
static lv_disp_draw_buf_t disp_buf;
static lv_color_t buf[DISP_BUF_SIZE];
static lv_disp_drv_t disp_drv;

/* Private function prototypes -----------------------------------------------*/
static void lvgl_init(void);

/* Private functions ---------------------------------------------------------*/

/**
 * @brief Initialize LVGL and display driver
 * @retval None
 */
static void lvgl_init(void)
{
    // Initialize LVGL
    lv_init();
    
    // Initialize display buffer
    lv_disp_draw_buf_init(&disp_buf, buf, NULL, DISP_BUF_SIZE);
    
    // Initialize display driver
    lv_disp_drv_init(&disp_drv);
    disp_drv.hor_res = LCD_WIDTH;
    disp_drv.ver_res = LCD_HEIGHT;
    disp_drv.flush_cb = lcd_flush;
    disp_drv.draw_buf = &disp_buf;
    
    // Register display driver
    lv_disp_drv_register(&disp_drv);
}

/* Public functions ----------------------------------------------------------*/

/**
 * @brief Main application entry point
 * @retval None
 */
void tuya_app_main(void)
{
    // Initialize LCD hardware
    lcd_init();
    
    // Initialize LVGL
    lvgl_init();
    
    // Create the main UI
    create_main_ui();
    
    // Main application loop
    while (1) {
        // Handle LVGL tasks
        lv_timer_handler();
        
        // Add a small delay to prevent excessive CPU usage
        // This should be replaced with proper TuyaOS delay function
        for (volatile uint32_t i = 0; i < 1000; i++);
    }
}

/**
 * @file ui.h
 * @brief UI module header for TuyaOS LVGL demo
 * @author TuyaOS Development Team
 * @date 2025
 */

#ifndef __UI_H__
#define __UI_H__

/* Includes ------------------------------------------------------------------*/
#include "lvgl.h"

/* Font declarations ---------------------------------------------------------*/
LV_FONT_DECLARE(font_dont_disturb_48);
LV_FONT_DECLARE(font_please_disturb_48);

/* Exported function prototypes ----------------------------------------------*/

/**
 * @brief Create and initialize the main UI
 * @retval None
 */
void create_main_ui(void);

#endif /* __UI_H__ */

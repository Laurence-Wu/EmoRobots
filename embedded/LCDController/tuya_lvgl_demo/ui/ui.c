/**
 * @file ui.c
 * @brief UI implementation for TuyaOS LVGL demo
 * @author TuyaOS Development Team
 * @date 2025
 */

/* Includes ------------------------------------------------------------------*/
#include "ui.h"

/* Private variables ---------------------------------------------------------*/
static lv_obj_t *page_dont_disturb;
static lv_obj_t *page_please_disturb;

/* Private function prototypes -----------------------------------------------*/
static void create_dont_disturb_page(void);
static void create_please_disturb_page(void);
static void btn_next_event_cb(lv_event_t *e);
static void btn_back_event_cb(lv_event_t *e);

/* Private functions ---------------------------------------------------------*/

/**
 * @brief Event callback for "Next" button
 * @param e: Event structure
 * @retval None
 */
static void btn_next_event_cb(lv_event_t *e)
{
    lv_event_code_t code = lv_event_get_code(e);
    
    if (code == LV_EVENT_CLICKED) {
        // Load "Please Disturb" page with left sliding animation
        lv_scr_load_anim(page_please_disturb, LV_SCR_LOAD_ANIM_MOVE_LEFT, 300, 0, false);
    }
}

/**
 * @brief Event callback for "Back" button
 * @param e: Event structure
 * @retval None
 */
static void btn_back_event_cb(lv_event_t *e)
{
    lv_event_code_t code = lv_event_get_code(e);
    
    if (code == LV_EVENT_CLICKED) {
        // Load "Don't Disturb" page with right sliding animation
        lv_scr_load_anim(page_dont_disturb, LV_SCR_LOAD_ANIM_MOVE_RIGHT, 300, 0, false);
    }
}

/**
 * @brief Create the "Don't Disturb" page
 * @retval None
 */
static void create_dont_disturb_page(void)
{
    // Create screen object
    page_dont_disturb = lv_obj_create(NULL);
    
    // Set background color to blue
    lv_obj_set_style_bg_color(page_dont_disturb, lv_palette_main(LV_PALETTE_BLUE), 0);
    lv_obj_set_style_bg_opa(page_dont_disturb, LV_OPA_COVER, 0);
    
    // Create main label with Chinese text
    lv_obj_t *label_main = lv_label_create(page_dont_disturb);
    lv_label_set_text(label_main, "不要打扰");
    lv_obj_set_style_text_font(label_main, &font_dont_disturb_48, 0);
    lv_obj_set_style_text_color(label_main, lv_color_white(), 0);
    lv_obj_center(label_main);
    lv_obj_set_pos(label_main, 0, -50);  // Move up a bit
    
    // Create "Next" button
    lv_obj_t *btn_next = lv_btn_create(page_dont_disturb);
    lv_obj_set_size(btn_next, 120, 50);
    lv_obj_align(btn_next, LV_ALIGN_BOTTOM_CENTER, 0, -20);
    lv_obj_add_event_cb(btn_next, btn_next_event_cb, LV_EVENT_ALL, NULL);
    
    // Create button label
    lv_obj_t *btn_label = lv_label_create(btn_next);
    lv_label_set_text(btn_label, "Next >");
    lv_obj_set_style_text_color(btn_label, lv_color_white(), 0);
    lv_obj_center(btn_label);
    
    // Style the button
    lv_obj_set_style_bg_color(btn_next, lv_palette_darken(LV_PALETTE_BLUE, 2), 0);
    lv_obj_set_style_border_color(btn_next, lv_color_white(), 0);
    lv_obj_set_style_border_width(btn_next, 2, 0);
    lv_obj_set_style_radius(btn_next, 10, 0);
}

/**
 * @brief Create the "Please Disturb" page
 * @retval None
 */
static void create_please_disturb_page(void)
{
    // Create screen object
    page_please_disturb = lv_obj_create(NULL);
    
    // Set background color to green
    lv_obj_set_style_bg_color(page_please_disturb, lv_palette_main(LV_PALETTE_GREEN), 0);
    lv_obj_set_style_bg_opa(page_please_disturb, LV_OPA_COVER, 0);
    
    // Create main label with Chinese text
    lv_obj_t *label_main = lv_label_create(page_please_disturb);
    lv_label_set_text(label_main, "请来打扰");
    lv_obj_set_style_text_font(label_main, &font_please_disturb_48, 0);
    lv_obj_set_style_text_color(label_main, lv_color_white(), 0);
    lv_obj_center(label_main);
    lv_obj_set_pos(label_main, 0, -50);  // Move up a bit
    
    // Create "Back" button
    lv_obj_t *btn_back = lv_btn_create(page_please_disturb);
    lv_obj_set_size(btn_back, 120, 50);
    lv_obj_align(btn_back, LV_ALIGN_BOTTOM_CENTER, 0, -20);
    lv_obj_add_event_cb(btn_back, btn_back_event_cb, LV_EVENT_ALL, NULL);
    
    // Create button label
    lv_obj_t *btn_label = lv_label_create(btn_back);
    lv_label_set_text(btn_label, "< Back");
    lv_obj_set_style_text_color(btn_label, lv_color_white(), 0);
    lv_obj_center(btn_label);
    
    // Style the button
    lv_obj_set_style_bg_color(btn_back, lv_palette_darken(LV_PALETTE_GREEN, 2), 0);
    lv_obj_set_style_border_color(btn_back, lv_color_white(), 0);
    lv_obj_set_style_border_width(btn_back, 2, 0);
    lv_obj_set_style_radius(btn_back, 10, 0);
}

/* Public functions ----------------------------------------------------------*/

/**
 * @brief Create and initialize the main UI
 * @retval None
 */
void create_main_ui(void)
{
    // Create both pages
    create_dont_disturb_page();
    create_please_disturb_page();
    
    // Load the "Don't Disturb" page as the initial screen
    lv_scr_load(page_dont_disturb);
}

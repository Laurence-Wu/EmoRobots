/* Stub header for LVGL - for compilation testing only */
#ifndef LVGL_H
#define LVGL_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* Basic LVGL types and structures */
typedef struct {
    int16_t x1;
    int16_t y1;
    int16_t x2;
    int16_t y2;
} lv_area_t;

typedef union {
    struct {
        uint8_t blue  : 5;
        uint8_t green : 6;
        uint8_t red   : 5;
    };
    uint16_t full;
} lv_color_t;

typedef struct lv_disp_drv_t lv_disp_drv_t;
typedef struct lv_obj_t lv_obj_t;
typedef struct lv_event_t lv_event_t;

typedef void (*lv_disp_flush_cb_t)(lv_disp_drv_t * disp_drv, const lv_area_t * area, lv_color_t * color_p);

struct lv_disp_drv_t {
    lv_disp_flush_cb_t flush_cb;
    void * draw_buf;
    uint32_t hor_res;
    uint32_t ver_res;
};

typedef struct {
    void * buf1;
    void * buf2;
    uint32_t size;
} lv_disp_draw_buf_t;

typedef enum {
    LV_EVENT_CLICKED,
    LV_EVENT_ALL
} lv_event_code_t;

typedef enum {
    LV_PALETTE_BLUE,
    LV_PALETTE_GREEN
} lv_palette_t;

typedef enum {
    LV_ALIGN_CENTER,
    LV_ALIGN_BOTTOM_CENTER
} lv_align_t;

typedef enum {
    LV_SCR_LOAD_ANIM_MOVE_LEFT,
    LV_SCR_LOAD_ANIM_MOVE_RIGHT
} lv_scr_load_anim_t;

typedef enum {
    LV_OPA_COVER = 255
} lv_opa_t;

/* Font related */
typedef struct lv_font_t lv_font_t;
typedef struct {
    const uint8_t * glyph_bitmap;
    const void * glyph_dsc;
    const void * cmaps;
    const void * kern_dsc;
    uint16_t kern_scale;
    uint16_t cmap_num;
    uint8_t bpp;
    uint8_t kern_classes;
    uint8_t bitmap_format;
} lv_font_fmt_txt_dsc_t;

typedef struct {
    uint32_t bitmap_index;
    uint32_t adv_w;
    uint16_t box_w;
    uint16_t box_h;
    int16_t ofs_x;
    int16_t ofs_y;
} lv_font_fmt_txt_glyph_dsc_t;

typedef struct {
    uint32_t range_start;
    uint16_t range_length;
    uint16_t glyph_id_start;
    const uint16_t * unicode_list;
    const void * glyph_id_ofs_list;
    uint16_t list_length;
    uint8_t type;
} lv_font_fmt_txt_cmap_t;

struct lv_font_t {
    const void * get_glyph_dsc;
    const void * get_glyph_bitmap;
    uint8_t line_height;
    uint8_t base_line;
    uint8_t subpx;
    int8_t underline_position;
    uint8_t underline_thickness;
    const void * dsc;
};

#define LV_FONT_DECLARE(font_name) extern const lv_font_t font_name;
#define LV_ATTRIBUTE_LARGE_CONST
#define LV_FONT_FMT_TXT_CMAP_FORMAT0_TINY 0
#define LVGL_VERSION_MAJOR 8
#define LV_VERSION_CHECK(a,b,c) 1
#define LV_FONT_SUBPX_NONE 0

/* Function declarations */
void lv_init(void);
void lv_timer_handler(void);
void lv_disp_flush_ready(lv_disp_drv_t * disp_drv);
void lv_disp_draw_buf_init(lv_disp_draw_buf_t * draw_buf, void * buf1, void * buf2, uint32_t size_in_px_cnt);
void lv_disp_drv_init(lv_disp_drv_t * driver);
lv_disp_drv_t * lv_disp_drv_register(lv_disp_drv_t * driver);
lv_obj_t * lv_obj_create(lv_obj_t * parent);
lv_obj_t * lv_label_create(lv_obj_t * parent);
lv_obj_t * lv_btn_create(lv_obj_t * parent);
void lv_label_set_text(lv_obj_t * obj, const char * text);
void lv_obj_set_style_bg_color(lv_obj_t * obj, lv_color_t value, uint32_t selector);
void lv_obj_set_style_bg_opa(lv_obj_t * obj, lv_opa_t value, uint32_t selector);
void lv_obj_set_style_text_font(lv_obj_t * obj, const lv_font_t * value, uint32_t selector);
void lv_obj_set_style_text_color(lv_obj_t * obj, lv_color_t value, uint32_t selector);
void lv_obj_set_style_border_color(lv_obj_t * obj, lv_color_t value, uint32_t selector);
void lv_obj_set_style_border_width(lv_obj_t * obj, int32_t value, uint32_t selector);
void lv_obj_set_style_radius(lv_obj_t * obj, int32_t value, uint32_t selector);
void lv_obj_center(lv_obj_t * obj);
void lv_obj_set_pos(lv_obj_t * obj, int32_t x, int32_t y);
void lv_obj_set_size(lv_obj_t * obj, int32_t w, int32_t h);
void lv_obj_align(lv_obj_t * obj, lv_align_t align, int32_t x_ofs, int32_t y_ofs);
void lv_obj_add_event_cb(lv_obj_t * obj, void * event_cb, lv_event_code_t filter, void * user_data);
void lv_scr_load(lv_obj_t * scr);
void lv_scr_load_anim(lv_obj_t * scr, lv_scr_load_anim_t anim_type, uint32_t time, uint32_t delay, bool auto_del);
lv_event_code_t lv_event_get_code(lv_event_t * e);
lv_color_t lv_palette_main(lv_palette_t p);
lv_color_t lv_palette_darken(lv_palette_t p, uint8_t lvl);
lv_color_t lv_color_white(void);

/* Font function stubs */
bool lv_font_get_glyph_dsc_fmt_txt(const lv_font_t * font, void * dsc_out, uint32_t unicode_letter, uint32_t unicode_letter_next);
const uint8_t * lv_font_get_bitmap_fmt_txt(const lv_font_t * font, uint32_t unicode_letter);

#endif /* LVGL_H */

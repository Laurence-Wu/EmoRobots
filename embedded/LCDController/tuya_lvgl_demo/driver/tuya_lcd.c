/**
 * @file tuya_lcd.c
 * @brief LCD driver implementation for ST7789V controller on T5-E1 IPEX Development Board
 * @author TuyaOS Development Team
 * @date 2025
 */

/* Includes ------------------------------------------------------------------*/
#include "tuya_lcd.h"
#include <string.h>

/* Private defines -----------------------------------------------------------*/
#define LCD_CMD  0
#define LCD_DATA 1

/* ST7789V Commands */
#define ST7789_SWRESET    0x01
#define ST7789_SLPOUT     0x11
#define ST7789_NORON      0x13
#define ST7789_MADCTL     0x36
#define ST7789_COLMOD     0x3A
#define ST7789_PORCTRL    0xB2
#define ST7789_GCTRL      0xB7
#define ST7789_VCOMS      0xBB
#define ST7789_LCMCTRL    0xC0
#define ST7789_VDVVRHEN   0xC2
#define ST7789_VRHS       0xC3
#define ST7789_VDVS       0xC4
#define ST7789_FRCTRL2    0xC6
#define ST7789_PWCTRL1    0xD0
#define ST7789_PVGAMCTRL  0xE0
#define ST7789_NVGAMCTRL  0xE1
#define ST7789_DISPON     0x29
#define ST7789_CASET      0x2A
#define ST7789_RASET      0x2B
#define ST7789_RAMWR      0x2C

/* Private function prototypes -----------------------------------------------*/
static void lcd_write_cmd(uint8_t cmd);
static void lcd_write_data(uint8_t data);
static void lcd_write_data_buf(uint8_t *buf, uint16_t len);
static void lcd_set_address_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1);
static void lcd_delay_ms(uint32_t ms);

/* Private functions ---------------------------------------------------------*/

/**
 * @brief Write command to LCD
 * @param cmd: Command to write
 * @retval None
 */
static void lcd_write_cmd(uint8_t cmd)
{
    tuya_gpio_write(LCD_DC_PIN, 0);  // Command mode
    tuya_gpio_write(LCD_CS_PIN, 0);  // Select LCD
    tuya_spi_write(&cmd, 1);
    tuya_gpio_write(LCD_CS_PIN, 1);  // Deselect LCD
}

/**
 * @brief Write data to LCD
 * @param data: Data to write
 * @retval None
 */
static void lcd_write_data(uint8_t data)
{
    tuya_gpio_write(LCD_DC_PIN, 1);  // Data mode
    tuya_gpio_write(LCD_CS_PIN, 0);  // Select LCD
    tuya_spi_write(&data, 1);
    tuya_gpio_write(LCD_CS_PIN, 1);  // Deselect LCD
}

/**
 * @brief Write data buffer to LCD
 * @param buf: Data buffer
 * @param len: Buffer length
 * @retval None
 */
static void lcd_write_data_buf(uint8_t *buf, uint16_t len)
{
    tuya_gpio_write(LCD_DC_PIN, 1);  // Data mode
    tuya_gpio_write(LCD_CS_PIN, 0);  // Select LCD
    tuya_spi_write(buf, len);
    tuya_gpio_write(LCD_CS_PIN, 1);  // Deselect LCD
}

/**
 * @brief Set LCD address window
 * @param x0: Start X coordinate
 * @param y0: Start Y coordinate
 * @param x1: End X coordinate
 * @param y1: End Y coordinate
 * @retval None
 */
static void lcd_set_address_window(uint16_t x0, uint16_t y0, uint16_t x1, uint16_t y1)
{
    // Column address set
    lcd_write_cmd(ST7789_CASET);
    lcd_write_data(x0 >> 8);
    lcd_write_data(x0 & 0xFF);
    lcd_write_data(x1 >> 8);
    lcd_write_data(x1 & 0xFF);

    // Row address set
    lcd_write_cmd(ST7789_RASET);
    lcd_write_data(y0 >> 8);
    lcd_write_data(y0 & 0xFF);
    lcd_write_data(y1 >> 8);
    lcd_write_data(y1 & 0xFF);

    // Write to RAM
    lcd_write_cmd(ST7789_RAMWR);
}

/**
 * @brief Simple delay function
 * @param ms: Delay in milliseconds
 * @retval None
 */
static void lcd_delay_ms(uint32_t ms)
{
    // Implementation depends on TuyaOS delay function
    // This is a placeholder - replace with actual TuyaOS delay
    for (volatile uint32_t i = 0; i < ms * 1000; i++);
}

/* Public functions ----------------------------------------------------------*/

/**
 * @brief Initialize the ST7789V LCD controller
 * @retval None
 */
void lcd_init(void)
{
    // Configure GPIO pins
    tuya_gpio_config(LCD_CS_PIN, TUYA_GPIO_OUTPUT);
    tuya_gpio_config(LCD_DC_PIN, TUYA_GPIO_OUTPUT);
    tuya_gpio_config(LCD_RST_PIN, TUYA_GPIO_OUTPUT);
    tuya_gpio_config(LCD_BL_PIN, TUYA_GPIO_OUTPUT);

    // Initialize SPI
    tuya_spi_init();

    // Hardware reset
    tuya_gpio_write(LCD_RST_PIN, 0);
    lcd_delay_ms(10);
    tuya_gpio_write(LCD_RST_PIN, 1);
    lcd_delay_ms(120);

    // Turn on backlight
    tuya_gpio_write(LCD_BL_PIN, 1);

    // ST7789V initialization sequence
    lcd_write_cmd(ST7789_SWRESET);  // Software reset
    lcd_delay_ms(150);

    lcd_write_cmd(ST7789_SLPOUT);   // Sleep out
    lcd_delay_ms(10);

    lcd_write_cmd(ST7789_COLMOD);   // Set color mode
    lcd_write_data(0x55);           // 16-bit color

    lcd_write_cmd(ST7789_MADCTL);   // Memory access control
    lcd_write_data(0x00);           // Normal orientation

    lcd_write_cmd(ST7789_CASET);    // Column address set
    lcd_write_data(0x00);
    lcd_write_data(0x00);
    lcd_write_data(0x00);
    lcd_write_data(0xEF);           // 239

    lcd_write_cmd(ST7789_RASET);    // Row address set
    lcd_write_data(0x00);
    lcd_write_data(0x00);
    lcd_write_data(0x01);
    lcd_write_data(0x3F);           // 319

    lcd_write_cmd(ST7789_PORCTRL);  // Porch control
    lcd_write_data(0x0C);
    lcd_write_data(0x0C);
    lcd_write_data(0x00);
    lcd_write_data(0x33);
    lcd_write_data(0x33);

    lcd_write_cmd(ST7789_GCTRL);    // Gate control
    lcd_write_data(0x35);

    lcd_write_cmd(ST7789_VCOMS);    // VCOMS setting
    lcd_write_data(0x19);

    lcd_write_cmd(ST7789_LCMCTRL);  // LCM control
    lcd_write_data(0x2C);

    lcd_write_cmd(ST7789_VDVVRHEN); // VDV and VRH command enable
    lcd_write_data(0x01);

    lcd_write_cmd(ST7789_VRHS);     // VRH set
    lcd_write_data(0x12);

    lcd_write_cmd(ST7789_VDVS);     // VDV set
    lcd_write_data(0x20);

    lcd_write_cmd(ST7789_FRCTRL2);  // Frame rate control 2
    lcd_write_data(0x0F);

    lcd_write_cmd(ST7789_PWCTRL1);  // Power control 1
    lcd_write_data(0xA4);
    lcd_write_data(0xA1);

    // Positive voltage gamma control
    lcd_write_cmd(ST7789_PVGAMCTRL);
    lcd_write_data(0xD0);
    lcd_write_data(0x04);
    lcd_write_data(0x0D);
    lcd_write_data(0x11);
    lcd_write_data(0x13);
    lcd_write_data(0x2B);
    lcd_write_data(0x3F);
    lcd_write_data(0x54);
    lcd_write_data(0x4C);
    lcd_write_data(0x18);
    lcd_write_data(0x0D);
    lcd_write_data(0x0B);
    lcd_write_data(0x1F);
    lcd_write_data(0x23);

    // Negative voltage gamma control
    lcd_write_cmd(ST7789_NVGAMCTRL);
    lcd_write_data(0xD0);
    lcd_write_data(0x04);
    lcd_write_data(0x0C);
    lcd_write_data(0x11);
    lcd_write_data(0x13);
    lcd_write_data(0x2C);
    lcd_write_data(0x3F);
    lcd_write_data(0x44);
    lcd_write_data(0x51);
    lcd_write_data(0x2F);
    lcd_write_data(0x1F);
    lcd_write_data(0x1F);
    lcd_write_data(0x20);
    lcd_write_data(0x23);

    lcd_write_cmd(ST7789_NORON);    // Normal display on
    lcd_delay_ms(10);

    lcd_write_cmd(ST7789_DISPON);   // Display on
    lcd_delay_ms(100);
}

/**
 * @brief LVGL compatible flush callback function
 * @param drv: Display driver
 * @param area: Area to flush
 * @param color_p: Color data buffer
 * @retval None
 */
void lcd_flush(lv_disp_drv_t *drv, const lv_area_t *area, lv_color_t *color_p)
{
    // Set the address window
    lcd_set_address_window(area->x1, area->y1, area->x2, area->y2);

    // Calculate the number of pixels
    uint32_t size = (area->x2 - area->x1 + 1) * (area->y2 - area->y1 + 1);

    // Send pixel data
    lcd_write_data_buf((uint8_t*)color_p, size * 2);  // 2 bytes per pixel (RGB565)

    // Inform LVGL that flushing is done
    lv_disp_flush_ready(drv);
}

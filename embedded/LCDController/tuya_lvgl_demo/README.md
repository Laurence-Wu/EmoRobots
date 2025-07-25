# TuyaOS LVGL Demo - LCD Controller

A complete C project for the TuyaOS platform featuring a two-page interactive UI on the T5-E1 IPEX Development Board's LCD display using the LVGL graphics library.

## Project Structure

```
tuya_lvgl_demo/
├── driver/
│   ├── tuya_lcd.c          # ST7789V LCD driver implementation
│   └── tuya_lcd.h          # LCD driver header
├── ui/
│   ├── ui.c                # UI implementation with page navigation
│   ├── ui.h                # UI module header
│   ├── font_dont_disturb.c # Custom font for "不要打扰" (48px, 4bpp)
│   └── font_please_disturb.c # Custom font for "请来打扰" (48px, 4bpp)
├── tuya_app_main.c         # Main application entry point
├── SConstruct              # TuyaOS build script
└── README.md               # This file
```

## Hardware Specifications

- **Development Board**: T5-E1 IPEX
- **LCD Controller**: ST7789V
- **Resolution**: 240x320 pixels
- **Pin Configuration**:
  - CS (Chip Select): P8
  - DC (Data/Command): P9
  - RST (Reset): P10
  - BL (Backlight): P11

## Features

### UI Pages
1. **"Don't Disturb" Page** (不要打扰)
   - Blue background with white text
   - Custom 48px Chinese font
   - "Next >" button for navigation

2. **"Please Disturb" Page** (请来打扰)
   - Green background with white text
   - Custom 48px Chinese font
   - "< Back" button for navigation

### Technical Features
- Full ST7789V initialization sequence
- LVGL graphics library integration
- Custom Chinese font support (4-bit anti-aliasing)
- Smooth page transitions with sliding animations
- Touch-free navigation using buttons
- Efficient display buffer management

## Build Instructions

### Prerequisites
- TuyaOS development environment
- LVGL library component
- SCons build system

### Building the Project
```bash
# Build the project
scons

# Clean build files
scons clean

# Flash to device
scons flash
```

### Build Targets
- `(default)`: Build the complete project
- `clean`: Remove all build artifacts
- `flash`: Flash the compiled program to the target device

## Code Architecture

### LCD Driver (`driver/`)
- **tuya_lcd.h**: Header with pin definitions and function prototypes
- **tuya_lcd.c**: Complete ST7789V driver with initialization and LVGL integration

### UI Module (`ui/`)
- **ui.h**: UI function declarations and font imports
- **ui.c**: Page creation, event handling, and navigation logic
- **font_*.c**: Custom LVGL fonts generated for Chinese characters

### Main Application
- **tuya_app_main.c**: LVGL initialization, display setup, and main loop

## Font Details

Both custom fonts are configured with:
- **Size**: 48 pixels
- **Bit depth**: 4 bits per pixel (16 levels of anti-aliasing)
- **Format**: LVGL font format with bitmap data
- **Characters**: 
  - `font_dont_disturb_48`: 不要打扰
  - `font_please_disturb_48`: 请来打扰

## Navigation Flow

```
┌─────────────────┐    Next >     ┌─────────────────┐
│   不要打扰       │ ───────────► │   请来打扰       │
│ (Don't Disturb) │              │ (Please Disturb) │
│                 │ ◄─────────── │                 │
└─────────────────┘    < Back     └─────────────────┘
```

## Memory Usage

- **Display Buffer**: 2,400 bytes (240 × 10 pixels × 2 bytes/pixel)
- **Font Data**: ~5KB total for both custom fonts
- **Code Size**: Approximately 15-20KB compiled

## Customization

### Adding New Pages
1. Create page creation function in `ui.c`
2. Add navigation event callbacks
3. Update `create_main_ui()` to include new page

### Custom Fonts
1. Use LVGL font converter tool
2. Generate C files with required character sets
3. Declare fonts in `ui.h`
4. Apply fonts using `lv_obj_set_style_text_font()`

### Display Settings
- Modify `LCD_WIDTH` and `LCD_HEIGHT` in `tuya_lcd.h`
- Adjust `DISP_BUF_SIZE` in `tuya_app_main.c`
- Update pin definitions if using different hardware

## Dependencies

- **TuyaOS SDK**: Core platform functions
- **LVGL**: Graphics library (v8.x compatible)
- **tuya_spi**: SPI communication
- **tuya_gpio**: GPIO control

## License

This project is part of the TuyaOS development ecosystem. Please refer to TuyaOS licensing terms for usage and distribution.

## Support

For technical support and questions:
- TuyaOS Documentation
- TuyaOS Developer Community
- LVGL Documentation: https://docs.lvgl.io/

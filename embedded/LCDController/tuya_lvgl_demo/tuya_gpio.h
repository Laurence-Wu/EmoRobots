/* Stub header for TuyaOS GPIO - for compilation testing only */
#ifndef TUYA_GPIO_H
#define TUYA_GPIO_H

#include <stdint.h>

/* GPIO pin definitions */
#define P8  8
#define P9  9
#define P10 10
#define P11 11

/* GPIO configuration types */
typedef enum {
    TUYA_GPIO_INPUT,
    TUYA_GPIO_OUTPUT,
    TUYA_GPIO_INPUT_PULLUP,
    TUYA_GPIO_INPUT_PULLDOWN
} tuya_gpio_mode_t;

/* GPIO function declarations */
int tuya_gpio_config(uint8_t pin, tuya_gpio_mode_t mode);
int tuya_gpio_write(uint8_t pin, uint8_t value);
int tuya_gpio_read(uint8_t pin);

#endif /* TUYA_GPIO_H */

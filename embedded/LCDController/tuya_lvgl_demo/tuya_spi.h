/* Stub header for TuyaOS SPI - for compilation testing only */
#ifndef TUYA_SPI_H
#define TUYA_SPI_H

#include <stdint.h>

/* SPI function declarations */
int tuya_spi_init(void);
int tuya_spi_write(const uint8_t *data, uint16_t len);
int tuya_spi_read(uint8_t *data, uint16_t len);
int tuya_spi_transfer(const uint8_t *tx_data, uint8_t *rx_data, uint16_t len);

#endif /* TUYA_SPI_H */

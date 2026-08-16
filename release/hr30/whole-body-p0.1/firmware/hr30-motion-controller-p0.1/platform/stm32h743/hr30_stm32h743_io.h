#ifndef HR30_STM32H743_IO_H
#define HR30_STM32H743_IO_H

#include <stdint.h>

/* Exact project-owned STM32H743ZIT6 LQFP144 package bindings from the
 * motion-controller P0.1 ECAD.  Port is encoded A=0, B=1, ... G=6. */
typedef struct {
    uint8_t port_index;
    uint8_t pin_number;
    uint8_t package_pin;
} hr30_stm32_pin_t;

#define HR30_PORT_A UINT8_C(0)
#define HR30_PORT_B UINT8_C(1)
#define HR30_PORT_C UINT8_C(2)
#define HR30_PORT_D UINT8_C(3)
#define HR30_PORT_E UINT8_C(4)
#define HR30_PORT_G UINT8_C(6)

#define HR30_PIN_SAFETY_PERMIT       ((hr30_stm32_pin_t){HR30_PORT_B, UINT8_C(0),  UINT8_C(46)})
#define HR30_PIN_PRECHARGE_STATUS     ((hr30_stm32_pin_t){HR30_PORT_B, UINT8_C(1),  UINT8_C(47)})
#define HR30_PIN_HEARTBEAT            ((hr30_stm32_pin_t){HR30_PORT_B, UINT8_C(2),  UINT8_C(48)})
#define HR30_PIN_PRECHARGE_REQUEST    ((hr30_stm32_pin_t){HR30_PORT_B, UINT8_C(10), UINT8_C(69)})
#define HR30_PIN_FAULT_DIAGNOSTIC     ((hr30_stm32_pin_t){HR30_PORT_B, UINT8_C(11), UINT8_C(70)})
#define HR30_PIN_ACTION_SPI_CS        ((hr30_stm32_pin_t){HR30_PORT_B, UINT8_C(12), UINT8_C(73)})
#define HR30_PIN_ACTION_SPI_SCK       ((hr30_stm32_pin_t){HR30_PORT_B, UINT8_C(13), UINT8_C(74)})
#define HR30_PIN_ACTION_SPI_MISO      ((hr30_stm32_pin_t){HR30_PORT_B, UINT8_C(14), UINT8_C(75)})
#define HR30_PIN_ACTION_SPI_MOSI      ((hr30_stm32_pin_t){HR30_PORT_B, UINT8_C(15), UINT8_C(76)})
#define HR30_PIN_ACTION_READY         ((hr30_stm32_pin_t){HR30_PORT_G, UINT8_C(11), UINT8_C(126)})

/* Bus order is the canonical bus-binding.csv order, indices 0..7. */
#define HR30_PIN_RS_LLEG_TX           ((hr30_stm32_pin_t){HR30_PORT_A, UINT8_C(9),  UINT8_C(101)})
#define HR30_PIN_RS_LLEG_RX           ((hr30_stm32_pin_t){HR30_PORT_A, UINT8_C(10), UINT8_C(102)})
#define HR30_PIN_RS_LLEG_DIR          ((hr30_stm32_pin_t){HR30_PORT_A, UINT8_C(12), UINT8_C(104)})
#define HR30_PIN_RS_RLEG_TX           ((hr30_stm32_pin_t){HR30_PORT_D, UINT8_C(5),  UINT8_C(119)})
#define HR30_PIN_RS_RLEG_RX           ((hr30_stm32_pin_t){HR30_PORT_D, UINT8_C(6),  UINT8_C(122)})
#define HR30_PIN_RS_RLEG_DIR          ((hr30_stm32_pin_t){HR30_PORT_D, UINT8_C(4),  UINT8_C(118)})
#define HR30_PIN_RS_LARM_TX           ((hr30_stm32_pin_t){HR30_PORT_D, UINT8_C(8),  UINT8_C(77)})
#define HR30_PIN_RS_LARM_RX           ((hr30_stm32_pin_t){HR30_PORT_D, UINT8_C(9),  UINT8_C(78)})
#define HR30_PIN_RS_LARM_DIR          ((hr30_stm32_pin_t){HR30_PORT_D, UINT8_C(12), UINT8_C(81)})
#define HR30_PIN_RS_RARM_TX           ((hr30_stm32_pin_t){HR30_PORT_C, UINT8_C(6),  UINT8_C(96)})
#define HR30_PIN_RS_RARM_RX           ((hr30_stm32_pin_t){HR30_PORT_C, UINT8_C(7),  UINT8_C(97)})
#define HR30_PIN_RS_RARM_DIR          ((hr30_stm32_pin_t){HR30_PORT_G, UINT8_C(8),  UINT8_C(93)})
#define HR30_PIN_RS_WAIST_TX          ((hr30_stm32_pin_t){HR30_PORT_C, UINT8_C(10), UINT8_C(111)})
#define HR30_PIN_RS_WAIST_RX          ((hr30_stm32_pin_t){HR30_PORT_C, UINT8_C(11), UINT8_C(112)})
#define HR30_PIN_RS_WAIST_DIR         ((hr30_stm32_pin_t){HR30_PORT_A, UINT8_C(15), UINT8_C(110)})
#define HR30_PIN_TTL_LDIST_TX         ((hr30_stm32_pin_t){HR30_PORT_C, UINT8_C(12), UINT8_C(113)})
#define HR30_PIN_TTL_LDIST_DIR        ((hr30_stm32_pin_t){HR30_PORT_C, UINT8_C(8),  UINT8_C(98)})
#define HR30_PIN_TTL_RDIST_TX         ((hr30_stm32_pin_t){HR30_PORT_E, UINT8_C(8),  UINT8_C(59)})
#define HR30_PIN_TTL_RDIST_DIR        ((hr30_stm32_pin_t){HR30_PORT_E, UINT8_C(9),  UINT8_C(60)})
#define HR30_PIN_TTL_HEAD_TX          ((hr30_stm32_pin_t){HR30_PORT_E, UINT8_C(1),  UINT8_C(142)})
#define HR30_PIN_TTL_HEAD_DIR         ((hr30_stm32_pin_t){HR30_PORT_D, UINT8_C(15), UINT8_C(86)})

#define HR30_DIRECTION_PIN_COUNT UINT32_C(8)
#define HR30_UART_SIGNAL_PIN_COUNT UINT32_C(13)

/* The target boot path must preload every output latch low before selecting
 * output mode.  It must keep all UART peripheral clocks disabled and every TX
 * or RX signal in analog/no-pull mode.  This file is a binding contract; the
 * target binary still requires independent review and HIL before flashing. */

#endif

#ifndef HR30_STM32H743_REGISTERS_H
#define HR30_STM32H743_REGISTERS_H

#include <stdint.h>

/* Minimal register boundary used by FIRST_POWER_NO_MOTION.  Values are bound
 * to ST RM0433 and cmsis-device-h7 v1.10.7 / commit de8243d2.  No UART is
 * configured or clocked by this profile. */
#define HR30_RCC_BASE                UINT32_C(0x58024400)
#define HR30_RCC_AHB4ENR             (HR30_RCC_BASE + UINT32_C(0x00e0))
#define HR30_RCC_APB1LENR            (HR30_RCC_BASE + UINT32_C(0x00e8))
#define HR30_RCC_APB2ENR             (HR30_RCC_BASE + UINT32_C(0x00f0))

#define HR30_GPIO_A_BASE             UINT32_C(0x58020000)
#define HR30_GPIO_PORT_STRIDE        UINT32_C(0x00000400)
#define HR30_GPIO_MODER_OFFSET       UINT32_C(0x00)
#define HR30_GPIO_OTYPER_OFFSET      UINT32_C(0x04)
#define HR30_GPIO_OSPEEDR_OFFSET     UINT32_C(0x08)
#define HR30_GPIO_PUPDR_OFFSET       UINT32_C(0x0c)
#define HR30_GPIO_IDR_OFFSET         UINT32_C(0x10)
#define HR30_GPIO_ODR_OFFSET         UINT32_C(0x14)
#define HR30_GPIO_BSRR_OFFSET        UINT32_C(0x18)

#define HR30_SYST_CSR                UINT32_C(0xe000e010)
#define HR30_SYST_RVR                UINT32_C(0xe000e014)
#define HR30_SYST_CVR                UINT32_C(0xe000e018)
#define HR30_SCB_VTOR                UINT32_C(0xe000ed08)

#define HR30_RCC_AHB4_GPIO_MASK      UINT32_C(0x0000005f) /* A,B,C,D,E,G */
#define HR30_RCC_APB1_UART_MASK      UINT32_C(0xc01e0000) /* USART2/3, UART4/5/7/8 */
#define HR30_RCC_APB2_UART_MASK      UINT32_C(0x00000030) /* USART1/6 */

#define HR30_GPIO_MODE_INPUT         UINT32_C(0)
#define HR30_GPIO_MODE_OUTPUT        UINT32_C(1)
#define HR30_GPIO_MODE_ANALOG        UINT32_C(3)
#define HR30_GPIO_PULL_NONE          UINT32_C(0)
#define HR30_GPIO_PULL_DOWN          UINT32_C(2)

#define HR30_SYST_CSR_ENABLE         UINT32_C(0x00000001)
#define HR30_SYST_CSR_CLKSOURCE      UINT32_C(0x00000004)
#define HR30_SYST_CSR_COUNTFLAG      UINT32_C(0x00010000)
#define HR30_RESET_HSI_HZ            UINT32_C(64000000)
#define HR30_SYSTICK_1MS_RELOAD      (HR30_RESET_HSI_HZ / UINT32_C(1000) - UINT32_C(1))

#if defined(HR30_TARGET_HOST_SIMULATION)
uint32_t hr30_target_mmio_read32(uint32_t address);
void hr30_target_mmio_write32(uint32_t address, uint32_t value);
#else
static inline uint32_t hr30_target_mmio_read32(uint32_t address) {
    return *(volatile uint32_t *)(uintptr_t)address;
}

static inline void hr30_target_mmio_write32(uint32_t address, uint32_t value) {
    *(volatile uint32_t *)(uintptr_t)address = value;
}
#endif

static inline uint32_t hr30_gpio_base(uint8_t port_index) {
    return HR30_GPIO_A_BASE + (uint32_t)port_index * HR30_GPIO_PORT_STRIDE;
}

#endif

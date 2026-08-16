#include "hr30_stm32h743_target.h"

#include "hr30_stm32h743_io.h"
#include "hr30_stm32h743_registers.h"

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* This word is intentionally read through a volatile object so the target
 * image retains a runtime configuration-identity comparison. */
volatile const uint32_t g_hr30_target_configuration_word = HR30_TARGET_CONFIGURATION_WORD;
static volatile uint16_t g_hr30_bus_write_attempt_mask;

static const hr30_stm32_pin_t direction_pins[HR30_DIRECTION_PIN_COUNT] = {
    HR30_PIN_RS_LLEG_DIR, HR30_PIN_RS_RLEG_DIR,
    HR30_PIN_RS_LARM_DIR, HR30_PIN_RS_RARM_DIR,
    HR30_PIN_RS_WAIST_DIR, HR30_PIN_TTL_LDIST_DIR,
    HR30_PIN_TTL_RDIST_DIR, HR30_PIN_TTL_HEAD_DIR
};

static const hr30_stm32_pin_t uart_signal_pins[HR30_UART_SIGNAL_PIN_COUNT] = {
    HR30_PIN_RS_LLEG_TX, HR30_PIN_RS_LLEG_RX,
    HR30_PIN_RS_RLEG_TX, HR30_PIN_RS_RLEG_RX,
    HR30_PIN_RS_LARM_TX, HR30_PIN_RS_LARM_RX,
    HR30_PIN_RS_RARM_TX, HR30_PIN_RS_RARM_RX,
    HR30_PIN_RS_WAIST_TX, HR30_PIN_RS_WAIST_RX,
    HR30_PIN_TTL_LDIST_TX, HR30_PIN_TTL_RDIST_TX, HR30_PIN_TTL_HEAD_TX
};

static uint32_t pin_register(hr30_stm32_pin_t pin, uint32_t offset) {
    return hr30_gpio_base(pin.port_index) + offset;
}

static void update_two_bit_field(uint32_t address, uint8_t pin_number, uint32_t value) {
    const uint32_t shift = (uint32_t)pin_number * UINT32_C(2);
    const uint32_t mask = UINT32_C(3) << shift;
    uint32_t current = hr30_target_mmio_read32(address);
    current = (current & ~mask) | ((value & UINT32_C(3)) << shift);
    hr30_target_mmio_write32(address, current);
}

static void write_pin(hr30_stm32_pin_t pin, bool high) {
    const uint32_t bit = UINT32_C(1) << pin.pin_number;
    hr30_target_mmio_write32(
        pin_register(pin, HR30_GPIO_BSRR_OFFSET),
        high ? bit : (bit << UINT32_C(16))
    );
}

static bool read_pin(hr30_stm32_pin_t pin) {
    return (hr30_target_mmio_read32(pin_register(pin, HR30_GPIO_IDR_OFFSET)) &
            (UINT32_C(1) << pin.pin_number)) != UINT32_C(0);
}

static void configure_output_low(hr30_stm32_pin_t pin) {
    const uint32_t bit = UINT32_C(1) << pin.pin_number;
    uint32_t value;

    /* Load the low value before output mode, preventing a software-created
     * high pulse at the mode transition. */
    write_pin(pin, false);
    value = hr30_target_mmio_read32(pin_register(pin, HR30_GPIO_OTYPER_OFFSET));
    hr30_target_mmio_write32(pin_register(pin, HR30_GPIO_OTYPER_OFFSET), value & ~bit);
    update_two_bit_field(pin_register(pin, HR30_GPIO_OSPEEDR_OFFSET), pin.pin_number, UINT32_C(0));
    update_two_bit_field(pin_register(pin, HR30_GPIO_PUPDR_OFFSET), pin.pin_number, HR30_GPIO_PULL_NONE);
    update_two_bit_field(pin_register(pin, HR30_GPIO_MODER_OFFSET), pin.pin_number, HR30_GPIO_MODE_OUTPUT);
}

static void configure_input_pulldown(hr30_stm32_pin_t pin) {
    update_two_bit_field(pin_register(pin, HR30_GPIO_MODER_OFFSET), pin.pin_number, HR30_GPIO_MODE_INPUT);
    update_two_bit_field(pin_register(pin, HR30_GPIO_PUPDR_OFFSET), pin.pin_number, HR30_GPIO_PULL_DOWN);
}

static void configure_analog_no_pull(hr30_stm32_pin_t pin) {
    update_two_bit_field(pin_register(pin, HR30_GPIO_PUPDR_OFFSET), pin.pin_number, HR30_GPIO_PULL_NONE);
    update_two_bit_field(pin_register(pin, HR30_GPIO_MODER_OFFSET), pin.pin_number, HR30_GPIO_MODE_ANALOG);
}

static void disable_uart_clocks(void) {
    uint32_t value = hr30_target_mmio_read32(HR30_RCC_APB1LENR);
    hr30_target_mmio_write32(HR30_RCC_APB1LENR, value & ~HR30_RCC_APB1_UART_MASK);
    value = hr30_target_mmio_read32(HR30_RCC_APB2ENR);
    hr30_target_mmio_write32(HR30_RCC_APB2ENR, value & ~HR30_RCC_APB2_UART_MASK);
}

void hr30_target_early_safe(void) {
    static const hr30_stm32_pin_t safe_outputs[] = {
        HR30_PIN_HEARTBEAT, HR30_PIN_PRECHARGE_REQUEST,
        HR30_PIN_FAULT_DIAGNOSTIC, HR30_PIN_ACTION_SPI_MISO,
        HR30_PIN_ACTION_READY
    };
    static const hr30_stm32_pin_t fail_low_inputs[] = {
        HR30_PIN_SAFETY_PERMIT, HR30_PIN_PRECHARGE_STATUS,
        HR30_PIN_ACTION_SPI_CS, HR30_PIN_ACTION_SPI_SCK,
        HR30_PIN_ACTION_SPI_MOSI
    };
    uint32_t index;
    uint32_t value = hr30_target_mmio_read32(HR30_RCC_AHB4ENR);

    hr30_target_mmio_write32(HR30_RCC_AHB4ENR, value | HR30_RCC_AHB4_GPIO_MASK);
    (void)hr30_target_mmio_read32(HR30_RCC_AHB4ENR);
    disable_uart_clocks();

    for (index = 0u; index < (uint32_t)(sizeof(safe_outputs) / sizeof(safe_outputs[0])); ++index) {
        configure_output_low(safe_outputs[index]);
    }
    for (index = 0u; index < HR30_DIRECTION_PIN_COUNT; ++index) {
        configure_output_low(direction_pins[index]);
    }
    for (index = 0u; index < (uint32_t)(sizeof(fail_low_inputs) / sizeof(fail_low_inputs[0])); ++index) {
        configure_input_pulldown(fail_low_inputs[index]);
    }
    for (index = 0u; index < HR30_UART_SIGNAL_PIN_COUNT; ++index) {
        configure_analog_no_pull(uart_signal_pins[index]);
    }
}

void hr30_target_read_inputs(hr30_inputs_t *inputs) {
    if (inputs == NULL) {
        return;
    }
    inputs->configuration_digest_matches =
        (g_hr30_target_configuration_word == HR30_TARGET_CONFIGURATION_WORD);
    inputs->safety_permit_hardwired = read_pin(HR30_PIN_SAFETY_PERMIT);
    inputs->precharge_status = read_pin(HR30_PIN_PRECHARGE_STATUS);
    inputs->reset_request = false; /* no reset-command input exists in P0.1 ECAD */
    inputs->all_actuator_torque_disabled = true; /* software command state only */
    inputs->observed_torque_enabled_mask = UINT32_C(0);
    inputs->observed_bus_tx_mask = g_hr30_bus_write_attempt_mask;
}

void hr30_target_apply_outputs(const hr30_outputs_t *outputs) {
    uint32_t index;
    const bool heartbeat = (outputs != NULL) && outputs->heartbeat_level &&
                           (outputs->state != HR30_STATE_LATCHED_FAULT);
    const bool fault = (outputs == NULL) || outputs->fault_diagnostic ||
                       (outputs->state == HR30_STATE_LATCHED_FAULT);

    /* FIRST_POWER_NO_MOTION deliberately ignores any caller attempt to assert
     * precharge or ACTION_READY.  No target function exists that can clock a
     * UART or select a UART alternate function. */
    disable_uart_clocks();
    write_pin(HR30_PIN_HEARTBEAT, heartbeat);
    write_pin(HR30_PIN_FAULT_DIAGNOSTIC, fault);
    write_pin(HR30_PIN_PRECHARGE_REQUEST, false);
    write_pin(HR30_PIN_ACTION_READY, false);
    write_pin(HR30_PIN_ACTION_SPI_MISO, false);
    for (index = 0u; index < HR30_DIRECTION_PIN_COUNT; ++index) {
        write_pin(direction_pins[index], false);
    }
}

static void configure_polling_systick(void) {
    hr30_target_mmio_write32(HR30_SYST_CSR, UINT32_C(0));
    hr30_target_mmio_write32(HR30_SYST_RVR, HR30_SYSTICK_1MS_RELOAD);
    hr30_target_mmio_write32(HR30_SYST_CVR, UINT32_C(0));
    hr30_target_mmio_write32(HR30_SYST_CSR, HR30_SYST_CSR_ENABLE | HR30_SYST_CSR_CLKSOURCE);
}

static void wait_one_millisecond(void) {
    while ((hr30_target_mmio_read32(HR30_SYST_CSR) & HR30_SYST_CSR_COUNTFLAG) == UINT32_C(0)) {
#if !defined(HR30_TARGET_HOST_SIMULATION)
        __asm volatile ("nop");
#endif
    }
}

void hr30_target_main(void) {
    hr30_controller_t controller;
    hr30_inputs_t inputs;
    uint32_t now_ms = UINT32_C(0);
    uint32_t tick;

    hr30_target_early_safe();
    configure_polling_systick();
    hr30_controller_init(&controller);

    for (;;) {
        for (tick = 0u; tick < HR30_TARGET_LOOP_PERIOD_MS; ++tick) {
            wait_one_millisecond();
            now_ms++;
        }
        hr30_target_read_inputs(&inputs);
        hr30_controller_step(&controller, &inputs, NULL, now_ms);
        hr30_target_apply_outputs(&controller.output);
    }
}

void hr30_target_fault_hold(void) {
    hr30_target_early_safe();
    write_pin(HR30_PIN_FAULT_DIAGNOSTIC, true);
    for (;;) {
#if !defined(HR30_TARGET_HOST_SIMULATION)
        __asm volatile ("wfi");
#endif
    }
}

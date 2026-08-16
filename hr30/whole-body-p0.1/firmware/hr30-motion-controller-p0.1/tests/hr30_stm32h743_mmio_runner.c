#include "hr30_stm32h743_io.h"
#include "hr30_stm32h743_registers.h"
#include "hr30_stm32h743_target.h"

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define REQUIRE(condition) do { if (!(condition)) { \
    (void)fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #condition); return EXIT_FAILURE; \
} } while (0)

typedef struct {
    uint32_t address;
    uint32_t value;
} register_entry_t;

static register_entry_t registers[256];
static size_t register_count;

static register_entry_t *entry(uint32_t address, int create) {
    size_t index;
    for (index = 0u; index < register_count; ++index) {
        if (registers[index].address == address) {
            return &registers[index];
        }
    }
    if ((create == 0) || (register_count >= (sizeof(registers) / sizeof(registers[0])))) {
        return NULL;
    }
    registers[register_count].address = address;
    registers[register_count].value = 0u;
    register_count++;
    return &registers[register_count - 1u];
}

uint32_t hr30_target_mmio_read32(uint32_t address) {
    register_entry_t *found = entry(address, 0);
    return (found == NULL) ? 0u : found->value;
}

void hr30_target_mmio_write32(uint32_t address, uint32_t value) {
    register_entry_t *found = entry(address, 1);
    const uint32_t gpio_offset = (address - HR30_GPIO_A_BASE) % HR30_GPIO_PORT_STRIDE;
    if (found == NULL) {
        abort();
    }
    found->value = value;
    if ((address >= HR30_GPIO_A_BASE) &&
        (address < HR30_GPIO_A_BASE + UINT32_C(7) * HR30_GPIO_PORT_STRIDE) &&
        (gpio_offset == HR30_GPIO_BSRR_OFFSET)) {
        const uint32_t base = address - HR30_GPIO_BSRR_OFFSET;
        register_entry_t *odr = entry(base + HR30_GPIO_ODR_OFFSET, 1);
        odr->value |= value & UINT32_C(0x0000ffff);
        odr->value &= ~((value >> UINT32_C(16)) & UINT32_C(0x0000ffff));
    }
}

static uint32_t field(hr30_stm32_pin_t pin, uint32_t offset) {
    return (hr30_target_mmio_read32(hr30_gpio_base(pin.port_index) + offset) >>
            ((uint32_t)pin.pin_number * UINT32_C(2))) & UINT32_C(3);
}

static int pin_level(hr30_stm32_pin_t pin) {
    return (hr30_target_mmio_read32(hr30_gpio_base(pin.port_index) + HR30_GPIO_ODR_OFFSET) &
            (UINT32_C(1) << pin.pin_number)) != UINT32_C(0);
}

int main(void) {
    const hr30_stm32_pin_t direction_pins[] = {
        HR30_PIN_RS_LLEG_DIR, HR30_PIN_RS_RLEG_DIR,
        HR30_PIN_RS_LARM_DIR, HR30_PIN_RS_RARM_DIR,
        HR30_PIN_RS_WAIST_DIR, HR30_PIN_TTL_LDIST_DIR,
        HR30_PIN_TTL_RDIST_DIR, HR30_PIN_TTL_HEAD_DIR
    };
    const hr30_stm32_pin_t uart_pins[] = {
        HR30_PIN_RS_LLEG_TX, HR30_PIN_RS_LLEG_RX,
        HR30_PIN_RS_RLEG_TX, HR30_PIN_RS_RLEG_RX,
        HR30_PIN_RS_LARM_TX, HR30_PIN_RS_LARM_RX,
        HR30_PIN_RS_RARM_TX, HR30_PIN_RS_RARM_RX,
        HR30_PIN_RS_WAIST_TX, HR30_PIN_RS_WAIST_RX,
        HR30_PIN_TTL_LDIST_TX, HR30_PIN_TTL_RDIST_TX, HR30_PIN_TTL_HEAD_TX
    };
    const hr30_stm32_pin_t outputs[] = {
        HR30_PIN_HEARTBEAT, HR30_PIN_PRECHARGE_REQUEST,
        HR30_PIN_FAULT_DIAGNOSTIC, HR30_PIN_ACTION_SPI_MISO,
        HR30_PIN_ACTION_READY
    };
    const hr30_stm32_pin_t inputs[] = {
        HR30_PIN_SAFETY_PERMIT, HR30_PIN_PRECHARGE_STATUS,
        HR30_PIN_ACTION_SPI_CS, HR30_PIN_ACTION_SPI_SCK,
        HR30_PIN_ACTION_SPI_MOSI
    };
    hr30_outputs_t output;
    hr30_inputs_t input;
    size_t index;

    (void)memset(registers, 0, sizeof(registers));
    register_count = 0u;
    hr30_target_mmio_write32(HR30_RCC_APB1LENR, UINT32_MAX);
    hr30_target_mmio_write32(HR30_RCC_APB2ENR, UINT32_MAX);
    hr30_target_early_safe();

    REQUIRE((hr30_target_mmio_read32(HR30_RCC_AHB4ENR) & HR30_RCC_AHB4_GPIO_MASK) ==
            HR30_RCC_AHB4_GPIO_MASK);
    REQUIRE((hr30_target_mmio_read32(HR30_RCC_APB1LENR) & HR30_RCC_APB1_UART_MASK) == 0u);
    REQUIRE((hr30_target_mmio_read32(HR30_RCC_APB2ENR) & HR30_RCC_APB2_UART_MASK) == 0u);
    for (index = 0u; index < sizeof(outputs) / sizeof(outputs[0]); ++index) {
        REQUIRE(field(outputs[index], HR30_GPIO_MODER_OFFSET) == HR30_GPIO_MODE_OUTPUT);
        REQUIRE(!pin_level(outputs[index]));
    }
    for (index = 0u; index < sizeof(direction_pins) / sizeof(direction_pins[0]); ++index) {
        REQUIRE(field(direction_pins[index], HR30_GPIO_MODER_OFFSET) == HR30_GPIO_MODE_OUTPUT);
        REQUIRE(!pin_level(direction_pins[index]));
    }
    for (index = 0u; index < sizeof(inputs) / sizeof(inputs[0]); ++index) {
        REQUIRE(field(inputs[index], HR30_GPIO_MODER_OFFSET) == HR30_GPIO_MODE_INPUT);
        REQUIRE(field(inputs[index], HR30_GPIO_PUPDR_OFFSET) == HR30_GPIO_PULL_DOWN);
    }
    for (index = 0u; index < sizeof(uart_pins) / sizeof(uart_pins[0]); ++index) {
        REQUIRE(field(uart_pins[index], HR30_GPIO_MODER_OFFSET) == HR30_GPIO_MODE_ANALOG);
        REQUIRE(field(uart_pins[index], HR30_GPIO_PUPDR_OFFSET) == HR30_GPIO_PULL_NONE);
    }

    (void)memset(&output, 0, sizeof(output));
    output.state = HR30_STATE_PERMIT_OBSERVED;
    output.heartbeat_level = true;
    output.precharge_request = true;
    output.action_ready = true;
    output.torque_enable_mask = HR30_ALL_AXIS_MASK;
    output.bus_tx_enable_mask = HR30_ALL_BUS_MASK;
    hr30_target_apply_outputs(&output);
    REQUIRE(pin_level(HR30_PIN_HEARTBEAT));
    REQUIRE(!pin_level(HR30_PIN_FAULT_DIAGNOSTIC));
    REQUIRE(!pin_level(HR30_PIN_PRECHARGE_REQUEST));
    REQUIRE(!pin_level(HR30_PIN_ACTION_READY));
    for (index = 0u; index < sizeof(direction_pins) / sizeof(direction_pins[0]); ++index) {
        REQUIRE(!pin_level(direction_pins[index]));
    }

    output.state = HR30_STATE_LATCHED_FAULT;
    output.fault_diagnostic = true;
    hr30_target_apply_outputs(&output);
    REQUIRE(!pin_level(HR30_PIN_HEARTBEAT));
    REQUIRE(pin_level(HR30_PIN_FAULT_DIAGNOSTIC));

    hr30_target_mmio_write32(
        hr30_gpio_base(HR30_PORT_B) + HR30_GPIO_IDR_OFFSET,
        (UINT32_C(1) << HR30_PIN_SAFETY_PERMIT.pin_number) |
        (UINT32_C(1) << HR30_PIN_PRECHARGE_STATUS.pin_number)
    );
    (void)memset(&input, 0, sizeof(input));
    hr30_target_read_inputs(&input);
    REQUIRE(input.configuration_digest_matches);
    REQUIRE(input.safety_permit_hardwired);
    REQUIRE(input.precharge_status);
    REQUIRE(!input.reset_request);
    REQUIRE(input.all_actuator_torque_disabled);
    REQUIRE(input.observed_torque_enabled_mask == 0u);
    REQUIRE(input.observed_bus_tx_mask == 0u);

    REQUIRE(HR30_PIN_TTL_RDIST_TX.package_pin == 59u);
    REQUIRE(HR30_PIN_TTL_RDIST_DIR.package_pin == 60u);
    REQUIRE(HR30_PIN_ACTION_READY.package_pin == 126u);
    REQUIRE(HR30_TARGET_VECTOR_COUNT == 166u);

    (void)puts("PASS: STM32H743 MMIO simulation keeps eight buses and all motion outputs inactive");
    (void)puts("NO TARGET HIL, FUNCTIONAL-SAFETY CREDIT, OR ENERGIZATION AUTHORITY");
    return EXIT_SUCCESS;
}

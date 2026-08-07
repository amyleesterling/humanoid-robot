/* PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION. */
/* Raspberry Pi Pico 1 binding for ordinary diagnostic watchdog logic. */
/* No functional-safety credit. HIL validation remains mandatory. */

#include "pb_watchdog.h"

#include <stdbool.h>
#include <stdint.h>

#include "hardware/gpio.h"
#include "hardware/watchdog.h"
#include "pico/stdlib.h"
#include "pico/time.h"

#define PB_WD_GPIO_HEARTBEAT 2u
#define PB_WD_GPIO_RELAY1_DRIVE 3u
#define PB_WD_GPIO_RELAY2_DRIVE 4u
#define PB_WD_GPIO_RELAY1_NC 6u
#define PB_WD_GPIO_RELAY2_NC 7u
#define PB_WD_PROCESSOR_WATCHDOG_MS 100u
#define PB_WD_LOOP_PERIOD_US 1000u
#define PB_WD_DRIVE_MASK ((1u << PB_WD_GPIO_RELAY1_DRIVE) | (1u << PB_WD_GPIO_RELAY2_DRIVE))

_Static_assert(PB_WD_GPIO_RELAY1_DRIVE != PB_WD_GPIO_RELAY2_DRIVE,
               "relay drive GPIOs must remain distinct");
_Static_assert(PB_WD_PROCESSOR_WATCHDOG_MS < PB_WD_HEARTBEAT_TIMEOUT_MS,
               "processor watchdog must expire before heartbeat timeout");
_Static_assert(PB_WD_LOOP_PERIOD_US <= 1000u,
               "candidate polling interval must remain at most 1 ms");

static void force_relay_drives_off(void) {
    gpio_put_masked(PB_WD_DRIVE_MASK, 0u);
}
static void initialize_drive_off(uint gpio) {
    gpio_init(gpio);
    gpio_put(gpio, false);
    gpio_set_drive_strength(gpio, GPIO_DRIVE_STRENGTH_2MA);
    gpio_set_slew_rate(gpio, GPIO_SLEW_RATE_SLOW);
    gpio_set_dir(gpio, GPIO_OUT);
}

static void initialize_input(uint gpio) {
    gpio_init(gpio);
    gpio_set_dir(gpio, GPIO_IN);
    gpio_disable_pulls(gpio);
    gpio_set_input_hysteresis_enabled(gpio, true);
}

int main(void) {
    /* Configure both commands low before any input or timer setup. */
    initialize_drive_off(PB_WD_GPIO_RELAY1_DRIVE);
    initialize_drive_off(PB_WD_GPIO_RELAY2_DRIVE);
    force_relay_drives_off();

    initialize_input(PB_WD_GPIO_HEARTBEAT);
    initialize_input(PB_WD_GPIO_RELAY1_NC);
    initialize_input(PB_WD_GPIO_RELAY2_NC);

    pb_wd_state_t state;
    pb_wd_init(&state, to_ms_since_boot(get_absolute_time()), gpio_get(PB_WD_GPIO_HEARTBEAT));

    /* A debug halt must not indefinitely preserve an energized output. */
    watchdog_enable(PB_WD_PROCESSOR_WATCHDOG_MS, false);

    while (true) {
        const pb_wd_inputs_t inputs = {
            .now_ms = to_ms_since_boot(get_absolute_time()),
            .heartbeat_level = gpio_get(PB_WD_GPIO_HEARTBEAT),
            .relay1_nc = gpio_get(PB_WD_GPIO_RELAY1_NC),
            .relay2_nc = gpio_get(PB_WD_GPIO_RELAY2_NC),
        };
        const pb_wd_outputs_t outputs = pb_wd_step(&state, inputs);
        const uint32_t drive_value =
            (outputs.relay1_drive ? (1u << PB_WD_GPIO_RELAY1_DRIVE) : 0u) |
            (outputs.relay2_drive ? (1u << PB_WD_GPIO_RELAY2_DRIVE) : 0u);
        gpio_put_masked(PB_WD_DRIVE_MASK, drive_value);

        watchdog_update();
        busy_wait_us_32(PB_WD_LOOP_PERIOD_US);
    }
}

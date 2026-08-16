#include "hr30_motion.h"

#include <stdio.h>
#include <stdlib.h>

#define REQUIRE(condition) do { if (!(condition)) { \
    (void)fprintf(stderr, "FAIL line %d: %s\n", __LINE__, #condition); return EXIT_FAILURE; \
} } while (0)

static hr30_inputs_t safe_inputs(void) {
    hr30_inputs_t input = {0};
    input.configuration_digest_matches = true;
    input.all_actuator_torque_disabled = true;
    return input;
}

static hr30_action_request_t action(hr30_action_kind_t kind, uint32_t sequence, uint32_t now_ms) {
    hr30_action_request_t request = {0};
    request.present = true;
    request.authenticated = true;
    request.supervised = true;
    request.sequence = sequence;
    request.issued_at_ms = now_ms;
    request.expires_after_ms = 500u;
    request.max_speed_permille = 0u;
    request.kind = kind;
    return request;
}

static void finish_boot(hr30_controller_t *controller, hr30_inputs_t *input, uint32_t start_ms) {
    hr30_controller_step(controller, input, NULL, start_ms);
    hr30_controller_step(controller, input, NULL, start_ms + 1u);
    hr30_controller_step(controller, input, NULL, start_ms + 2u);
    hr30_controller_step(controller, input, NULL, start_ms + 3u);
}

int main(void) {
    hr30_controller_t controller;
    hr30_inputs_t input = safe_inputs();
    hr30_action_request_t request;

    hr30_controller_init(&controller);
    REQUIRE(controller.output.state == HR30_STATE_BOOT_HOLD);
    REQUIRE(controller.output.torque_enable_mask == 0u);
    REQUIRE(controller.output.bus_tx_enable_mask == 0u);
    REQUIRE(!controller.output.precharge_request);
    REQUIRE(!controller.output.action_ready);

    finish_boot(&controller, &input, 0u);
    REQUIRE(controller.output.state == HR30_STATE_SAFE_HOLD);
    REQUIRE(controller.output.torque_enable_mask == 0u);

    input.safety_permit_hardwired = true;
    hr30_controller_step(&controller, &input, NULL, 4u);
    REQUIRE(controller.output.state == HR30_STATE_PERMIT_OBSERVED);
    REQUIRE(!controller.output.action_ready);
    REQUIRE(controller.output.torque_enable_mask == 0u);
    REQUIRE(controller.output.bus_tx_enable_mask == 0u);

    request = action(HR30_ACTION_STEP_REQUEST, 1u, 5u);
    hr30_controller_step(&controller, &input, &request, 5u);
    REQUIRE(controller.output.last_reject == HR30_REJECT_PROFILE_LOCKED);
    REQUIRE(controller.output.torque_enable_mask == 0u);

    request = action(HR30_ACTION_STOP_REQUEST, 2u, 6u);
    hr30_controller_step(&controller, &input, &request, 6u);
    REQUIRE(controller.output.last_reject == HR30_REJECT_NONE);
    REQUIRE(controller.output.accepted_stop_sequence == 2u);
    REQUIRE(!controller.output.action_ready);
    REQUIRE(controller.output.torque_enable_mask == 0u);

    hr30_controller_step(&controller, &input, &request, 7u);
    REQUIRE(controller.output.last_reject == HR30_REJECT_REPLAY);

    request = action(HR30_ACTION_STOP_REQUEST, 3u, 8u);
    request.authenticated = false;
    hr30_controller_step(&controller, &input, &request, 8u);
    REQUIRE(controller.output.last_reject == HR30_REJECT_NOT_AUTHENTICATED);

    request = action(HR30_ACTION_STOP_REQUEST, 4u, 0u);
    request.expires_after_ms = 1u;
    hr30_controller_step(&controller, &input, &request, 9u);
    REQUIRE(controller.output.last_reject == HR30_REJECT_EXPIRED);

    input.observed_torque_enabled_mask = 1u << 12;
    input.all_actuator_torque_disabled = false;
    hr30_controller_step(&controller, &input, NULL, 10u);
    REQUIRE(controller.output.state == HR30_STATE_LATCHED_FAULT);
    REQUIRE(controller.output.fault == HR30_FAULT_UNEXPECTED_TORQUE);
    REQUIRE(controller.output.torque_enable_mask == 0u);
    REQUIRE(!controller.output.heartbeat_level);

    hr30_controller_step(&controller, &input, NULL, 11u);
    REQUIRE(controller.output.state == HR30_STATE_LATCHED_FAULT);
    REQUIRE(!controller.output.heartbeat_level);

    input = safe_inputs();
    input.reset_request = true;
    hr30_controller_step(&controller, &input, NULL, 12u);
    REQUIRE(controller.output.state == HR30_STATE_SAFE_HOLD);
    REQUIRE(controller.output.fault == HR30_FAULT_NONE);

    finish_boot(&controller, &input, 13u);
    input.safety_permit_hardwired = true;
    input.reset_request = false;
    hr30_controller_step(&controller, &input, NULL, 17u);
    REQUIRE(controller.output.state == HR30_STATE_PERMIT_OBSERVED);
    input.safety_permit_hardwired = false;
    hr30_controller_step(&controller, &input, NULL, 18u);
    REQUIRE(controller.output.state == HR30_STATE_LATCHED_FAULT);
    REQUIRE(controller.output.fault == HR30_FAULT_PERMIT_DROPOUT);
    REQUIRE(!controller.output.heartbeat_level);

    hr30_controller_init(&controller);
    input = safe_inputs();
    finish_boot(&controller, &input, 20u);
    input.observed_bus_tx_mask = 1u << 7;
    hr30_controller_step(&controller, &input, NULL, 24u);
    REQUIRE(controller.output.fault == HR30_FAULT_UNEXPECTED_BUS_TX);

    hr30_controller_init(&controller);
    input = safe_inputs();
    finish_boot(&controller, &input, 30u);
    input.configuration_digest_matches = false;
    hr30_controller_step(&controller, &input, NULL, 34u);
    REQUIRE(controller.output.fault == HR30_FAULT_CONFIGURATION);

    hr30_controller_init(&controller);
    input = safe_inputs();
    hr30_controller_step(&controller, &input, NULL, 20u);
    hr30_controller_step(&controller, &input, NULL, 19u);
    REQUIRE(controller.output.fault == HR30_FAULT_CLOCK_ROLLBACK);

    REQUIRE(HR30_AXIS_COUNT == 25u);
    REQUIRE(HR30_BUS_COUNT == 8u);
    REQUIRE(HR30_ALL_AXIS_MASK == 0x01ffffffu);
    REQUIRE(HR30_ALL_BUS_MASK == 0x00ffu);

    (void)puts("PASS: HR-30 FIRST_POWER_NO_MOTION compiled-C vectors");
    (void)puts("25 axes / 8 buses / all motion requests rejected / STOP is a no-op");
    (void)puts("NO TARGET HIL, FUNCTIONAL-SAFETY CREDIT, OR ENERGIZATION AUTHORITY");
    return EXIT_SUCCESS;
}

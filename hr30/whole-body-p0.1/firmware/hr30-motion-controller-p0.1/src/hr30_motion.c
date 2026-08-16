#include "hr30_motion.h"

static void clear_bytes(void *destination, size_t count) {
    unsigned char *cursor = (unsigned char *)destination;
    size_t index;
    for (index = 0u; index < count; ++index) {
        cursor[index] = 0u;
    }
}

static void force_no_motion(hr30_controller_t *controller) {
    controller->output.torque_enable_mask = UINT32_C(0);
    controller->output.bus_tx_enable_mask = UINT16_C(0);
    controller->output.precharge_request = false;
    controller->output.action_ready = false;
}

static void latch_fault(hr30_controller_t *controller, hr30_fault_t fault) {
    force_no_motion(controller);
    controller->output.heartbeat_level = false;
    controller->output.state = HR30_STATE_LATCHED_FAULT;
    controller->output.fault = fault;
    controller->output.fault_diagnostic = true;
    controller->output.last_reject = HR30_REJECT_FAULTED;
}

static bool elapsed_within(uint32_t now_ms, uint32_t issued_at_ms, uint16_t duration_ms) {
    return (uint32_t)(now_ms - issued_at_ms) <= (uint32_t)duration_ms;
}

static hr30_reject_t validate_request(
    const hr30_controller_t *controller,
    const hr30_action_request_t *request,
    uint32_t now_ms
) {
    if ((request == NULL) || !request->present) {
        return HR30_REJECT_NO_REQUEST;
    }
    if (!request->authenticated) {
        return HR30_REJECT_NOT_AUTHENTICATED;
    }
    if (!request->supervised) {
        return HR30_REJECT_NOT_SUPERVISED;
    }
    if ((request->expires_after_ms == 0u) ||
        (request->expires_after_ms > HR30_ACTION_MAX_EXPIRY_MS)) {
        return HR30_REJECT_EXPIRY_RANGE;
    }
    if (!elapsed_within(now_ms, request->issued_at_ms, request->expires_after_ms)) {
        return HR30_REJECT_EXPIRED;
    }
    if (request->sequence <= controller->last_sequence) {
        return HR30_REJECT_REPLAY;
    }
    if (request->max_speed_permille > UINT16_C(250)) {
        return HR30_REJECT_SPEED_RANGE;
    }
    if (request->kind != HR30_ACTION_STOP_REQUEST) {
        return HR30_REJECT_PROFILE_LOCKED;
    }
    return HR30_REJECT_NONE;
}

void hr30_controller_init(hr30_controller_t *controller) {
    if (controller == NULL) {
        return;
    }
    clear_bytes(controller, sizeof(*controller));
    controller->output.state = HR30_STATE_BOOT_HOLD;
    controller->output.last_reject = HR30_REJECT_NO_REQUEST;
    force_no_motion(controller);
}

void hr30_controller_step(
    hr30_controller_t *controller,
    const hr30_inputs_t *inputs,
    const hr30_action_request_t *request,
    uint32_t now_ms
) {
    hr30_reject_t rejection;

    if ((controller == NULL) || (inputs == NULL)) {
        if (controller != NULL) {
            latch_fault(controller, HR30_FAULT_INPUT_INVALID);
        }
        return;
    }

    force_no_motion(controller);

    /* A latched controller fault must withdraw the ordinary watchdog
     * heartbeat.  Keeping it alive here would allow a failed controller to
     * continue satisfying the external watchdog-inhibit prerequisite. */
    if (controller->output.state == HR30_STATE_LATCHED_FAULT) {
        controller->output.heartbeat_level = false;
        if (inputs->reset_request && !inputs->safety_permit_hardwired &&
            inputs->all_actuator_torque_disabled &&
            (inputs->observed_torque_enabled_mask == UINT32_C(0)) &&
            (inputs->observed_bus_tx_mask == UINT16_C(0)) &&
            inputs->configuration_digest_matches) {
            controller->output.state = HR30_STATE_SAFE_HOLD;
            controller->output.fault = HR30_FAULT_NONE;
            controller->output.fault_diagnostic = false;
            controller->output.last_reject = HR30_REJECT_NO_REQUEST;
            controller->permit_was_observed = false;
            controller->valid_boot_samples = 0u;
        }
        return;
    }

    controller->output.heartbeat_level = !controller->output.heartbeat_level;

    if (controller->clock_initialized && (now_ms < controller->last_now_ms)) {
        latch_fault(controller, HR30_FAULT_CLOCK_ROLLBACK);
        return;
    }
    controller->clock_initialized = true;
    controller->last_now_ms = now_ms;

    if (!inputs->configuration_digest_matches) {
        latch_fault(controller, HR30_FAULT_CONFIGURATION);
        return;
    }
    if (!inputs->all_actuator_torque_disabled ||
        ((inputs->observed_torque_enabled_mask & HR30_ALL_AXIS_MASK) != UINT32_C(0))) {
        latch_fault(controller, HR30_FAULT_UNEXPECTED_TORQUE);
        return;
    }
    if ((inputs->observed_bus_tx_mask & HR30_ALL_BUS_MASK) != UINT16_C(0)) {
        latch_fault(controller, HR30_FAULT_UNEXPECTED_BUS_TX);
        return;
    }
    if (controller->permit_was_observed && !inputs->safety_permit_hardwired) {
        latch_fault(controller, HR30_FAULT_PERMIT_DROPOUT);
        return;
    }

    if (controller->valid_boot_samples < UINT8_C(3)) {
        controller->valid_boot_samples++;
        controller->output.state = HR30_STATE_BOOT_HOLD;
        controller->output.last_reject = HR30_REJECT_NO_REQUEST;
        return;
    }

    if (!inputs->safety_permit_hardwired) {
        controller->output.state = HR30_STATE_SAFE_HOLD;
        controller->output.last_reject = HR30_REJECT_NO_REQUEST;
        return;
    }

    controller->permit_was_observed = true;
    controller->output.state = HR30_STATE_PERMIT_OBSERVED;
    rejection = validate_request(controller, request, now_ms);
    controller->output.last_reject = rejection;
    if (rejection == HR30_REJECT_NONE) {
        controller->last_sequence = request->sequence;
        controller->output.accepted_stop_sequence = request->sequence;
    }
    /* FIRST_POWER_NO_MOTION never makes action_ready true and never transmits. */
}

const char *hr30_state_name(hr30_state_t state) {
    switch (state) {
        case HR30_STATE_BOOT_HOLD: return "BOOT_HOLD";
        case HR30_STATE_SAFE_HOLD: return "SAFE_HOLD";
        case HR30_STATE_PERMIT_OBSERVED: return "PERMIT_OBSERVED_NO_MOTION";
        case HR30_STATE_LATCHED_FAULT: return "LATCHED_FAULT";
        default: return "UNKNOWN";
    }
}

const char *hr30_fault_name(hr30_fault_t fault) {
    switch (fault) {
        case HR30_FAULT_NONE: return "NONE";
        case HR30_FAULT_CONFIGURATION: return "CONFIGURATION";
        case HR30_FAULT_UNEXPECTED_TORQUE: return "UNEXPECTED_TORQUE";
        case HR30_FAULT_UNEXPECTED_BUS_TX: return "UNEXPECTED_BUS_TX";
        case HR30_FAULT_PERMIT_DROPOUT: return "PERMIT_DROPOUT";
        case HR30_FAULT_CLOCK_ROLLBACK: return "CLOCK_ROLLBACK";
        case HR30_FAULT_INPUT_INVALID: return "INPUT_INVALID";
        default: return "UNKNOWN";
    }
}

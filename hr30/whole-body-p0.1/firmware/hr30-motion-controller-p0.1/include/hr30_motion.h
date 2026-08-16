#ifndef HR30_MOTION_H
#define HR30_MOTION_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define HR30_AXIS_COUNT 25u
#define HR30_BUS_COUNT 8u
#define HR30_ALL_AXIS_MASK UINT32_C(0x01ffffff)
#define HR30_ALL_BUS_MASK UINT16_C(0x00ff)
#define HR30_ACTION_MAX_EXPIRY_MS UINT16_C(2000)
#define HR30_NO_MOTION_PROFILE_ID UINT32_C(0x4833304e)

typedef enum {
    HR30_STATE_BOOT_HOLD = 0,
    HR30_STATE_SAFE_HOLD,
    HR30_STATE_PERMIT_OBSERVED,
    HR30_STATE_LATCHED_FAULT
} hr30_state_t;

typedef enum {
    HR30_FAULT_NONE = 0,
    HR30_FAULT_CONFIGURATION,
    HR30_FAULT_UNEXPECTED_TORQUE,
    HR30_FAULT_UNEXPECTED_BUS_TX,
    HR30_FAULT_PERMIT_DROPOUT,
    HR30_FAULT_CLOCK_ROLLBACK,
    HR30_FAULT_INPUT_INVALID
} hr30_fault_t;

typedef enum {
    HR30_ACTION_NONE = 0,
    HR30_ACTION_SPEAK,
    HR30_ACTION_LOOK_AT,
    HR30_ACTION_OPEN_HAND,
    HR30_ACTION_CLOSE_HAND,
    HR30_ACTION_PRESENT_OBJECT,
    HR30_ACTION_RELEASE_OBJECT,
    HR30_ACTION_STAND_PREPARE,
    HR30_ACTION_WEIGHT_SHIFT_REQUEST,
    HR30_ACTION_STEP_REQUEST,
    HR30_ACTION_STOP_REQUEST
} hr30_action_kind_t;

typedef enum {
    HR30_REJECT_NONE = 0,
    HR30_REJECT_NO_REQUEST,
    HR30_REJECT_PROFILE_LOCKED,
    HR30_REJECT_NOT_AUTHENTICATED,
    HR30_REJECT_NOT_SUPERVISED,
    HR30_REJECT_EXPIRED,
    HR30_REJECT_EXPIRY_RANGE,
    HR30_REJECT_REPLAY,
    HR30_REJECT_SPEED_RANGE,
    HR30_REJECT_FAULTED
} hr30_reject_t;

typedef struct {
    bool configuration_digest_matches;
    bool safety_permit_hardwired;
    bool precharge_status;
    bool reset_request;
    bool all_actuator_torque_disabled;
    uint32_t observed_torque_enabled_mask;
    uint16_t observed_bus_tx_mask;
} hr30_inputs_t;

typedef struct {
    bool present;
    bool authenticated;
    bool supervised;
    uint32_t sequence;
    uint32_t issued_at_ms;
    uint16_t expires_after_ms;
    uint16_t max_speed_permille;
    hr30_action_kind_t kind;
} hr30_action_request_t;

typedef struct {
    bool heartbeat_level;
    bool action_ready;
    bool precharge_request;
    bool fault_diagnostic;
    uint32_t torque_enable_mask;
    uint16_t bus_tx_enable_mask;
    hr30_state_t state;
    hr30_fault_t fault;
    hr30_reject_t last_reject;
    uint32_t accepted_stop_sequence;
} hr30_outputs_t;

typedef struct {
    hr30_outputs_t output;
    uint32_t last_now_ms;
    uint32_t last_sequence;
    uint8_t valid_boot_samples;
    bool permit_was_observed;
    bool clock_initialized;
} hr30_controller_t;

void hr30_controller_init(hr30_controller_t *controller);
void hr30_controller_step(
    hr30_controller_t *controller,
    const hr30_inputs_t *inputs,
    const hr30_action_request_t *request,
    uint32_t now_ms
);
const char *hr30_state_name(hr30_state_t state);
const char *hr30_fault_name(hr30_fault_t fault);

#endif

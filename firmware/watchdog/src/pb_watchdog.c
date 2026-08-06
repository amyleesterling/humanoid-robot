/* PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION. */
/* Portable diagnostic state logic. GPIO/platform binding is not released. */

#include "pb_watchdog.h"

#include <stddef.h>

_Static_assert(PB_WD_HEARTBEAT_TIMEOUT_MS == 3u * PB_WD_HEARTBEAT_NOMINAL_EDGE_MS,
               "heartbeat timeout must equal three nominal edges");
_Static_assert(PB_WD_HEARTBEAT_MINIMUM_EDGE_MS < PB_WD_HEARTBEAT_NOMINAL_EDGE_MS,
               "minimum edge interval must be below nominal");
_Static_assert(PB_WD_STARTUP_VALID_EDGES >= 2u,
               "multiple edges are required to reject a stuck heartbeat");

static uint32_t elapsed_ms(uint32_t now_ms, uint32_t then_ms) {
    return now_ms - then_ms;
}

static void latch_fault(pb_wd_state_t *state, pb_wd_fault_t fault, uint32_t now_ms) {
    if (state->fault == PB_WD_FAULT_NONE) {
        state->fault = fault;
    }
    if (state->relay1_drive || state->relay2_drive) {
        state->relay1_drive = false;
        state->relay2_drive = false;
        state->drive_change_ms = now_ms;
    }
}

void pb_wd_init(pb_wd_state_t *state, uint32_t now_ms, bool heartbeat_level) {
    if (state == NULL) {
        return;
    }
    *state = (pb_wd_state_t){
        .initialized = true,
        .last_heartbeat_level = heartbeat_level,
        .have_edge = false,
        .last_edge_ms = now_ms,
        .valid_edges = 0u,
        .relay1_drive = false,
        .relay2_drive = false,
        .drive_change_ms = now_ms,
        .fault = PB_WD_FAULT_NONE,
    };
}

pb_wd_outputs_t pb_wd_step(pb_wd_state_t *state, pb_wd_inputs_t inputs) {
    if (state == NULL) {
        return (pb_wd_outputs_t){0};
    }
    if (!state->initialized) {
        pb_wd_init(state, inputs.now_ms, inputs.heartbeat_level);
    }

    if (elapsed_ms(inputs.now_ms, state->drive_change_ms) >= PB_WD_RELAY_FEEDBACK_SETTLE_MS) {
        if (inputs.relay1_nc != !state->relay1_drive) {
            latch_fault(state, PB_WD_FAULT_RELAY1_FEEDBACK, inputs.now_ms);
        }
        if (inputs.relay2_nc != !state->relay2_drive) {
            latch_fault(state, PB_WD_FAULT_RELAY2_FEEDBACK, inputs.now_ms);
        }
    }

    if (inputs.heartbeat_level != state->last_heartbeat_level) {
        if (state->have_edge && elapsed_ms(inputs.now_ms, state->last_edge_ms) < PB_WD_HEARTBEAT_MINIMUM_EDGE_MS) {
            latch_fault(state, PB_WD_FAULT_HEARTBEAT_TOO_FAST, inputs.now_ms);
        } else {
            state->have_edge = true;
            state->last_edge_ms = inputs.now_ms;
            state->valid_edges += 1u;
        }
        state->last_heartbeat_level = inputs.heartbeat_level;
    }

    const bool heartbeat_fresh = state->have_edge &&
        elapsed_ms(inputs.now_ms, state->last_edge_ms) < PB_WD_HEARTBEAT_TIMEOUT_MS;
    if (!heartbeat_fresh) {
        state->valid_edges = 0u;
    }
    const bool desired = state->fault == PB_WD_FAULT_NONE && heartbeat_fresh &&
        state->valid_edges >= PB_WD_STARTUP_VALID_EDGES;
    if (state->relay1_drive != desired || state->relay2_drive != desired) {
        state->relay1_drive = desired;
        state->relay2_drive = desired;
        state->drive_change_ms = inputs.now_ms;
    }

    return (pb_wd_outputs_t){
        .relay1_drive = state->relay1_drive,
        .relay2_drive = state->relay2_drive,
        .heartbeat_fresh = heartbeat_fresh,
        .fault_latched = state->fault != PB_WD_FAULT_NONE,
        .fault = state->fault,
        .valid_edges = state->valid_edges,
    };
}

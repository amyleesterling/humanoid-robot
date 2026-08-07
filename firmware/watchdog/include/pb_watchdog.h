#ifndef PB_WATCHDOG_H
#define PB_WATCHDOG_H

/* PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION. */
/* Diagnostic prototype logic only; no functional-safety credit. */

#include <stdbool.h>
#include <stdint.h>

#define PB_WD_HEARTBEAT_NOMINAL_EDGE_MS 100u
#define PB_WD_HEARTBEAT_TIMEOUT_MS 300u
#define PB_WD_HEARTBEAT_MINIMUM_EDGE_MS 20u
#define PB_WD_STARTUP_VALID_EDGES 3u
#define PB_WD_RELAY_FEEDBACK_SETTLE_MS 25u

typedef enum {
    PB_WD_FAULT_NONE = 0,
    PB_WD_FAULT_HEARTBEAT_TOO_FAST = 1,
    PB_WD_FAULT_RELAY1_FEEDBACK = 2,
    PB_WD_FAULT_RELAY2_FEEDBACK = 3,
    PB_WD_FAULT_CLOCK_REGRESSION = 4
} pb_wd_fault_t;

typedef struct {
    uint32_t now_ms;
    bool heartbeat_level;
    bool relay1_nc;
    bool relay2_nc;
} pb_wd_inputs_t;

typedef struct {
    bool relay1_drive;
    bool relay2_drive;
    bool heartbeat_fresh;
    bool fault_latched;
    pb_wd_fault_t fault;
    uint32_t valid_edges;
} pb_wd_outputs_t;

typedef struct {
    bool initialized;
    uint32_t last_now_ms;
    bool last_heartbeat_level;
    bool have_edge;
    uint32_t last_edge_ms;
    uint32_t valid_edges;
    bool relay1_drive;
    bool relay2_drive;
    uint32_t drive_change_ms;
    pb_wd_fault_t fault;
} pb_wd_state_t;

void pb_wd_init(pb_wd_state_t *state, uint32_t now_ms, bool heartbeat_level);
pb_wd_outputs_t pb_wd_step(pb_wd_state_t *state, pb_wd_inputs_t inputs);

#endif

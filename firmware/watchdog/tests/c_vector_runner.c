/* PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION. */
/* Host test harness for ordinary diagnostic watchdog logic; no safety credit. */

#include "pb_watchdog.h"

#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>

int main(void) {
    pb_wd_state_t state = {0};
    char line[128];

    while (fgets(line, (int)sizeof(line), stdin) != NULL) {
        unsigned long long now_value = 0u;
        unsigned int heartbeat = 0u;
        unsigned int relay1_nc = 0u;
        unsigned int relay2_nc = 0u;
        char extra = '\0';

        const int fields = sscanf(
            line,
            "%llu,%u,%u,%u %c",
            &now_value,
            &heartbeat,
            &relay1_nc,
            &relay2_nc,
            &extra
        );
        if (fields != 4 || now_value > UINT32_MAX || heartbeat > 1u || relay1_nc > 1u || relay2_nc > 1u) {
            fputs("invalid vector\n", stderr);
            return 2;
        }

        const pb_wd_inputs_t inputs = {
            .now_ms = (uint32_t)now_value,
            .heartbeat_level = heartbeat != 0u,
            .relay1_nc = relay1_nc != 0u,
            .relay2_nc = relay2_nc != 0u,
        };
        const pb_wd_outputs_t output = pb_wd_step(&state, inputs);
        if (printf(
                "%u,%u,%u,%u,%u,%u\n",
                output.relay1_drive ? 1u : 0u,
                output.relay2_drive ? 1u : 0u,
                output.heartbeat_fresh ? 1u : 0u,
                output.fault_latched ? 1u : 0u,
                (unsigned int)output.fault,
                (unsigned int)output.valid_edges
            ) < 0) {
            return 3;
        }
    }

    return ferror(stdin) != 0 ? 4 : 0;
}

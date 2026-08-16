#ifndef HR30_STM32H743_TARGET_H
#define HR30_STM32H743_TARGET_H

#include "hr30_motion.h"

#include <stdint.h>

#define HR30_TARGET_CONFIGURATION_WORD UINT32_C(0x6764f016)
#define HR30_TARGET_LOOP_PERIOD_MS UINT32_C(100)
#define HR30_TARGET_VECTOR_COUNT UINT32_C(166)

void hr30_target_early_safe(void);
void hr30_target_read_inputs(hr30_inputs_t *inputs);
void hr30_target_apply_outputs(const hr30_outputs_t *outputs);
void hr30_target_main(void) __attribute__((noreturn));
void hr30_target_fault_hold(void) __attribute__((noreturn));

#endif

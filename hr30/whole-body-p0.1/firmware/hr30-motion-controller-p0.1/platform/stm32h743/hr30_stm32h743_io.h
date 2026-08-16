#ifndef HR30_STM32H743_IO_H
#define HR30_STM32H743_IO_H

/* Exact project-owned LQFP144 pin binding from motion-controller P0.1 ECAD. */
#define HR30_PIN_SAFETY_PERMIT_PORT 'B'
#define HR30_PIN_SAFETY_PERMIT_NUMBER 0u
#define HR30_PIN_SAFETY_PERMIT_PACKAGE 46u
#define HR30_PIN_PRECHARGE_STATUS_PORT 'B'
#define HR30_PIN_PRECHARGE_STATUS_NUMBER 1u
#define HR30_PIN_PRECHARGE_STATUS_PACKAGE 47u
#define HR30_PIN_HEARTBEAT_PORT 'B'
#define HR30_PIN_HEARTBEAT_NUMBER 2u
#define HR30_PIN_HEARTBEAT_PACKAGE 48u
#define HR30_PIN_PRECHARGE_REQUEST_PORT 'B'
#define HR30_PIN_PRECHARGE_REQUEST_NUMBER 10u
#define HR30_PIN_PRECHARGE_REQUEST_PACKAGE 69u
#define HR30_PIN_FAULT_DIAGNOSTIC_PORT 'B'
#define HR30_PIN_FAULT_DIAGNOSTIC_NUMBER 11u
#define HR30_PIN_FAULT_DIAGNOSTIC_PACKAGE 70u
#define HR30_PIN_ACTION_READY_PORT 'G'
#define HR30_PIN_ACTION_READY_NUMBER 11u
#define HR30_PIN_ACTION_READY_PACKAGE 126u

/* Platform startup must drive heartbeat, precharge request, fault diagnostic,
 * ACTION_READY and every UART direction pin inactive before clocks/peripherals.
 * This header is a binding contract, not an STM32 target/HIL release. */

#endif

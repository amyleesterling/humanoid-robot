# HR-V0 watchdog logic candidate

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

The proposed watchdog is an RP2040-class diagnostic controller driving two separate default-off low-side relay channels. The portable state logic is in `src/pb_watchdog.c`; `reference_model.py` is an executable specification used for unit tests.

Behavior represented here:

- outputs are off at power-up;
- three valid heartbeat edges are required before both relay commands may turn on;
- a heartbeat edge gap greater than 300 ms turns both commands off;
- heartbeat recovery may restore the watchdog relay commands, but the separate PNOZ/SRA1 monitored physical ARM circuit must remain dropped until a new ARM action;
- too-fast heartbeat edges and relay-NC feedback disagreement latch a diagnostic fault and turn both commands off; and
- there is no online firmware reset input. A diagnostic latch requires controlled service/power-cycle investigation.

This module cannot establish a safety category, PL or SIL. Both channels share the same MCU, power, clock, code and configuration. Exact GPIO assignments, drivers, feedback polarity, input conditioning, EMC behavior, clock supervision, platform startup, build toolchain and HIL traces remain **SELECTION REQUIRED**.

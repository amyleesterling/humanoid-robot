# HR-V0 watchdog logic candidate

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

The proposed watchdog is an RP2040-class diagnostic controller driving two separate default-off low-side relay channels. The portable state logic is in `src/pb_watchdog.c`; `reference_model.py` is an executable specification used for unit tests. `platform/pico/main.c` is the compiled Pico 1 / RP2040 P0.1 binding.

Behavior represented here:

- outputs are off at power-up;
- three valid heartbeat edges are required before both relay commands may turn on;
- a heartbeat edge gap greater than 300 ms turns both commands off;
- heartbeat recovery may restore only the watchdog relay commands; Electrical V3-P1.0 requires a later physical SR1 RESET and then a distinct physical SRA1 ARM before K1/K2 can return;
- KWD NC feedback is conditioned by the proposed `TI_ISO1212DBQ_P0.1` front end and is active-high at the GPIO; low or contradictory feedback remains fault evidence, not proof of a safe relay state;
- too-fast heartbeat edges and relay-NC feedback disagreement latch a diagnostic fault and turn both commands off; and
- there is no online firmware reset input. A diagnostic latch requires controlled service/power-cycle investigation.

This module cannot establish a safety category, PL or SIL. Both channels share the same MCU, power, clock, code and configuration. The P0.4 interface candidate freezes GP2/physical pin 4 for heartbeat, GP3/5 and GP4/6 for the two drives, and GP6/9 and GP7/10 for conditioned NC feedback. The P0.1 Pico binding writes both relay commands low before enabling output direction, uses a 100 ms hardware watchdog with pause-on-debug disabled, and targets a 1 ms polling loop. Electrical V3-P1.0 retains the exact `VO618A-4X017T` heartbeat interface and two separate `TPL7407LPWR` driver packages and freezes exact proposed ISO1212 support-passive order codes. Every circuit still requires receiving, routed-PCB inspection, derating, polarity, timing, COM-slew, EMC, brownout, fault-injection, clock-supervision and HIL evidence under `INSPECT-ELEC-006`, `INSPECT-ELEC-007`, and `TEST-ELEC-005`.

`CMakeLists.txt`, `toolchain-lock.json` and `tools/build_hr_v0_watchdog.ps1` define the controlled build. Two clean builds produced byte-identical ELF, UF2, BIN, HEX, linker map and canonical disassembly artifacts in `output/P0.1/`. See `docs/hr-v0-watchdog-build-p0.1.md`. These files are source/build evidence only: the binary has not been flashed or run on received hardware, and `EG-017` remains partial.

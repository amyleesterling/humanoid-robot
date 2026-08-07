# Sol R12 Findings Rechecked against R39

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07
System baseline: `HR-30-SYS-R0.2`
Correction baseline: `HR-V0-WD-BUILD-P0.1`

This is a project-owned status reconciliation, not a new independent review. Sol's R12 review remains the independent 18 BLOCKER / 30 MAJOR / 8 MINOR assessment of the pre-correction `ee276af...` baseline.

## R39 correction

R39 addresses part of Sol's missing real-time/watchdog implementation evidence:

- binds the portable watchdog logic to exact Raspberry Pi Pico 1 / RP2040 GPIOs matching Electrical V3-P1.0;
- writes both relay commands low before enabling output direction;
- configures a 100 ms processor watchdog with debug pause disabled and a 1 ms target loop;
- pins Pico SDK, compiler, CMake, Ninja, picotool and Python revisions to official sources and publisher hashes;
- compiles Project Button source with warnings treated as errors and produces static size/stack records; and
- records byte-identical ELF, UF2, BIN, HEX, linker-map and canonical-disassembly hashes across two clean builds.

## What this narrows

Sol's statement that the repository contained only intended future watchdog separation is stale for the R39 branch. A native Pico target, exact GPIO binding, controlled toolchain and reproducible binary evidence now exist. The ordinary diagnostic watchdog software architecture is therefore materially more reviewable.

## What remains open

- The UF2 has not been flashed or executed on a received Pico.
- Default-off behavior is not physically proven through startup, brownout, reset, debug halt or processor hang.
- Input polarity, continuity, voltage/noise margin, relay timing and fault-injection traces remain unexecuted.
- The watchdog remains a single-MCU ordinary diagnostic function with shared power, clock, code and configuration. It receives no PL/SIL credit.
- Supervisor deployment, DYNAMIXEL transport, selected kinematics, received actuator identity and external branch-current evidence remain open.
- The XM540/JST conflict, physical build, mechanical proof, functional-safety allocation, HIL and every energization blocker retained through R38 remain open.
- Through E2 the gate result remains 0 closed, 15 partial and 6 open. `EG-017` remains partial.

## Disposition

Sol's central verdict remains correct: HR-V0 is not ready for fabrication or energization, and HR-30W walking is not demonstrated. R39 converts target compilation and reproducibility from a missing claim into controlled evidence; it does not provide hardware or safety validation and does not authorize flashing or energization.

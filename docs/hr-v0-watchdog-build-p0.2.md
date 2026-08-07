# HR-V0 Watchdog Build and Compiled-C Evidence P0.2

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Identifiers: `HR-V0-WD-BUILD-P0.2`; `HR-V0-WD-HOST-VECTOR-P0.1`

System baseline: `HR-30-SYS-R0.2`

Firmware baseline: `HR-V0-FW-P0.1`

Electrical dependency: `Project Button Electrical V3-P1.7` candidate

## Result

P0.2 corrects and tests the portable watchdog's 32-bit time behavior. P0.1 relied on unsigned subtraction in C, so legitimate `uint32_t` wrap was valid, but it did not explicitly latch a small clock regression. The Python model latched a regression but used ordinary integer subtraction, so it incorrectly rejected legitimate wrap. P0.2 gives both implementations the same fail-closed half-range rule:

- a forward elapsed interval below `2^31` ms is valid, including `uint32_t` wrap;
- an elapsed value in the upper half-range latches `PB_WD_FAULT_CLOCK_REGRESSION`; and
- intervals of `2^31` ms or more are deliberately unsupported and fail closed.

This interpretation depends on calling the state step more often than once every 24.8 days. The Pico candidate calls it every 1 ms. Target timing and clock-fault behavior still require HIL.

## Compiled-C differential evidence

The portable C source is compiled into a Windows host vector runner with strict C11 diagnostics. Two clean builds with the publisher-verified LLVM-MinGW 20260616 UCRT x86-64 archive (LLVM 22.1.8) produced the same 91,136-byte executable and SHA-256 `45ab2752513c5f930516306cb8176ce2b2f8325d031b562eba7ed873b24f5180`.

The executable and Python reference model agree at every one of 44 controlled steps in nine scenarios:

1. three-edge startup and 299/300 ms timeout boundaries;
2. 19 ms minimum-edge fault;
3. 20 ms minimum-edge acceptance;
4. 24/25 ms relay-feedback settling boundary and relay 1 fault;
5. relay 2 feedback fault;
6. three-new-edge recovery after timeout;
7. legitimate `uint32_t` clock wrap;
8. a small clock regression; and
9. the exact half-range fail-closed boundary.

The controlled host evidence is in `firmware/watchdog/output/host-vector/P0.1/`. The exact compiler archive, publisher digest and build controls are in `firmware/watchdog/host-test-toolchain-lock.json`. `tools/build_hr_v0_watchdog_host_runner.ps1` reproduces both clean builds.

Primary source verified 2026-08-07:

- [LLVM-MinGW 20260616 with LLVM 22.1.8](https://github.com/mstorsjo/llvm-mingw/releases/tag/20260616)

## RP2040 target build

The corrected P0.2 logic was rebuilt for Raspberry Pi Pico 1 / RP2040 with the same publisher-pinned Pico SDK 2.3.0 and Arm GNU 14.3.rel1 controls used for P0.1. Two clean target builds produced matching ELF, UF2, BIN, HEX, canonical linker map, canonical disassembly, stack-usage files and canonical size report. The controlled artifacts are in `firmware/watchdog/output/P0.2/`.

| Evidence | Result |
|---|---:|
| Target build A / B | exit 0 / 0 |
| Target source errors / warnings | 0 / 0 |
| Controlled target artifacts matching | 9 of 9 |
| Flash payload (`.bin`) | 7,572 bytes |
| `.text` / `.rodata` / `.data` / `.bss` | 6,620 / 316 / 344 / 980 bytes |
| Largest reported Project Button frame | `main`, 72 bytes |
| Host build A / B | exit 0 / 0 |
| Compiled C / Python differential | 9 scenarios, 44 steps, all equal |

P0.1 is retained as historical build evidence and is superseded by P0.2 for further review. It must not be flashed.

## Verification boundary

This pass proves source/model agreement for the controlled vectors, strict host compilation, host-executable reproducibility, strict RP2040 target compilation and target-artifact reproducibility. It does not prove:

- execution, timing or clock behavior on a received Pico;
- GPIO polarity, continuity, voltage margin, brownout/reset/debug-halt behavior or electrical default-off performance;
- relay response, welded-contact injection, total stopping time or common-cause behavior;
- compiler diversity, structural coverage, EMC or functional-safety integrity; or
- permission to fabricate, flash or energize.

`EG-017` remains partial. The next permitted firmware evidence step is disconnected-load target HIL under the applicable controls and qualified review.

# HR-V0 Watchdog Pico Build P0.1

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Identifier: `HR-V0-WD-BUILD-P0.1`
System baseline: `HR-30-SYS-R0.2`
Firmware baseline: `HR-V0-FW-P0.1`
Electrical dependency: `Project Button Electrical V3-P1.0` candidate

## Result

The portable watchdog logic now has a compiling Raspberry Pi Pico 1 / RP2040 platform binding and a controlled two-build artifact set. Two clean Windows AMD64 builds produced identical ELF, UF2, BIN, HEX, linker-map and canonical-disassembly SHA-256 values. Project source compiled with warnings treated as errors. This is build evidence only; the UF2 has not been flashed to a received board and receives no functional-safety credit.

The controlled evidence is in `firmware/watchdog/output/P0.1/`. Exact tools, download URLs, source revision and publisher hashes are frozen in `firmware/watchdog/toolchain-lock.json`. `tools/build_hr_v0_watchdog.ps1` repeats the clean A/B build and fails if any controlled executable artifact differs.

## Frozen platform binding

| Signal | Pico GPIO | Physical pin | Direction | Candidate behavior |
|---|---:|---:|---|---|
| Isolated heartbeat | GP2 | 4 | input | no internal pull; external VO618A/R910 interface controls state |
| KWD1 drive command | GP3 | 5 | output | written low before output direction; 2 mA drive, slow slew |
| KWD2 drive command | GP4 | 6 | output | written low before output direction; 2 mA drive, slow slew |
| KWD1 NC feedback | GP6 | 9 | input | active high after proposed ISO1212 conditioning |
| KWD2 NC feedback | GP7 | 10 | input | active high after proposed ISO1212 conditioning |

The two relay commands are updated with one masked GPIO write. A 100 ms RP2040 hardware watchdog is enabled with pause-on-debug disabled. The loop target is 1 ms. The hardware watchdog is intentionally shorter than the portable logic's 300 ms heartbeat timeout so a stalled loop resets the MCU instead of indefinitely preserving commanded relay outputs. Physical default-off behavior still depends on the proposed TPL7407L input pulldowns, relay wiring and received-board behavior and must be proven by HIL.

## Reproducible build controls

- Raspberry Pi Pico SDK `2.3.0`, tag revision `98a542c1a62fb549ffb5d66a3e5892b06276b670`.
- Arm GNU Toolchain `14.3.rel1`, GCC `14.3.1` build `arm-14.174`.
- CMake `4.3.3`, Ninja `1.13.2`, Raspberry Pi prebuilt picotool `2.3.0`, and Python embeddable `3.13.14`.
- Publisher-provided SHA-256 values are recorded for every downloaded archive.
- USB and UART stdio are disabled; the binary has no operator console path.
- Linker build ID is disabled, `SOURCE_DATE_EPOCH` is fixed at `1786060800` (`2026-08-07T00:00:00Z`), and source, SDK and build paths are normalized.
- Project C source uses strict warnings, `-fstack-usage`, and a 256-byte per-function stack-warning threshold.

Raspberry Pi's Pico SDK configure step emits one non-blocking warning because the TinyUSB submodule is absent. USB stdio is deliberately disabled, so TinyUSB is not part of this target. That warning is recorded rather than suppressed.

Primary documentation verified 2026-08-07:

- [Raspberry Pi Pico SDK 2.3.0 release](https://github.com/raspberrypi/pico-sdk/releases/tag/2.3.0)
- [Raspberry Pi Pico C/C++ SDK documentation](https://www.raspberrypi.com/documentation/microcontrollers/c_sdk.html)
- [Raspberry Pi Pico datasheet](https://datasheets.raspberrypi.com/pico/pico-datasheet.pdf)
- [Arm GNU Toolchain downloads](https://developer.arm.com/downloads/-/arm-gnu-toolchain-downloads)
- [Raspberry Pi Pico SDK tools 2.3.0 release](https://github.com/raspberrypi/pico-sdk-tools/releases/tag/v2.3.0-0)
- [TI TPL7407L data sheet, Rev. D, March 2016](https://www.ti.com/lit/ds/symlink/tpl7407l.pdf)
- [Python 3.13.14 release](https://www.python.org/downloads/release/python-31314/)

## Controlled results

| Evidence | Result |
|---|---|
| Clean configure/build A | exit 0 |
| Clean configure/build B | exit 0 |
| Project-source compiler errors/warnings | 0 / 0 |
| ELF / UF2 / BIN / HEX match | yes / yes / yes / yes |
| Linker map / canonical disassembly match | yes / yes |
| Flash payload (`.bin`) | 7,540 bytes |
| `.text` / `.rodata` / `.data` / `.bss` | 6,588 / 316 / 344 / 980 bytes |
| Largest reported Project Button function frame | `main`, 64 bytes |

The SDK-generated raw `.dis` file is not controlled because its two file-header lines contain the absolute build directory. The raw linker map also records tool and CMake object-path tokens that change when the build root moves. The controlled canonical disassembly uses a relative ELF filename, and the controlled canonical map replaces those host-path tokens. Both are byte-identical across clean builds and across the independently exercised repository build root. Executable artifacts are unaffected.

## Release boundary

This pass closes the missing target-compilation, exact GPIO binding and reproducible-binary portions of `EG-017`; the gate remains `partial`. It does not close:

- received Pico inspection, flash provenance or boot evidence;
- measured output-low behavior through power-up, brownout, reset, debug halt and processor hang;
- input voltage, polarity, continuity, noise-margin or EMC evidence;
- heartbeat timeout, relay settling, welded-contact injection or total stopping-time traces;
- clock-fault, common-cause, HIL or functional-safety validation;
- independent controls/electrical code review; or
- permission to fabricate, flash, energize or command motion.

The next permitted controls step is an unpowered continuity/polarity inspection followed by current-limited control-only HIL under the applicable energization gates and a qualified reviewer. Do not connect actuator power on the strength of this build.

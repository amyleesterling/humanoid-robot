# Independent review request — compute/debug interface P0.1

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

Review baseline: Electrical `V3-P1.12`, `HR-V0-COMPUTE-IF-P0.1`, PCB-P0.5 and firmware binding `HR-V0-COMPUTE-IF-P0.1`.

Please review accuracy and completeness, not presentation polish. Do not infer a cable, contact, housing, programmer, fixture, GPIO runtime, timing value, rating, safety category or authority to connect/energize.

## Reproduce

1. Run `tools/generate_hr_v0_compute_debug_interface.py` and `tools/check_hr_v0_compute_debug_interface.py`.
2. Run `tools/generate_hr_v0_electrical_v3.py --validate` and `tools/check_hr_v0_electrical_v3.py` with KiCad 10.0.5.
3. Confirm `JDBG1` and `TBD-GPIO-HB` are absent from current generated electrical source, schedules, netlist and exports.
4. Confirm `PI1:HDR40-11` maps to `PI_HEARTBEAT`, `PI1:HDR40-6` maps to `COMPUTE_0V`, JWH1 remains pins 1/2 heartbeat/return, and TP15/TP16/TP2 remain SWDIO/SWCLK/SAFETY_0V.
5. Confirm firmware config uses BCM numbering, GPIO17, physical pin 11 and physical pin 6 return, defaults inactive/high-impedance until explicit configuration, and assigns no safety credit.

## Challenge explicitly

- Is physical pin 6 an acceptable return allocation for the exact future harness, or should another manufacturer-documented ground be chosen after routing/EMC review?
- Could GPIO17 be claimed by a device-tree overlay or alternate SPI1 function in the frozen software image?
- Are boot, shutdown, crash, brownout and restart default states sufficiently fail-closed once the actual OS/backend is selected?
- Can any programmer/fixture state back-power the board, assert watchdog outputs, impair SR1/SRA1, or create a short at adjacent test points?
- Are the existing Harwin test points physically accessible with the installed guard and harness, and is an unpowered fixture mechanically repeatable?
- Are the ten recorded holds complete enough to prevent accidental cable or fixture fabrication?

## Expected disposition

Return prioritized BLOCKER/MAJOR/MINOR findings with exact artifact, record, terminal/net and primary-source evidence. Passing ERC and repository checkers prove only modeled consistency. They do not approve cable fabrication, programming connection, powered debug, functional safety, fabrication or energization.

# HR-V0 compute-heartbeat and watchdog-debug interface P0.1

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

Identifier: `HR-V0-COMPUTE-IF-P0.1`

Electrical baseline: `Project Button Electrical V3-P1.12`

Date: 2026-08-08

## Correction

The earlier system schematic showed `JDBG1`, an unselected installed watchdog programming connector with three `TBD-*` terminals. That block was not a physical design and could be mistaken for a released connector. Electrical V3-P1.12 removes it.

The routed watchdog PCB candidate already contains exact Harwin `S1751-46R` test points: `TP15` on `WD_SWDIO`, `TP16` on `WD_SWCLK`, and `TP2` on `SAFETY_0V`. Those are the only modeled debug-access points. The programmer, unpowered fixture, lead assignment, mechanical access, no-back-power controls, work instruction and physical proof remain `SELECTION REQUIRED`.

## Compute heartbeat allocation

The Raspberry Pi heartbeat is allocated to BCM `GPIO17`, physical 40-pin-header pin 11. Physical header pin 6 is the compute-domain return. Current Raspberry Pi documentation identifies Pi 5 as having the standard 40-pin header, identifies GPIO17 at header pin 11 in the SPI1 mapping, and states GPIO outputs are 3.3 V. Raspberry Pi documentation separately identifies physical header pin 6 as ground.

This allocation does not release a cable or runtime implementation. The exact Pi-header contacts/housing or controlled individual-contact method, JWH1 mating hardware, wire, length, routing, strain relief, retention, GPIO backend, permissions, overlay conflicts, boot behavior, waveform and HIL evidence remain open. The output is required to remain input/high-impedance until explicitly configured by the supervisor process.

## No safety credit

The Pi heartbeat, VO618A isolation path, watchdog microcontroller, driver circuits, test points and debug process are ordinary control/diagnostic functions at this stage. They receive no PL/SIL or functional-safety credit. Debug connection, halt, reset, flashing, disconnect, abandoned sessions and tool faults must be proven unable to assert either watchdog output or restore motion eligibility.

No powered debug or programming connection is authorized. Any future procedure must begin from a de-energized actuator source and disabled outputs and must explicitly prevent back-powering or bypass.

## Controlled artifacts

- `electrical/interfaces/hr-v0-compute-debug-interface-p0.1/pin-allocation.csv`
- `electrical/interfaces/hr-v0-compute-debug-interface-p0.1/compatibility-holds.csv`
- `electrical/interfaces/hr-v0-compute-debug-interface-p0.1/source-register.csv`
- `electrical/interfaces/hr-v0-compute-debug-interface-p0.1/interface-summary.json`
- `electrical/interfaces/hr-v0-compute-debug-interface-p0.1/HR-V0_compute-debug-interface-guide.html`
- `firmware/supervisor/compute-interface-config.json`

The package is checked by `tools/check_hr_v0_compute_debug_interface.py`. Passing that checker proves configuration consistency only; it does not prove electrical suitability, physical construction, safe stopping, functional safety, fabrication readiness or permission to energize.

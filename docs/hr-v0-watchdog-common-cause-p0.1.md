# HR-V0 watchdog dependent-failure and common-cause analysis P0.1

Status: **PRELIMINARY - ANALYSIS AND UNEXECUTED TEST CONTROL ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Configuration: `Electrical V3-P1.12 / PCB-P0.5 / HR-V0-CP-P0.4`

Identifier: `HR-V0-WD-CCF-P0.1`

Date: 2026-08-08

## Decision

The ordinary heartbeat diagnostic `DF-01` still receives **zero safety credit**. This pass does not prove that it is non-interfering. It maps the exact V3 terminals, expands the controlled FMEA from 11 broad cases to 32 configuration-bound cases, defines 12 common-cause groups, and creates 28 unexecuted analysis/fault cases plus 16 physical-separation controls.

The current topology has a blocking negative-contribution question:

- `KWD1:A1` and `KWD1:21` carry `SAFETY_24V` while `KWD1:11/14` lies after E-stop contact `S0:R-1/R-2` and returns to `SR1:S12`;
- `KWD2:A1` and `KWD2:21` have the equivalent relationship to `S0:L-1/L-2` and `SR1:S22`; and
- an internal or panel bridge from A1/21 to terminal 14 could inject voltage downstream of an E-stop NC contact.

The exact PNOZ input response, diagnostic coverage, channel consequence and allowable fault treatment require the controlled Pilz application method, the actual wiring, and qualified analysis. No internal fault exclusion is accepted. Until the project either redesigns this boundary or includes and validates the negative contribution in a qualified `SF-01`/`SF-03` architecture, `WDD-001` remains a blocker.

## Exact source boundary

The controlled path register proves the nominal source relationships:

1. `SR1:S11 -> S0:R-1/R-2 -> KWD1:11/14 -> SR1:S12`;
2. `SR1:S21 -> S0:L-1/L-2 -> KWD2:11/14 -> SR1:S22`;
3. `SR1:S12 -> S1 RESET -> SR1:S34`;
4. `SR1:13/14` and `SR1:23/24` feed the two `SRA1` input channels;
5. `SRA1:S12 -> S2 ARM -> K1/K2 NC mirror-contact EDM -> SRA1:S34`; and
6. `SRA1:13/14` and `23/24` command K1/K2 coils separately.

Nominal watchdog recovery therefore cannot restore SR1 without physical RESET or restore SRA1/K1/K2 without the later physical ARM. That is only nominal sequence evidence. The fault cases intentionally challenge bridges, stuck outputs, welded contacts, brownout, feedback corruption, debug back-power and configuration error.

PCB-P0.5 carries ordinary power, heartbeat, drivers, coil sinks and feedback. It does not carry `WD1_SAFETY_IN`, `WD2_SAFETY_IN`, `SR1_S12` or `SR1_S22`; those contact-return conductors are panel wiring. The nominal panel allocation is not a released routing drawing and supplies no protected-wiring fault exclusion.

## Common dependencies

The two watchdog channels are not independent safety channels. They share:

- `WDCTRL1`, firmware, clock/reset behavior and ordinary supervision;
- `SAFETY_24V`, `SAFETY_0V`, DC1 and downstream low-voltage rails;
- one two-layer PCB and assembly/contamination process;
- JWP1 power/coil-sink and JWF1 feedback connector bodies;
- one enclosure, wire-duct/workmanship environment and service process; and
- debug/test access and configuration management.

Separate UDRV1/UDRV2 packages and KWD1/KWD2 modules reduce some single-component coupling, but do not establish a safety architecture or common-cause score.

## Required architecture disposition

`WDD-001` must be closed by a qualified, configuration-specific choice. Acceptable categories of action are deliberately stated without selecting a circuit:

1. redesign the ordinary watchdog interface so its power, feedback and credible internal/external shorts cannot force a credited input downstream of S0;
2. include every KWD and routing failure that can negatively affect `SF-01`/`SF-03` in the credited reliability, diagnostic, common-cause and validation model; or
3. remove the ordinary diagnostic from the credited input boundary and, where control-loss risk requires it, select a separately allocated safety-rated `SF-02` function.

Any redesign requires a new native KiCad revision, synchronized schedules/exports, ERC/DRC, panel/harness definition, updated FMEA, physical validation and qualified review. This document does not authorize an improvised rewire.

## Controlled evidence

- interactive guide: `safety/hr-v0-watchdog-ccf-p0.1/index.html`;
- boundary diagram: `safety/hr-v0-watchdog-ccf-p0.1/watchdog-boundary.svg`;
- exact paths: `exact-path-register.csv`;
- failure modes: `failure-mode-register.csv` and canonical `safety/hr-v0-watchdog-boundary-fmea.csv`;
- common causes: `common-cause-group-register.csv`;
- unexecuted cases: `fault-injection-matrix.csv`;
- physical controls: `separation-control-register.csv`;
- unresolved decisions: `open-decision-register.csv`;
- execution templates: `tests/forms/hr-v0-watchdog-fault-injection-template.csv` and `hr-v0-watchdog-separation-inspection-template.csv`; and
- generator/checker: `tools/generate_hr_v0_watchdog_ccf.py` and `tools/check_hr_v0_watchdog_ccf.py`.

All 28 cases remain `NOT EXECUTED` and `NOT AUTHORIZED`. Internal-equivalent injection and cross-rail tests must not be attempted until a qualified reviewer accepts the analysis method, current-limited no-load fixture, instruments, numerical limits, stop conditions and two-person control. The actuator source remains physically absent for the later E2 logic subset.

## Primary-document basis

- Phoenix Contact PLC-RSC-24DC/21-21 item 2967060 official product PDF, data-maintenance 2026-04-01, rechecked 2026-08-08: https://www.phoenixcontact.com/en-pc/products/relay-module-plc-rsc-24dc-21-21-2967060?type=pdf
- TI TPL7407L datasheet `SLRS066D`, Revision D, March 2016, current product page rechecked 2026-08-08: https://www.ti.com/lit/ds/symlink/tpl7407l.pdf
- TI ISO1211/ISO1212 datasheet `SLLSEY7G`, Revision G, February 2025, rechecked 2026-08-08: https://www.ti.com/lit/ds/symlink/iso1212.pdf
- Raspberry Pi RP2040 product-information portal, official documents updated 2025-10-06, rechecked 2026-08-08: https://pip.raspberrypi.com/categories/814-rp2040
- Pilz PNOZ s4 operating manual `21396-EN-23`, English revision 23 / 2026-02, rechecked 2026-08-08: https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf
- ISO 13849-1:2023 official record, Edition 4, published 2023-04, rechecked 2026-08-08: https://www.iso.org/standard/73481.html

Manufacturer documents support component and terminal review only. They do not allocate the project PLr, accept a fault exclusion, validate the system, or authorize energization.

## Release consequence

`ANALYSIS-SAFE-002` now has a complete configuration-bound input package, but it has not been executed or signed. `EG-012` remains partial. `SF-01` and `SF-03` retain `SELECTION REQUIRED`; `DF-01` retains zero credit. No fabrication, wiring, connection, fault injection, motion or energization gate closes.

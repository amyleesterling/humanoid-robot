# Sol R12 Findings Rechecked Against R19

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-06

Current configuration: `HR-30-SYS-R0.2`, Electrical `V3-P0.4`, firmware `HR-V0-FW-P0.1` with watchdog configuration `HR-V0-WD-P0.3`

## Scope and independence

This is a project-owned status reconciliation, not a new independent review round. Sol's R12 review examined GitHub `main` at `ee276af6f1a17c3a168f55efc91df2dd4a9eba38` and the hosted Electrical V2.1 artifacts. Sol has not independently reviewed R13-R19.

The original R12 totals - 18 BLOCKER, 30 MAJOR, and 8 MINOR findings - remain attached to the configuration Sol reviewed. Later evidence does not silently delete, downgrade or backdate those findings.

## What changed after R18

R18 removed a modeled 24 V-to-Pico boundary but left `IFB1` and `IFB2` as opaque `DESIGN REQUIRED` blocks. R19 replaces those placeholders with:

- one exact `ISO1212DBQ` dual-channel receiver and all 16 package pins;
- 1 kOhm `RTHR`, 562 Ohm `RSENSE`, and 10 nF `CIN` per channel;
- a calculated 2.70 kOhm 1%, 0.5 W contact-wetting load per channel;
- 100 nF VCC bypass, 1 kOhm output-series resistors, and 10 kOhm GPIO pulldowns;
- a checked active-high feedback-polarity record in the watchdog configuration; and
- a dedicated KiCad feedback sheet plus a primary-source calculation record.

The first R19 drawing incorrectly connected `RSENSE` from `IN` to field ground. A direct TI Rev. G recheck identified that application error and corrected `RSENSE` to the required `SENSE`-to-`IN` connection before the candidate was committed. This is preserved in the review ledger because clean ERC did not detect it.

The resulting Electrical V3-P0.4 project has one root plus ten child sheets, 55 component blocks, 241 modeled terminals, 62 named connected nets, 25 deliberate unconnected nets, 216 wire labels, 43 unresolved component/interface rows, and 64 `TBD-*` terminals. KiCad 10.0.5 ERC is 0 errors / 0 warnings; native netlist, PDF, SVG and exact-net checks pass.

## Current disposition of Sol's headline conclusions

| Sol R12 conclusion | R19 disposition |
|---|---|
| Authoritative GitHub source lacked native KiCad. | **Corrected after Sol's baseline.** V2.1 and V3 native KiCad sources are present with manifests and validation outputs. This does not make either build-released. |
| HR-V0 lacks a buildable electrical schematic. | **Partially addressed; open.** V3-P0.4 is connected and pin-level at the watchdog feedback boundary, but exact protection, conductors, connectors, driver circuitry, PCB, enclosure and application evidence remain open. |
| Watchdog recovery could restore authority without enforced manual restart. | **Nominal topology corrected; safety finding open.** V3 requires SR1 RESET followed by distinct SRA1 ARM. Welded contacts, common causes, diagnostic coverage, PLr/SIL, timing and physical fault tests remain open. |
| Watchdog feedback was architecture-only. | **Circuit candidate added; release evidence open.** Threshold, wetting-current and GPIO margins are calculated, but exact passives, PCB, EMC, brownout, fault injection and HIL remain unverified. |
| HR-V0 has no buildable mechanical release. | **Open.** Quote geometry is not manufacturing CAD; fit, tolerances, fasteners, guards, hard stops, cable paths, anchoring and proof tests remain unresolved. |
| HR-V0 energization is prohibited. | **Still correct.** No applicable energization gate is closed by the R19 circuit correction. |
| HR-30W walking is plausible but unproved. | **Still correct.** Mass/inertia closure, continuous joint performance, safe power loss, sensing, controls, restraint and physical walking evidence remain absent. |

## Independent review now requested

An independent reviewer should reproduce `tools/generate_hr_v0_electrical_v3.py --validate`, `tools/check_hr_v0_electrical_v3.py`, the firmware tests/checker, traceability, and the E2 gate check against the exact R19 commit. The reviewer must inspect every sheet visually and independently rederive:

- ISO1212DBQ pin mapping and `RSENSE` placement;
- Mean Well 23.4-24.6 V rail endpoints;
- ISO1212 thresholds and input-current bounds;
- Phoenix 10 mA minimum contact-current margin;
- wetting-resistor dissipation and derating;
- RP2040 logic margins and brownout behavior;
- tied-ground/no-isolation-credit boundary; and
- open/short/common-cause/fault-injection coverage.

The controlled review prompt is `docs/reviews/2026-08-06-electrical-v3-independent-review-request.md`.

## Verdict

R19 materially improves electrical reviewability but does not change the program release verdict. HR-V0 remains not ready for procurement, fabrication, control-only energization or actuator energization. The package is suitable for another detailed independent design review and for qualified reviewers to identify the remaining closure evidence; it is not a released machine design.

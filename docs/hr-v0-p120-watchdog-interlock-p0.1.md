# HR-V0 P1.20 watchdog-interlock candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P120-WD-INTERLOCK-P0.1`

Round: R232

Date: 2026-08-11

## Decision

P1.20 is an unaccepted source-level correction candidate for Sol R12 blocker B-005. It removes the two ordinary watchdog contacts from the `SR1:A1` supply path and places one contact in each independent `SRA1` input return:

- `SR1:14` -> `KWD1:11-14` -> `SRA1:S12`
- `SR1:24` -> `KWD2:11-14` -> `SRA1:S22`

`SR1:A1` returns directly to `SAFETY_24V`. The direct dual-channel S0-to-SR1 E-stop loops remain unchanged. Heartbeat restoration still requires a fresh monitored ARM event before SRA1 may become eligible, and ARM does not create a motion command.

This candidate materially addresses the reviewed single-watchdog-contact source topology: either one welded KWD contact is defeated when the other SRA1 channel opens. It does **not** close B-005. Dual weld/bypass, a shared controller or driver command, protected routing, dependent failure, exact input-contact suitability, installed behavior, achieved stopping response and qualified functional-safety allocation remain open. KWD1, KWD2 and the entire heartbeat path receive zero safety credit.

## Exact modeled change

The P1.19-to-P1.20 delta is exactly seven terminal/net assignments:

1. `SR1:A1`: `SR1_A1_WD_GATED` -> `SAFETY_24V`
2. `SR1:14`: `SRA1_S12` -> `SR1_OUT1_TO_KWD1`
3. `SR1:24`: `SRA1_S22` -> `SR1_OUT2_TO_KWD2`
4. `KWD1:11`: `SAFETY_24V` -> `SR1_OUT1_TO_KWD1`
5. `KWD1:14`: `WD_SUPPLY_INTERMEDIATE` -> `SRA1_S12`
6. `KWD2:11`: `WD_SUPPLY_INTERMEDIATE` -> `SR1_OUT2_TO_KWD2`
7. `KWD2:14`: `SR1_A1_WD_GATED` -> `SRA1_S22`

Machine checks prove:

- 13 native KiCad pages parse in KiCad 10.0.5;
- ERC is 0 errors / 0 warnings;
- all 84 native component reference/value/footprint identities are unchanged;
- all 340 modeled terminal identities remain present;
- 333 terminal/net assignments are unchanged and exactly seven changed;
- the native netlist changes exactly seven named-net memberships, matching the schedule delta;
- 82 BOM rows, 301 wire-table rows and 63 unresolved-selection rows remain present; and
- S0, S1, S2, SRA1, K1, K2, FSR1 and FSR2 terminal/net assignments are unchanged.

ERC proves modeled connectivity and annotation only. It does not prove the application, hardware, wiring, fault response or safety integrity.

## Fault screen

The controlled truth table contains twelve cases. Normal, heartbeat-loss, each single weld, each single bypass, one open path and heartbeat-restoration behavior are screened. Three cases remain explicitly hazardous and unresolved:

- both KWD contacts welded or bypassed;
- a shared controller/driver command holding both relays on; and
- both field interlock paths bypassed.

The truth table is a design review aid, not executed fault-injection evidence.

## Primary manufacturer records

- Phoenix Contact `PLC-RSC-24DC/21-21`, item 2967060: official product record and generated product PDF, data-maintenance date 2026-04-01, rechecked 2026-08-11. Used only for A1/A2 and 11-12-14 / 21-22-24 terminal identity plus published ordinary relay characteristics. It is not treated as a force-guided or safety-rated device and receives no application approval: <https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc21-21-2967060>
- Pilz `PNOZ s4`, order 750104: official product record; current listed operating manual 21396-EN-23 dated 2026-06-22, rechecked 2026-08-11. Exact Project Button input/start application and achieved PL/SIL remain subject to qualified confirmation: <https://www.pilz.com/en-US/eshop/product/750104>
- Schneider Electric `LC1D25BD`: official product record rechecked 2026-08-11. The exact contactor identity is retained, but its Project Button DC interruption, suppression, regeneration and endurance application remains open: <https://www.se.com/us/en/product/LC1D25BD/>

## Open holds

Nine holds remain: independent P1.20 topology review; qualified PNOZ application confirmation; ordinary KWD input/minimum-load/endurance evidence; common-cause/dependent-failure analysis; protected routing/separation; executed manual re-arm proof; authorized fault/stopping tests; qualified PLr/SIL allocation and validation; and formal configuration promotion.

P1.15 remains the current electrical product. P1.18, P1.19 and P1.20 remain unaccepted candidates.

## Controlled artifacts

- `electrical/kicad/project-button-v3-p1.20-watchdog-interlock-candidate/`
- `electrical/reviews/hr-v0-p120-watchdog-interlock-p0.1/`
- `release/hr-v0/p120-watchdog-interlock-p0.1/`
- `tools/generate_hr_v0_electrical_v3_p120_watchdog_interlock_candidate.py`
- `tools/generate_hr_v0_p120_watchdog_interlock_p01.py`
- `tools/check_hr_v0_p120_watchdog_interlock_p01.py`

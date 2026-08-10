# HR-V0 watchdog-gated SR1 supply correction P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Identifier: `HR-V0-WD-SUPPLY-P0.1`
Configuration: Electrical V3-P1.13 / PCB-P0.5 / HR-V0-CP-P0.5
Purpose: correct the R86 watchdog dependent-failure blocker without assigning safety credit to the heartbeat diagnostic.

## Correction

R86 found that KWD1/KWD2 contacts in the SR1 input returns created a possible voltage-injection path downstream of the E-stop. P1.13 removes every KWD terminal from those returns:

- `SR1:S11 -> S0:R-1/R-2 -> SR1:S12`;
- `SR1:S21 -> S0:L-1/L-2 -> SR1:S22`.

KWD1 and KWD2 instead form a series supply gate:

`SAFETY_24V -> KWD1:11/14 -> WD_SUPPLY_INTERMEDIATE -> KWD2:11/14 -> SR1_A1_WD_GATED -> SR1:A1`.

This source-level topology prevents the previously identified KWD A1/21-to-14 fault from directly energizing an E-stop return. A welded or bypassed KWD contact can still defeat heartbeat-based dropout. `DF-01` therefore receives zero safety credit and is assumed failed in the credited safety analysis.

## Restart semantics

Loss of either watchdog relay should remove SR1 A1 power. Restoring the heartbeat should restore only the possibility of restarting SR1, not motion. The required physical sequence remains:

1. heartbeat loss removes SR1 supply;
2. restored heartbeat makes the diagnostic gate available;
3. a deliberate physical RESET is required;
4. a separate deliberate physical ARM is required;
5. the motion controller must require a fresh trajectory.

No step is accepted from schematic logic alone. Brownout, relay chatter, recovery timing, retained firmware state, welded contacts, false feedback, and every relevant power-state permutation require controlled no-load tests before connection to contactor or actuator loads.

## Contact-load evidence boundary

The Pilz PNOZ s4 750104 record gives a 2.5 W DC power figure and maximum A1 startup pulse of 0.5 A for 5 ms. At 24 V, the nominal arithmetic is 0.10417 A. Phoenix Contact's 2967060 catalog data gives useful preliminary contact limits, but it does not prove switching suitability or endurance for this electronic safety-relay supply input. Manufacturer application confirmation, switching-cycle target, protection coordination, received-component inspection, measured inrush, brownout and endurance tests remain required.

## What the controlled package contains

The interactive guide is `safety/hr-v0-watchdog-supply-gate-p0.1/index.html`. Its source registers include:

- 14 exact circuit/configuration paths;
- four explicitly compared architecture options;
- seven contact-load screens;
- the complete 32-case controlled-open watchdog FMEA;
- 28 unexecuted and unauthorized fault cases;
- 12 unreleased separation controls;
- ten open release decisions; and
- eight source/configuration records.

The package checker cross-references the exact native-ECAD nets and terminals, panel wire schedule, route controls, canonical FMEA, status flags, warnings, and readable web/SVG presentation.

## Remaining blockers

The correction does not close functional-safety allocation, protected routing, internal-relay fault modeling, contact application, branch protection, conductor selection, fault current, physical terminal mapping, manual-reset behavior, total stop timing, contamination/workmanship, fault injection, HIL, or qualified review. An external conductor bridge into an SR1 return remains an explicit open impairment case. No fault exclusion is accepted.

The package is ready for independent electrical and functional-safety criticism of the proposed correction. It is not ready for panel fabrication, wiring, fault injection, energization, contactor connection, actuator connection, or motion.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

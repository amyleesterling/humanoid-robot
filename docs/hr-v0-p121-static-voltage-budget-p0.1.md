# HR-V0 P1.21 static 24 V control-rail voltage budget P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P121-STATIC-VOLTAGE-BUDGET-P0.1`

Round: R246

Status: **PARTIAL / NOT ACCEPTED**

## Result

The P1.21 topology now has an end-to-end, terminal-addressed static voltage-budget scaffold for eight control loads. It correctly binds GlobTek `WR9QI1660YL4NKITR6B` as the 24 V control source and excludes Mean Well `GST280A12-C6P`, which is the separate 12 V actuator-source candidate.

At the GlobTek output connector, the published +/-5% regulation produces a 22.8-25.2 V source interval. Before project wiring, contacts, fuses, return paths, temperature, uncertainty or transients, the raw low-side headroom is:

- 2.4 V for Pilz PNOZ s4 `SR1` and `SRA1` against their 20.4 V published minimum;
- 2.6 V for Phoenix Contact `KWD1/KWD2` against the 20.2 V published minimum at 20 C;
- 6.0 V for Schneider `K1/K2` coils against the 16.8 V operational limit through 60 C; and
- 16.3 V for the TRACO `TSR 1-2450` watchdog-board input against its 6.5 V published minimum.

These are raw source-connector screens, not installed margins. The accepted installed margin remains `NOT CALCULABLE` because the design has no conservative maximum for every series element or every simultaneous/dynamic load state.

## Exact control-loop boundaries

The controlled register traces:

1. `PSU2/J24/F24/XD24/C-01/SR1:A1` and `SR1:A2/XD0/J24:3`;
2. `XD24/C-03/KWD1:11-14/C-06/KWD2:11-14/C-07/SRA1:A1` and the `SRA1:A2` return;
3. each KWD coil through its own `JWP1` input, TI low-side driver package and common `JWP1:2/XD0:07` return;
4. both Schneider contactor-coil branches through `SRA1` outputs and unselected `FSR1/FSR2` protection;
5. the watchdog-board TRACO input; and
6. the Pilz `Y32` indication path to unresolved `H1` terminals.

TI `UDRV1/2` COM connections to `SAFETY_24V` are clamp/driver-operating connections, not steady coil-return paths.

## What prevents acceptance

The package retains eighteen explicit missing inputs. The blockers include exact fuse/link/holder selections and hot resistance, received J24 mating identity, common forward and return conductors, distribution-block impedance, actual cuts and DCR across temperature, Phoenix maximum module current and 11-14 contact drop, watchdog PCB/JWP1/driver return losses, maximum simultaneous current, GlobTek undershoot/foldback/recovery, H1 identity, accepted uncertainty/aging margin, installed thermal conditions, received voltage traces, restart fault injection and qualified review.

No unpublished value is inferred. `SELECTION REQUIRED` remains the controlling state where the evidence is absent.

## Primary manufacturer records

- GlobTek, `WR9QI1660YL4NKITR6B`, specification Rev B, rechecked 2026-08-11: https://spec.globtek.info/spec/?id=01t0c000008jfZg
- Pilz, PNOZ s4 operating manual `21396-EN-23`, imprint 2026-05 / portal 2026-06-22: https://www.pilz.com/en-US/eshop/Relay-modules/Safety-relays-protection-relays/PNOZsigma-safety-relays/PNOZ-s4-24VDC-3-n-o-1-n-c/p/750104
- Phoenix Contact, item `2967060`, last data management 2026-04-01: https://www.phoenixcontact.com/en-us/products/relay-module-plc-rsc-24dc-21-2967060
- Texas Instruments, `TPL7407L`, `SLRS066D`, revised 2016-03: https://www.ti.com/lit/ds/symlink/tpl7407l.pdf
- Schneider Electric, `LC1D25BD` data sheet, dated 2017-09-13: https://iportal.se.com/Contents/docs/SQD-LC1D25BD.PDF
- TRACO POWER, TSR 1 data sheet, dated 2024-02-07: https://www.tracopower.com/tsr1-datasheet
- Kycon, `KPJX-PM-4S`, Rev C2 dated 2026-01-08: https://www.kycon.com/Pub_Eng_Draw/KPJX-PM-4S.pdf
- MEAN WELL, `GST280A-SPEC`, dated 2026-04-03; recorded only to enforce exclusion from the 24 V budget: https://www.meanwell.com/Upload/PDF/GST280A/GST280A-SPEC.PDF

## Configuration boundary

P1.15 remains the current electrical candidate. P1.21 and this voltage-budget package remain unaccepted. Static-source arithmetic does not establish functional safety, stopping performance, build readiness or authority to perform physical work.

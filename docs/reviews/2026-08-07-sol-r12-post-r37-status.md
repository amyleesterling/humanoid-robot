# Sol R12 findings rechecked against R37

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

This is a project-owned reconciliation, not a new independent Sol review. Sol's R12 totals remain **18 BLOCKER, 30 MAJOR and 8 MINOR** against the historical configuration.

## R37 correction

R37 advances the connected system candidate to Electrical `V3-P1.2` and replaces three undefined inline DYNAMIXEL power-injection modules with one exact central star-injection interface, `INJ1`. It adds a separate native KiCad `DXL-STAR-P0.1` project with:

- seven exact proposed board headers and 18 frozen project terminals;
- one common DYNAMIXEL TTL data tree and one common actuator return;
- three mutually isolated positive rails, one per protected actuator branch;
- `JC1:2` deliberately assigned no net and no copper so the U2D2-side VDD path is absent;
- a 100 mm x 60 mm, two-layer routed PCB candidate with four board-only M3 holes, 17 routed segments and one common-return zone;
- native ERC/DRC 0/0, independent net/isolation assertions, readable top/bottom renders, synchronized schedules and source hashes; and
- no Gerber, drill, placement or assembly outputs.

R37 also adds a physical receiving/continuity/isolation/no-backfeed/thermal/waveform evidence form, two controlled procedures, exact proposed board and mating connector records, primary-source citations, and an expanded independent-review scope.

## What R37 narrows

- Sol M-013 is materially narrowed: U2D2 actuator VDD exclusion is now represented by an exact board pin with no net/copper and a required empty cable cavity, rather than by an undefined custom-module note.
- The three branch-positive isolation topology and project pin allocation are now reproducible from native ECAD and machine checked.
- Energization gate `EG-015` gains controlled design and test evidence locations but remains `partial` because no harness has been released, built, or tested.

## New and retained blockers

- JST publishes the EH family at 3 A with AWG 22, while ROBOTIS publishes a 4.4 A XM540-W270-T stall-current endpoint at 12 V. R37 exposes but does not close this application conflict.
- Exact cable wire, length, insulation, colors, crimp tools, crimp/pull limits, strain relief, source-side terminals, current limits, baud rate, waveform criteria and routing remain `SELECTION REQUIRED`.
- A DRC-clean 2.0 mm positive trace is not ampacity, thermal, connector, fault-clearing, or fabrication evidence.
- The common-return topology still requires ground-current, voltage-offset, EMI, signal-integrity and source-sequencing proof.
- No board or harness exists; no continuity, isolation, no-backfeed, thermal, waveform, retention or fault test has been executed.
- The protection values and conductor coordination from R36 remain unresolved.
- Every other physical-build, functional-safety, mechanical and control blocker retained in R36 remains open.

## Disposition

Sol's central verdict remains correct. R37 converts an ambiguous interface placeholder into reviewable native ECAD and an executable evidence route. It does not make HR-V0 buildable or energizable. No procurement, fabrication, wiring, functional-safety or energization approval is issued.

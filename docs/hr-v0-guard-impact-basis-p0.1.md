# HR-V0 guard impact-energy basis P0.1

**PRELIMINARY - IMPACT ALLOCATION INPUT ONLY. NOT APPROVED FOR PANEL SELECTION, PROCUREMENT, FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-07

Identifier: `HR-V0-GUARD-IMPACT-P0.1`

Parents: `HR-V0-GUARD-P0.3`, `HR-V0-GUARD-RET-P0.1`

Requirements: `SYS-002`, `SYS-003`, `SYS-004`, `SAFE-004`, `SAFE-010`, `SAFE-011`, `MASS-002`

Risks: `R-001`, `R-002`, `R-003`, `R-006`, `R-022`

## Result

R77 separates the guard problem into five hazard classes: the permitted foam payload, moving links, continued/runaway drive, detached hardware, and static access or push-out. This prevents the known payload-only result from being misused as the rating for the complete guard.

The arithmetic closes four payload/controlled-motion subcases and four sensitivity cases. It does **not** close the installed impact load. Effective/reflected inertia, continued drive after contact, detached-part definition, static push-out load, test multiplier, impactor, direction, conditioning and acceptance criteria remain unresolved. No transparent-sheet thickness or retention system is selected.

## Reproducible calculated cases

| Case | Calculation | Result | Allowed interpretation |
|---|---|---:|---|
| 100 g payload at the 0.15 m/s TCP ceiling | `0.5 x 0.100 x 0.150^2` | 0.001125 J | normal-command payload-only subcase |
| full 0.750 kg moving-mass ceiling at 0.15 m/s | `0.5 x 0.750 x 0.150^2` | 0.008438 J | conservative controlled-mode equivalent, not rigid-body impact closure |
| 100 g payload dropped through 0.950 m | `0.100 x 9.80665 x 0.950` | 0.931632 J | receiver/catch input only |
| payload drop plus permitted translation | `0.931632 + 0.001125` | 0.932757 J | payload-only combined planning screen |
| full moving-mass ceiling at 0.360 m and XM540 12 V no-load endpoint | `0.5 x 0.750 x (0.360 x pi)^2` | 0.479663 J | incomplete single-axis overspeed sensitivity |
| full moving-mass ceiling at 0.51745 m combined J1/J2 radius and the same endpoint | `0.5 x 0.750 x (0.51745 x pi)^2` | 0.990987 J | deliberately conservative, incomplete simultaneous-axis sensitivity |
| RAW 800 ideal torque-line work per degree per XM540 | `5.18 x pi/180` | 0.090408 J/degree | unit sensitivity; actual continued angle/time is unresolved |
| 12 V stall-endpoint work per degree per XM540 | `10.6 x pi/180` | 0.185005 J/degree | forbidden catalog-endpoint sensitivity, not a design load |

The 30 rev/min no-load and 10.6 N m stall endpoints must never be combined as simultaneous motor performance. ROBOTIS describes stall torque as a momentary output that differs from continuous and expected real-world performance. The no-load speed is not a guaranteed physical maximum under every fault, supply, gravity, thermal or regenerative condition.

## Why the guard is still unselected

The largest closed payload-only screen is 0.932757 J. The current incomplete combined-axis mass-ceiling sensitivity is 0.990987 J, but it omits reflected actuator/gear inertia and energy added while torque persists after contact. At the current RAW 800 project torque-line candidate, each unresolved degree of continued drive adds 0.090408 J per XM540 before gravity, compliance, rebound and simultaneous-axis effects.

Three entire load classes remain without numeric release values:

1. detached metal hardware, actuator, frame, fastener, cable or tool impact;
2. a powered link bearing on a panel while current persists; and
3. static access, panel push-out and guard-joint/anchor loading.

Therefore neither nominal 3 mm TUFFAK GP with `12004` nor the nominal 6 mm P0.3 branch may be selected, ordered or cut from this calculation.

## Required test definition

Before a panel branch can be selected, a qualified reviewer must release:

1. the exact as-built moving mass, center of mass and effective/reflected inertia;
2. measured maximum speed, contact detection, current persistence, energy-removal time, gravity contribution, compliance and rebound;
3. the largest credible detached item and its mass, shape, velocity and direction, or proof that its retention excludes that case;
4. static access/push-out loads and probes appropriate to the Boston installation;
5. test-energy multipliers, impactor geometry, panel location/direction, temperature/aging conditioning and repeat count;
6. exact production-equivalent sheet lot, edge finish, gasket engagement, frame, joints, anchors and cable entries; and
7. quantified acceptance criteria for escape, openings, fragments, engagement loss, permanent set and frame/joint/anchor damage.

Coupons may establish correlation or failure modes. They cannot alone release the complete installed enclosure.

## Source register

- ROBOTIS, XM540-W270-T/R e-Manual, live page with no formal revision shown, accessed 2026-08-07: https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/
- ROBOTIS, XM430-W350-T/R e-Manual, live page with no formal revision shown, accessed 2026-08-07: https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/
- ISO 14120:2015, Edition 2, published 2015-11; current ISO page checked 2026-08-07: https://www.iso.org/standard/59545.html
- OSHA 29 CFR 1910.212, current electronic regulation checked 2026-08-07: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.212
- Project Button `requirements/requirements.csv`, `HR-V0-ARM-ARCH-P0.7`, and `HR-V0-GUARD-P0.3`, repository state checked 2026-08-07.

The ISO public metadata establishes the general guard-design scope, and OSHA requires appropriate guarding and secure attachment. Neither public source supplies a project-specific impact energy, panel thickness, retention capacity or acceptance value. Applicable licensed standards and a qualified applicability review remain required.

The machine-readable registers and responsive guide are under `cad/hr-v0/guard-impact-basis-p0.1/`. They are calculation and test-definition inputs only.

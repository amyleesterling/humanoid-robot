# HR-V0 fixed guard and receiver candidate P0.2

> **SUPERSEDED FOR CURRENT GUIDANCE BY `HR-V0-GUARD-P0.3`.** Retained as R74 configuration history.

**PRELIMINARY—DESIGN CANDIDATE ONLY. NOT APPROVED FOR FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-07

Identifier: `HR-V0-GUARD-P0.2`

Mechanical basis: `HR-V0-MECH-P0.6` / `HR-V0-ARM-ARCH-P0.7`

Requirements: `SAFE-004`, `SAFE-010`, `SAFE-011`, `MECH-001`

Physical protective measure: `PG-01`; no SRP/CS, PL, SIL or functional-safety credit

## Result

This pass converts the R25 guard space study into a dimensioned fixed-enclosure candidate with source geometry, STEP/GLB exports, frame and panel schedules, a catch receiver, a machine-readable interface register, and a responsive interactive guide. It also replaces the obsolete `-25/75°` J1 and `10/130°` J2 inspection rows with the current P0.7 command and continuous-certificate cases.

The package is more complete, but it is intentionally not a cutting or installation release. Twelve holds remain open. In particular, the 450 mm radius remains a space reservation rather than a safety distance, and neither the nominal 6 mm transparent sheet nor the 20 × 20 mm frame envelope is a selected product or structurally qualified assembly.

## Coordinate system and candidate dimensions

Guard datum `G0` is the vertical projection of the J1 axis onto the bench. X is guard depth, Y is guard width, and Z is height above the bench. The candidate places J1 at `G0 + (0, 0, 500 mm)` and models the 450 mm Y–Z reservation as a 400 mm-deep extruded disk—not a sphere—because the complete out-of-plane gripper/cable sweep is still unknown. It provides the following internal clear box:

| Control | Candidate value | Boundary |
|---|---:|---|
| Internal X depth | 400 mm | full gripper and moving-cable out-of-plane sweep remains open |
| Internal Y width | 900 mm | based on the 450 mm radial reservation |
| Internal Z height | 950 mm | shoulder height plus the 450 mm radial reservation |
| Frame profile envelope | 20 × 20 mm | manufacturer, alloy, temper, joints and fasteners `SELECTION REQUIRED` |
| Transparent panel geometry | nominal 6 mm | manufacturer, grade, tolerance, impact, retention and edge treatment `SELECTION REQUIRED` |
| Catch clear region | 320 × 820 mm | receiver construction, nests, support and rebound acceptance remain open |
| Catch wall height | 50 mm | physical containment testing remains open |

The radial reservation is still `360 + 35 + 25 + 25 + 5 = 450 mm`. The last three terms—stopping travel, clearance, and build/calibration/tolerance—are provisional and cannot be treated as acceptance limits. The guard must grow whenever the measured union of the complete assembly sweep, gripper, payload, cables, stopping travel, tolerances and selected access clearance exceeds the candidate volume.

## Geometry and schedules

`cad/hr-v0/guard-receiver-p0.2/` contains:

- a native STEP assembly and a GLB visualization;
- a readable SVG dimension sheet;
- `HR-V0_fixed-guard-interactive.html`, with independently toggled panels, reserved space and receiver layers;
- four-line / sixteen-piece frame cut-length candidate;
- four-line / eight-piece panel-geometry candidate;
- interface, source, calculation and twelve-hold registers.

The frame schedule is length-controlled only. Saw allowance, tolerance, end treatment, profile manufacturer, joint brackets, screws, T-nuts, panel clamps and bench anchors remain unresolved. The panel schedule is finished-envelope geometry only: it provides no hole pattern, cut authority or product selection. All panels are fixed and tool-removable only after the applicable service disconnect is open and absence of actuator energy is verified. No door or interlock is selected or credited.

## Receiver energy boundary

The controlled 100 g foam article released from the top of the 950 mm internal space has a gravitational potential energy screen of:

`0.100 kg × 9.80665 m/s² × 0.950 m = 0.931632 J`.

This is a test input, not a receiver, panel or guard impact rating. It does not address rebound, off-axis release, actuator-attached debris, detached metal parts, fastener failure, robot collapse or energy remaining in a moving link. Those cases require the risk assessment, retention analysis and physical tests recorded in `guard-closure-holds.csv`.

## Primary-source boundary

- OSHA 29 CFR 1910.212 requires guards to be affixed where possible (otherwise secured) and not create a hazard themselves. Current electronic regulation checked 2026-08-07: https://www.osha.gov/laws-regs/regulations/standardnumber/1910/1910.212
- ISO 14120:2015 Edition 2 gives general requirements for fixed and movable guard design and construction. ISO reports publication in 2015-11, confirmation in 2021, and systematic review beginning 2026-01-15. The licensed standard and a qualified applicability review remain required: https://www.iso.org/standard/59545.html
- The possible 80/20 `20-2020` route was reached on 2026-08-07, but its anti-bot interstitial prevented verification of current product data. No order code, section property or structural rating is claimed: https://8020.net/20-2020.html
- The transparent sheet manufacturer, grade and technical data remain `SELECTION REQUIRED`. “Polycarbonate” alone is not a released material specification.

## Closure required before fabrication or guarded motion

1. Close all twelve `GH-*` rows, including complete gripper/payload/cable sweep and measured stopping travel with uncertainty.
2. Select exact frame, panel, joint, fastener, clamp, cable-entry and anchor products from current primary documentation.
3. Complete structural, stability, retention, impact, access and detached-part analyses against accepted load cases.
4. Freeze the bench survey, J1-to-G0 transform, enclosure footprint, control locations, service clearances and Boston site assumptions.
5. Execute all twelve inspection cases, `TEST-DROP-001`, access-probe tests and applicable guard proof/fault tests with traceable instruments.
6. Obtain signed qualified mechanical, electrical and functional-safety review of the frozen as-built configuration.

This package advances design definition only. It supplies no purchase, cutting, drilling, assembly, motion, connection, energization or functional-safety approval.

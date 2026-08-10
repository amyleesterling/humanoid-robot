# R197 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-KIN-P0.1`

Date: 2026-08-10

## Source correction

- Added a conservative planar TCP-rate bound using the current J1-to-J2 202.550 mm and derived J2-to-H104 129.050 mm candidate geometry.
- Added exact canonical model hashing and rejection of unresolved, substituted, stale, nonfinite or unaccepted configuration.
- Added `Supervisor.from_json()` so the validator comes from the same configuration object rather than an unrelated callback.
- Kept H104-to-tool reach, model hash and physical acceptance evidence `SELECTION REQUIRED`; the repository constructor refuses to create a motion validator.

## Executed checks

- Supervisor suite: 47/47 tests passed, including nine kinematic tests and repository-constructor refusal.
- Firmware checker: 58 executable unit tests passed; target flash, received-hardware execution and HIL remain not performed.
- Complete standard-runtime coverage: 141/141 checkers passed after regenerating the three configuration-bound hash registers and correcting the CAD manifest to its required line-ending-independent digest.
- Native KiCad `pcbnew` sweep: 13/13 checkers passed.
- Deterministic release manifest: 3,374 package files; dedicated checker passed against the staged candidate.
- `check_energization_gates.py --through E2 --require-ready` returned exit 2 as required: 0/21 gates closed and all 21 remain partial.

## Web-guide inspection boundary

The dedicated guide checker passed the 16 px body, 14 px metadata, responsive single-column breakpoint, calculator-control and undersized-declaration rules. No browser screenshot or manual visual-layout claim is made in this record; independent desktop/mobile visual inspection remains requested.

## Boundary

This is source/model evidence only. No target image, HIL, as-built geometry, tool selection, calibration, physical speed, stopping, guard or functional-safety behavior is proved. The 0.150 m/s configuration value is not released. No Sol finding, requirement, gate or work authority closes.

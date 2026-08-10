# R75 validation record — guard catalog candidates and mass correction

**PRELIMINARY—NOT APPROVED FOR PROCUREMENT, FABRICATION, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-07

Round: R75

Candidate: `HR-V0-GUARD-P0.3`

## Scope and corrections

R75 advances the R74 fixed-guard design without changing the internal clear-space candidate or claiming a safety distance. It:

- verifies current manufacturer pages for 80/20 `20-2020`, `14201`, `75-3581` and `20-2496`;
- freezes `20-2020`, `14201` and `75-3581` quantities as exact catalog candidates on hold;
- freezes Plaskolite TUFFAK GP clear nominal 6 mm as an exact grade candidate using PDS004 `122022` while preserving its typical-data limitation;
- adds the five receiver pieces omitted from the P0.2 panel schedule;
- records twenty joints and forty proposed joint-hardware assemblies;
- calculates an incomplete 30.799798 kg profile-and-sheet subtotal; and
- adds `BOM-074` through `BOM-078`, bringing the system BOM to 78 groups.

## Validation boundary

The generator/checker require exact artifact membership, 16 profile pieces, 13 sheet pieces, 20 joints, 40 joint-hardware assemblies, six current primary-source rows, six catalog-candidate rows, four mass rows, twelve open holds, twelve unexecuted inspection cases and the unchanged fail-closed warnings.

The BOM checker requires 17 evaluation candidates, 24 exact-candidate holds and 29 selection-required groups. `EG-003` and `EG-008` remain partial. Full repository and clean-clone results are recorded against the final commit before push.

## Validation results

- The P0.3 generator and checker passed at 16 frame pieces, 13 sheet pieces, 20 joints, 40 joint-hardware assemblies, 12 open holds and 12 unexecuted inspection cases.
- The BOM generator and checker passed at 78 system groups, 17 evaluation candidates, 24 exact-candidate holds and 29 selection-required groups.
- All 27 repository `tools/check_*.py` validators passed. The DXL-star and watchdog-PCB checks used KiCad 10.0 Python; the other checks used the controlled CAD Python environment.
- Traceability passed at 81 requirements, 40 risks and 104 procedures.
- The gate checker remained fail-closed at 0 closed, 22 partial and 8 open.
- The staged release manifest contains 810 package files and passed exact membership/hash validation. Clean-clone reproduction is recorded after the final commit.

A passing checker establishes internal consistency of the modeled evidence only. It does not establish physical fit, strength, stopping, guarding performance, functional safety or permission to build or energize.

Exact identity is not application acceptance. Joint capacity, panel retention, anchors, stopping, complete sweep, access, impact, received inspection, physical proof and qualified review remain open.

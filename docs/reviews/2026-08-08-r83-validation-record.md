# R83 validation record - hard-stop region clearance and interface acquisition

Date: 2026-08-08
Product: `HR-V0-STOP-REGION-P0.1`
Parent: `HR-V0-ARM-ARCH-P0.7`
Status: **PRELIMINARY - NO STOP, FABRICATION, MOTION, OR ENERGIZATION RELEASE**

## Correction

R83 responds to the open J1-minimum, J1-maximum and J2-minimum stop findings without promoting the historic study angles or inventing a mounting interface. It adds a deterministic stop-region generator, continuous clearance evidence, a physical-input register, a topology decision register, a readable SVG and an interactive HTML guide.

## Executed validation

- generator completed successfully with CadQuery/OCC;
- `6,411` unique 0.5-degree boundary poses evaluated;
- `6,411` rows reported `PASS_NOMINAL` and zero positive-volume intersection;
- `131` pair-region continuous certificates generated;
- `133` continuous leaf cells accepted;
- conservative minimum nominal clearance: `5.743912 mm`;
- required nominal model-space floor: `0.75 mm`;
- `20/20` physical-input rows remain `OPEN` and `NOT EXECUTED`;
- all three potentially acceptable stop topologies remain `NOT SELECTED`;
- actuator-case/cable/guard stops and software-only limiting are explicitly rejected; and
- `tools/check_hr_v0_stop_region_clearance.py` passed.

## Boundary

The computation reuses the exact controlled P0.7 nominal solids and excludes intentional frame interfaces and the existing C06/C07 positive-stop pair. It does not include proposed new stop hardware, manufacturing/assembly tolerance, deformation, cables, guards, backlash, stopping travel or the received article.

R83 establishes nominal free space in the three study regions. It does not establish an as-built stop datum or a fabricable stop. Received stack/attachment metrology, topology selection, integrated CAD, load/tolerance analysis, bumper selection, FAI, physical proof and qualified review remain open. No gate is closed.

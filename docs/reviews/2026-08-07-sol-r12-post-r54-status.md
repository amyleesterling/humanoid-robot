# Sol R12 status after R54 exact-coordinate arm candidate

**Independent review identity:** Sol R12, 18 BLOCKER / 30 MAJOR / 8 MINOR findings against the pre-correction baseline

**Project response:** R54 / `HR-V0-ARM-ARCH-P0.1`

**Status:** PRELIMINARY—NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION

## Review accounting

The Sol summary supplied again on 2026-08-07 is the existing R12 independent review. It is not counted as a new review round. R54 is a project-owned correction response, not an independent approval.

Sol's central verdict remains correct: HR-V0 is technically plausible but not yet buildable or energizable, and HR-30W walking remains undemonstrated.

## R54 correction

R53 withdrew a false coplanar-frame assumption. R54 replaces it with a coherent exact-coordinate candidate:

- controlled XM540, H101, S102 and H104 STEP hashes govern the assembly;
- J2/S102 is rolled +90° about X and the straight-reference output is offset -90°;
- J1 and J2 use parallel `+X` axes with a candidate 191.5 mm spacing;
- the candidate H104 frame origin is 118.0 mm beyond J2, reserving 50.5 mm for the gripper/TCP inside the 360 mm object-center ceiling;
- explicit 4 × 4 transforms and interface planes are exported;
- native STEP and interactive GLB plus a readable SVG are generated;
- 23 sampled J2 poses from 15° through 125° show zero positive self-intersection in the modeled scope; and
- the revised allocation screen is 1.762 N·m at J1 and 0.478 N·m at J2, or 3.965/1.075 N·m with the existing 2.25 screen.

The candidate uses a conservative 20 × 40 mm envelope for an orderable 80/20 `20-2040` route. It does not invent or release the exact profile/end-tap geometry.

## Sol finding disposition

| Sol concern | R54 response | Still required |
|---|---|---|
| No buildable mechanical definition | **Narrowed, open.** Exact transforms and candidate native assembly now exist. | Exact member/end machining, adapter drawings/tolerances, fasteners, complete assemblies and signed release |
| No closed mass/inertia model | **Narrowed, open.** Candidate link mass and updated static screens exist. | Received mass, local COM/inertia, cable/fastener allocation and immutable as-built reconciliation |
| Continuous leg/arm torque unproved | **Open.** Static arm screen remains below momentary stall, but no continuous credit is claimed. | Current/thermal/duty/gearbox/side-load testing and qualified margins |
| Dynamic restraint, stopping and power-loss behavior insufficient | **Open.** R54 does not address these safety blockers. | Stops, guard/catch, restraint, measured stopping and power-loss validation |
| Evidence chain stops before fabrication | **Open.** No supplier packet was reactivated. | DFM, FAI, proof/cycle testing and qualified mechanical/electrical/functional-safety review |

## Gate consequence

`EG-005` remains partial. `MECH-005` / `AUDIT-MECH-012` remain open because fasteners, exact structural member geometry, tolerances, access, cables, continuous sweep, stress/slip/fatigue/impact evidence, physical fit, FAI and qualified review are absent. All active fabrication-RFI ZIPs remain at zero.

R54 closes no procurement, fabrication, assembly, energization or functional-safety gate.

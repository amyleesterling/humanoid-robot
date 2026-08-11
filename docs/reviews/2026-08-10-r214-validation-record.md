# R214 validation record

> **PRELIMINARY — NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

R214 identifier: `HR-V0-ARM-ARCH-P0.8-DWG-INTEGRATED-CANDIDATE`

## Repository evidence

- Five exact R213 STEP identities imported and preserved byte-for-byte.
- Ten transform rows and nine interface rows match the P0.7 analytical basis row-for-row.
- C01/C04/C05/C06/C07 controlled cylindrical hole axes match the expected patterns.
- Complete arm STEP and GLB regenerated from the exact imports.
- 40,001 sampled poses regenerated; zero positive-volume collision at or below the 115-degree J2 candidate soft limit.
- 69 continuous-clearance pairs / 135 certified leaf cells regenerated; minimum guaranteed nominal clearance 0.765783 mm.
- First nominal body contact remains 121.643289 degrees.
- J2 nominal metal-stop contact remains 117.999985 degrees against the 118-degree target.
- P0.8 custom-part rounded mass subtotal increases by 0.196 g; rounded shoulder/elbow gravity screens remain 2.018/0.515 N·m.
- P0.7 generator remains byte-identical to its controlled source.

## Fail-closed synchronization

- `HR-V0-CONFIG-REC-P0.3` carries 18 current records, 10 supersessions, eight BOM integration records, nine partial gate records, 19 open holds and 16 unexecuted acceptance rows.
- Firmware records P0.8 as the required mechanical identity, P0.7 as inherited kinematic basis and P0.2 as the custom-part manufacturing identity. Acceptance hashes remain `SELECTION REQUIRED`; target/HIL execution remains absent.
- EG-003, EG-005 and EG-006 remain `partial`.
- Build traveler remains 14 phases / 85 steps / 21 through-E2 gates; zero steps authorized or executed; BT-P13 remains prohibited.

## Checker results

- `tools/check_hr_v0_arm_architecture_p08.py`: PASS
- `tools/check_hr_v0_arm_integration_release_p08.py`: PASS
- `tools/check_hr_v0_configuration_reconciliation_p03.py`: PASS
- `tools/check_hr_v0_governance_control_p03.py`: PASS
- `tools/check_hr_v0_build_traveler_p01.py`: PASS
- `tools/check_hr_v0_firmware.py`: PASS; target flash, received-hardware execution and HIL not performed
- standard non-`pcbnew` repository checker sweep: 156/156 PASS
- native KiCad 10.0.5 / `pcbnew` checker sweep: 18/18 PASS
- `tools/check_hr_v0_release_manifest.py`: PASS; 4,030 staged candidate files covered
- `git diff --check`: PASS

## Interactive-guide QA

- `release/hr-v0/arm-architecture-p0.8-dwg-integrated/index.html`: desktop 1280 x 900 and mobile 390 x 844 viewport checks PASS; no horizontal overflow; minimum functional text 16 px and technical badges 14 px; warning visible; five evidence/download links returned HTTP 200.
- `release/hr-v0/configuration-reconciliation-p0.3/index.html`: desktop 1280 x 900 and mobile 390 x 844 viewport checks PASS; no horizontal overflow; minimum functional text 16 px and technical badges 14 px; warning visible; responsive cards reflow to one column.
- The browser backend's full-page screenshot stitch produced a malformed diagnostic image; normal viewport screenshots and DOM dimensions were correct. The malformed stitch is not retained as review evidence.

Passing source checks does not establish physical performance, functional safety, fabrication readiness or permission to energize. R214 remains a controlled repository candidate with zero physical gate closure and zero work authority.

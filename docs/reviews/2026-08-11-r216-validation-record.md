# R216 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-E2-EVIDENCE-P0.2`

## Repository checks

- Eight current configuration identities are controlled.
- Seven evidence inputs are SHA-256 bound.
- Twenty hardware logic cases are paired one-to-one with twenty software-authority cases.
- Every software record requires active trajectory `NONE`, torque-enable request `FALSE` and stale replay `REJECTED`.
- E2-SL-005 and E2-SL-019 explicitly retain the physically absent actuator source and disconnected/covered actuator-branch boundary while the K1/K2 coil path may be ON.
- The corrected P0.2 unpowered form has aligned current configuration fields; the release-candidate ID no longer occupies the manifest-hash field.
- The P0.2 authorization form remains `NOT AUTHORIZED` and requires both EG-021 evidence records plus four roles.
- Seven evidence holds remain OPEN with every authority flag false.
- EG-018 through EG-022 remain partial.

## Browser QA

- Desktop 1280 x 720: 17 px body text, 16 px controls, 14 px helper text, no horizontal overflow and twenty initial case rows.
- The ON filter returns only E2-SL-005 and E2-SL-019.
- Mobile 390 x 844: 17 px body text, 16 px controls, 14 px helper text, no horizontal overflow and block-reflowed case rows.
- The preliminary and current-disposition warnings remain visible.

## Validation state

- `tools/check_hr_v0_e2_evidence_parity_p02.py`: PASS.
- Pre-manifest standard repository sweep: 157 of 158 checks PASS; the sole failure was the expected fail-closed rejection of thirteen new, not-yet-staged R216 files.
- Native KiCad 10 / `pcbnew` sweep: 18 of 18 checks PASS, including the controlled native ERC/DRC checks inside those packages.
- Firmware source validation: PASS with 78 executable unit tests. Target flash, received-hardware execution and HIL remain NOT PERFORMED.
- Final staged-manifest standard repository sweep: 158 of 158 checks PASS.
- Release manifest regenerated from the Git index: 4,062 controlled package files.
- Clean-commit verification remains to be performed against the committed candidate; this record does not convert any open hold or grant work authority.

Passing checks establish only schema, identity, hash, pairing and presentation consistency. They do not establish site safety, physical wiring, electrical test results, functional-safety performance, stopping behavior, reviewer competence or permission to energize.

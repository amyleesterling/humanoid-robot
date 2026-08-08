# R91 validation record — elbow actuator and moving-mass architecture hold

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-08

Configuration: `HR-V0-ARM-ARCH-P0.7` / `HR-V0-ELBOW-TRADE-P0.1`

## Trigger and decision

The controlled P0.7 known/CAD-estimated moving subtotal is 692.758 g against the 750 g ceiling and omits mandatory frames, fasteners, bumper, gripper mechanics, connectors and moving cable. R91 therefore holds the R90 P0.7 custom-metal route and requires a separately identified exact-coordinate X430/P0.8 comparison. P0.7 remains controlled and XM430 remains unselected.

## Evidence verified

- Four bounded trade rows close arithmetically to 750 g: 57.242 g, 115.225 g, 140.242 g and 198.225 g provisional headroom.
- The X430 elbow sensitivity removes exactly 83.000 g of catalog actuator mass and changes the three-actuator catalog stall-current sum from 11.1 A to 9.0 A.
- The 4.1 N·m / 1.158 N·m value is labeled only as a 3.541 stall-endpoint ratio; no continuous-duty, safety-factor or connector-release credit is taken.
- Current official ROBOTIS pages confirm the XM430/XM540 masses, 12 V stall endpoints, no-load speeds and warning that stall torque differs from continuous/real-world output. Current ROBOTIS OpenMANIPULATOR-X pages provide feasibility context only.
- Five official X430/FR12 files were acquired through manufacturer download records. SHA-256 and byte identities are controlled. Three STEP files have valid ISO-10303-21 headers and parse in CadQuery 2.8.0; both drawings have valid PDF headers. No drawing dimensional audit or STEP-derived mass credit is claimed.
- Twelve architecture holds remain OPEN. All quote, procurement, fabrication, motion, connection and energization flags remain false.
- The interactive guide uses 17 px body text, 16 px table text, 13 px short badges, responsive cards and the dark-blue, sky-blue and golden-yellow palette.
- In-app browser inspection passed at the default desktop viewport and at 390 x 844 mobile. Mobile computed values were 16 px body, 16 px table and 13 px badge text with no horizontal page overflow. The slider changed from 120 g to 200 g and recomputed the first result to 892.758 g / 142.758 g over; the console reported zero warnings or errors.

## Executed checks

```text
tools/check_hr_v0_elbow_actuator_trade.py
node syntax check for the interactive guide script
git diff --check
repository-wide HR-V0 checker suite
tools/check_traceability.py
tools/check_energization_gates.py
tools/generate_release_manifest.py and tools/check_release_manifest.py
```

The package checker verifies all counts, source-file hashes and headers, arithmetic, hold states, warnings, supersession language, text-size floors and false authorization flags. The regenerated `HR-V0-RC-P0.1` manifest covers 1,084 package files; a clean exact-commit check follows the R91 commit.

The 40 non-manifest `check_hr_v0_*.py` checks pass with their controlled runtimes, including three KiCad 10.0.5 checks and three CadQuery-environment checks. With the release-manifest checker, the completed suite is 41/41. Traceability resolves 81 requirements, 40 risks, 109 procedures and 56 release/walking-document procedure references. The gate register remains deliberately not ready: 30 applicable, 0 closed, 22 partial and 8 open; through E2, all 21 applicable gates remain partial. `--require-ready` returns 2 as expected.

## Remaining evidence

Independent drawing/datum/tolerance audit; exact-coordinate P0.8 CAD; new adapters and hard stops; complete mass/COM/inertia; continuous/cyclic torque and thermal data; external branch-current/connector evidence; speed, acceleration, stopping and fault tests; complete collision/cable/guard sweep; structural calculations and proof; firmware and electrical synchronization; received hardware; and qualified mechanical/electrical/controls/functional-safety disposition all remain open.

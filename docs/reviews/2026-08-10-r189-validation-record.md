# R189 validation record

> **PRELIMINARY - CONFIGURATION EVIDENCE ONLY - NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Artifact: `HR-V0-CLEAN-CLONE-AUDIT-P0.1`

Date: 2026-08-10

## Executed result

An external fresh clone of exact source commit `221035ed307f4e3501abad82cf7afa42f6e7cc36` was created with `git clone --no-hardlinks` under Git 2.37.0.windows.1 and machine-level `core.autocrlf=true`.

- 132/132 non-`pcbnew` checks passed.
- 13/13 native KiCad `pcbnew` checks passed under KiCad 10.0.5.
- 145/145 total checker programs passed.
- The sorted checker-name list SHA-256 was `2cf09e2aa9a8245551dcb47b26c9596d8f23bf414e341aabe2f825790f4bdb1b`.
- `check_hr_v0_release_manifest.py --require-clean` passed over 3,206 controlled package files.
- `git status --porcelain` remained empty after the run.

The first three attempts and their failures remain recorded in the configuration package. No failed attempt was reclassified as a pass.

## Boundary

The result is software/configuration reproducibility evidence only. It executes no physical inspection, calculation acceptance, qualified review, connection, powered test, motion, fabrication, or energization. `EG-002` remains partial and all 30 energization gates remain unresolved.

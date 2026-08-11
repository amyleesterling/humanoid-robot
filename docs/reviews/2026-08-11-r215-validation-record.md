# R215 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-MECH-MFG-REVIEW-P0.1`

## Repository checks

- Five current custom-part identities are bound to five drawings, five DXFs, and five exact STEP hashes.
- Twenty-six unique drawing controls are represented; the two shared stop controls produce 28 per-part coverage assignments.
- All thirty FAI operations remain unexecuted.
- Nine integrated interfaces and six fastener candidates are exposed with received stack, torque/locking/reuse, fit, and proof evidence open.
- Twelve DFM questions remain not sent with no response.
- Twelve release holds remain open with external/physical evidence absent.
- All quotation, procurement, fabrication, assembly, connection, powered-test, motion, and energization flags remain false.

## Validation state

- `tools/check_hr_v0_mechanical_manufacturing_review_p01.py`: PASS.
- Standard non-`pcbnew` repository sweep: 157/157 PASS.
- Native KiCad 10.0.5 / `pcbnew` sweep: 18/18 PASS.
- Firmware source validation: 78 executable unit tests PASS; target flash, received-hardware execution, and HIL were not performed.
- Desktop guide QA at 1280 x 900: no horizontal overflow, 14 px minimum rendered text, warning visible, five part cards and twelve hold cards present.
- Mobile guide QA at 390 x 844: no horizontal overflow, 14 px minimum rendered text, warning visible and readable.
- Release manifest: 4,049 staged candidate files; checker PASS before commit.
- `git diff --check`: PASS.

The final release-manifest count and exact commit are recorded by the generated manifest and Git history. Passing checks establish only internal consistency and readable presentation. They do not establish machinability, structural adequacy, physical fit, functional safety, or work authority.

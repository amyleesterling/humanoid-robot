# R115 validation record

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

## Scope

R115 issues `HR-V0-GRIP-H104-SRC-P0.1`. It controls current official ROBOTIS endpoints 646/647/648, adds the official FR12-H104K DWG and proves that the current PDF/STEP payloads are byte-identical to the repository's already controlled copies.

## Validation boundary

The DWG signature, PDF/STEP hashes, file sizes and STEP solid geometry are checked. The manufacturer drawing was rendered at 220 dpi and visually inspected: title, date, units, non-scale state, one-sheet count and `FOR REFERENCE ONLY` warning are readable and unclipped.

Installed Google Chrome rendered the responsive guide at `1440 x 1000` and `390 x 844`. Both layouts had zero page-width overflow. Computed body/control text was 16 px, metadata 14 px and badges 12 px. All six evidence cards were visible in the unfiltered view; the Open-work filter showed exactly the three open cards. Desktop and mobile screenshots were visually inspected: warnings, cards, hashes and evidence flow were legible and unclipped.

All **68 unique repository checker programs passed**. Traceability resolves 81 requirements, 40 risks, 110 procedures and 57 release/walking-document procedure references. The deterministic release manifest contains **1,554 package files** before final clean-commit reproduction.

The intentional command `tools/check_energization_gates.py --through-stage E2 --require-ready` returned the expected exit code `2`: zero of the 21 gates applicable through E2 are closed, all 21 remain partial, and all 30 total gates remain unresolved. The package correctly refuses an energization-readiness claim.

`GDC-001..007`, `GRH-001/002`, complete mechanism, manufacturing definition, received-part evidence and every authorization remain open. No source file or clean checker authorizes work.

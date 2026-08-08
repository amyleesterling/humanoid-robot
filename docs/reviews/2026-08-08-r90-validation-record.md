# R90 validation record - Boston custom-metal route P0.2

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-08

Configuration: `HR-V0-ARM-ARCH-P0.7` / `HR-V0-FAB-SRC-P0.5` / `HR-V0-BOSTON-FAB-ROUTE-P0.2`

## Trigger

The Boston fabrication research initially recommended 4.75 mm SendCutSend plates. Direct reconciliation against the controlled P0.7 drawings showed that every C01/C04/C05/C06/C07 part is 9.525 mm nominal and 9.00..10.00 mm finished. Current provider evidence also showed that SendCutSend's published finished-process accuracy and automatic M5 countersink do not meet several controlled dimensions.

## Corrections verified

- The 4.75 mm suggestion is explicitly rejected in the current sourcing document, route package, interactive guide, handoff and configuration record.
- All five current parts remain 9.525 mm nominal; P0.7 geometry is unchanged.
- SendCutSend is excluded as a direct finished-part route. Its oversized 9.53 mm blank path is research-only and has no upload artifact.
- Xometry and Protolabs are bounded high-requirement CNC capability-inquiry candidates, not selected suppliers.
- Artisans Asylum's current page verifies a Bridgeport CNC mill but not the Project Button application capability.
- The decision package contains six routes, nine dated current source records and fifteen exact review-only geometry identities with recomputed byte counts and SHA-256 values.
- Every provider-contact, upload, quotation, supplier-selection, first-article, fabrication and energization authorization value is false.
- The interactive guide uses 16 px body text, 13 px badges, responsive cards and the project dark-blue, sky-blue and golden-yellow palette.

## Executed checks

```text
tools/check_hr_v0_r66_fabrication_sourcing.py
tools/check_hr_v0_boston_fabrication_route.py
node -e <interactive guide syntax check>
git diff --check
```

The package checker validates route/source/geometry counts, recomputes every geometry hash, verifies fail-closed warnings, the finished-part exclusion, corrected thickness, interactive-guide content and all false authorization flags. The embedded guide script parses successfully with the controlled Node runtime. The repository-wide checks and manifest are recorded in the final R90 validation output after this record is added.

The source-level suite passes 40/40 `check_hr_v0_*.py` checkers when the three KiCad-dependent checks use KiCad 10.0.5's bundled Python. Traceability resolves 81 requirements, 40 risks, 109 procedures and 56 release/walking-document procedure references. The full gate register remains deliberately not ready: 30 applicable, 0 closed, 22 partial and 8 open; through E2, all 21 applicable gates remain partial. `--require-ready` returns 2 as required by the unreleased state.

The regenerated `HR-V0-RC-P0.1` manifest covers 1,068 package files. A clean exact-commit check is performed after the R90 commit; the pre-commit check correctly identifies the working candidate as uncommitted and retains `EG-002` partial.

Browser-control navigation to the local `file:` artifact was denied by the browser security policy. No bypass was attempted. Static document, CSS, script, link and interaction-state checks were performed through the package checker; deployment rendering remains part of independent/page review.

## Remaining evidence

Qualified review of P0.7 drawings and stop controls; received H104/S102/40-4040 fit; bumper selection; C06/C07 load/tolerance/contact closure; written supplier capability; exact hashes; material/MTR acceptance; separate first articles; FAI/CMM evidence; proof; and qualified disposition remain open. No provider was contacted and no geometry was uploaded.

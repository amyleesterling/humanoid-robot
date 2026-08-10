# R107 validation record - FX103 output adapter P0.3

> **PRELIMINARY - NOT RELEASED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

R107 issues `HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.3` for independent review. It is not a machining or fastener-procurement release.

## Corrected defect

R107 found that P0.2's nominal 8.00 mm flange and 2.20 mm counterbore left 5.80 mm of grip. The ROBOTIS HN12 set's published supplied M2x3 screw therefore stopped 2.80 mm before the HN12 face and provided zero engagement. That stack is rejected.

P0.3 changes the C01 counterbore depth to 3.00 mm, leaving 5.00 mm nominal grip. Held MISUMI candidates `SCB2-8` and `CB4-15` produce nominal arithmetic screens of 3.00 mm HN12 engagement and 7.00 mm C01 transfer engagement. The CB4 head and current hub envelope have 1.05 mm nominal axial clearance, so the M4 screws must be installed and inspected before the hub and the hub must be removed before later M4 service. Tolerances, incomplete threads, bottoming, protrusion, torque, locking, reuse, corrosion, received-lot identity, manufacturer acceptance, joint analysis and physical proof remain open.

## Controlled sources

The current ROBOTIS HN12 set page and official drawing were checked on 2026-08-08. The drawing identifies eight M2.0 x 4 tapped-through holes; the product page identifies the supplied WB M2x3 hardware. The current MISUMI `SCB2-8` product record was checked on 2026-08-08 for the exact M2 x 0.4 x 8 candidate identity and published geometry/material/class data.

The controlled MISUMI CB catalog PDF has SHA-256 `B4EFA4D078609D61762BBA80B8E560767141B9E52BE4B5FEBD8337CA8C974102`, PDF creation/modification metadata dated 2015-11-05, no printed revision/date and one page. It was rendered at 180 dpi and visually inspected for the `CB4-15` identity, M4 x 0.7 full-thread listing, SCM435, black oxide, 38-43 HRC, catalog strength rank 12.9 and head/hex dimensions. Catalog properties are not Project Button allowables or an installation-torque basis.

## Artifact and visual checks

`tools/check_hr_v0_fx103_output_adapter_p03.py` passes. It rechecks the source hash, corrected geometry and supersession, two held fastener candidates, nineteen non-authorizing screens, six unexecuted assembly steps, seventeen unexecuted inspections, eight source rows, five parent-artifact hashes, seven unsent RFIs, four partial plus seven open holds and every false release flag.

The interactive guide was inspected at 1280 px desktop and 390 px mobile viewports. The local model-viewer runtime visibly rendered the GLB, the SVG drawing rendered without broken images, and the corrected design-record, fastener-candidate, assembly-sequence, analysis, inspection and hold links were present. Functional computed text was 14 px or larger. At mobile width the document itself had no horizontal overflow; the 1200 px drawing and 900 px evidence table remained inside their labeled horizontal-scroll regions. Desktop and mobile screenshots showed readable warnings, headings, body copy, model and drawing without clipping.

## Repository validation

Repository-wide validation passed:

- 56 non-manifest HR-V0 checks: 49 workspace-Python, three CadQuery and four KiCad 10.0.5 runtime checks;
- 47 executable firmware unit tests; target flash, received-hardware execution and HIL were not performed;
- 359 hash-controlled generated CAD artifacts and 16 vendor references;
- 81 requirements, 40 risks, 109 procedures and 56 release/walking-document procedure references; and
- 30 unresolved energization gates through E6: zero closed, 22 partial and eight open.

The intentional `--require-ready` gate check returned exit code 2. This is the required fail-closed result, not a validation failure.

The staged candidate manifest passes with 1,433 package files. A clean post-commit manifest check is required before handoff.

Sol's resupplied 18 BLOCKER / 30 MAJOR / 8 MINOR analysis remains the already logged independent R12 review of the pre-correction baseline. R107 is a project-owned correction and does not close or renumber that review.

No supplier was contacted. No quote, order, machining, assembly, connection, powered test, motion or energization occurred. Automated checks provide no physical evidence, functional-safety approval, fabrication authorization or permission to energize.

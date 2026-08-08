# R106 validation record - FX103 output adapter P0.2

> **PRELIMINARY - NOT RELEASED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

R106 issues `HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.2` for independent review. It is not a machining release.

## Corrected defect

The R103 one-piece concept is rejected. Its nominal 15 mm shaft stub overlapped both the PCD 16 horn-hole envelope by 0.600 mm and a nominal 3.8 mm M2 screw-head envelope by 1.400 mm. The horn screws and driver therefore had no buildable access path.

P0.2 separates the interface into `FX103-C01 P0.2` (horn flange) and `FX103-C02 P0.1` (shaft flange). The piloted M4 transfer joint keeps the HN12 screws accessible and leaves nominal clearances of 1.100 mm from the C01 pilot to the M2 head envelope, 2.350 mm between the two bolt-pattern envelopes, 3.000 mm from the C02 stub to the M4 head envelope, and 5.050 mm exposed stub before the selected hub's documented insertion depth. These are nominal geometry screens only, not strength, tolerance-stack, fatigue, or assembly approval.

## Controlled sources

The complete Carpenter Custom 630 PDF is hash-controlled at `BCE080D21EE992F6220A7346E7FF6BE3849543F41EF258EAF44DC17A82E44640`. It has PDF creation/modification metadata dated 2024-10-03, no printed revision, and twelve pages. Pages 1, 3, 6, 7 and 8 were rendered and visually inspected for product identity, available forms, density, heat-treatment condition, typical mechanical properties and process cautions. The package labels the published 7820 kg/m3 density, 869 MPa H1150 yield strength and 993 MPa tensile strength as typical values only. Its 600 MPa project screen is not an allowable. Finished Condition A is prohibited.

Six source-register rows separately control the Carpenter document, ROBOTIS HN12 model/drawing, current ROBOTIS product page, exact Ruland MJC33-15-A hub page, exact Ruland two-clamp/92Y bundle page, and the ASME Y14.5-2018 (R2024) identifier. Live manufacturer pages were accessed 2026-08-08. No unverified connector, fastener, material, process, rating or order selection was inferred.

## Artifact and visual checks

`tools/check_hr_v0_fx103_output_adapter.py` passes. It rechecks the source hashes, two-part topology, fifteen feature controls, fifteen non-authorizing arithmetic screens, six material/process controls, fourteen unexecuted inspections, seven unsent RFIs, three partial plus eight open holds, and every false release flag.

The final drawing was rendered at 2000 x 1450 and visually inspected. Dimensions, leaders, flange thickness, shaft length, two-part material lines, notes and warning are readable and unclipped. Functional drawing text is 20 px or larger.

The interactive guide was inspected at a 1440 px desktop viewport and a 390 px mobile viewport. The local model-viewer runtime loaded the GLB; the model, status panels, registers, drawing and warning remained present. Guide text has a 14 px computed minimum. At mobile width, the drawing intentionally preserves its annotation floor inside a labeled horizontal-scroll region instead of shrinking below legibility requirements.

## Repository validation

Repository-wide validation passed:

- 55 non-manifest HR-V0 checks: 49 workspace-Python, three CadQuery and three KiCad 10.0.5 runtime checks;
- 47 executable firmware unit tests; target flash, received-hardware execution and HIL were not performed;
- 342 hash-controlled generated CAD artifacts and 16 vendor references;
- 81 requirements, 40 risks, 109 procedures and 56 release/walking-document procedure references; and
- 30 unresolved energization gates through E6: zero closed, 22 partial and eight open.

The intentional `--require-ready` gate check returned exit code 2. This is the required fail-closed result, not a validation failure.

The staged candidate manifest passes with 1,407 package files. A clean post-commit manifest check is required before handoff.

No supplier was contacted. No quote, order, machining, assembly, connection, powered test, motion or energization occurred. Automated checks provide no physical evidence, functional-safety approval, fabrication authorization or permission to energize.

# R256 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R256 validates source-derived feature identity and blank execution controls only. It does not validate a received article, metrology method, result, tolerance, fit or assembly.

## Generated-package checks

- dedicated R256 checker: **PASS**;
- controlled STEP sources: **3**, all hash-bound;
- source-bound features: **79**, all reproduced from exact source face geometry and transforms;
- measurement characteristics: **18**, all `NOT EXECUTED` with blank results and uncertainty;
- HSI routes: **20/20 represented**;
- selections: **12**, all `SELECTION REQUIRED`;
- acceptance rows: **12 OPEN / NOT EXECUTED**;
- configuration P0.20: **39 current records, 31 supersession records, 109 open holds and 142 blank/unexecuted acceptance rows**; and
- package status: zero received results, providers, physical work, assembly, connection, powered testing, motion, energization, qualified approvals or safety credit.

- standard repository checker sweep under the project CadQuery runtime: **199/199 PASS**;
- native KiCad/`pcbnew` checker sweep under KiCad 10.0: **18/18 PASS**; R256 changes no ECAD source;
- staged release-candidate manifest: **5,805 package files; PASS before commit**; and
- `git diff --check`: **PASS**.

## Browser QA

At the default 1280 px viewport, the interactive guide renders with 16 px body text, 14 px technical-table text, no page-level horizontal overflow, eight sections, four tables and 129 data rows. Both source-derived SVG views load at their exact native dimensions, the GLB viewer is present with the expected source, and the browser console records no warning or error.

At a 390 x 844 px mobile viewport, body text remains 16 px and technical-table text remains 14 px. Page-level width stays inside the viewport, the model viewer is 430 px high, and all four wide tables retain their own horizontal scrollers. The temporary viewport override was reset after QA.

## Interpretation boundary

Source face indices are one-based within the exact controlled STEP imports under the project CadQuery/OpenCascade environment. Geometric signatures are independently recomputed by the checker. They identify CAD surfaces; they do not establish received conformity or stable topology across a different source revision.

No Sol R12 blocker, build gate, qualified-review gate, functional-safety claim or energization prerequisite closes through R256.

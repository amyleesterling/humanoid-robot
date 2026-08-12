# R252 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R252 validates a source-bound review model and a fail-closed evidence route. It does not validate a physical fixture or joint stack. No part was purchased, received, fabricated, assembled, connected, powered, moved, measured, inspected, accepted, or released.

## Executed repository checks

- dedicated R252 checker: **PASS**;
- exact controlled native STEP inputs: **3**;
- generated review STEP solids: **13** — three exact vendor parts, four structural review envelopes, and six contact envelopes;
- nominal contact screen: **6/6 tangent to the transformed S102 outer face; minimum nominal distance to imported XM540 = 6.750 mm**;
- controlled keepouts: **6**, all physical verification `NOT EXECUTED`;
- temporary-stack operations: **12**, all `NOT EXECUTED`;
- fixture selections: **12**, all `SELECTION REQUIRED`;
- fixture holds: **12 OPEN**;
- fixture acceptance rows: **10 OPEN / NOT EXECUTED**;
- configuration P0.16: **36 current records, 23 supersession records, 70 open holds, 103 open/unexecuted acceptance rows**;
- standard repository sweep: **195/195 PASS after staging and release-manifest regeneration**;
- native KiCad regression under KiCad 10.0: **18/18 PASS**; and
- release manifest: **recorded after staging; clean-tree validation rerun after commit**.

## Browser QA

At the 1280 px desktop viewport, the fixture guide renders with 16 px body text, 14 px minimum technical text, no page-level horizontal overflow, seven tables, 63 data rows, seven downloads, a 1184 x 596 px interactive GLB viewport, the exact warning, and the exact fail-closed status. The model visibly contains the dark-blue review frame, exact joint-stack source geometry, and gold contact envelopes.

The first P0.16 guide build incorrectly inherited the fixture viewer and requested a nonexistent local GLB. Browser QA caught the resulting empty panel and 404. The generator was corrected: P0.16 now has its own heading and status, contains five reconciliation tables and 243 rows, has no model viewer, produces no browser warning/error, uses 16 px body and 14 px minimum technical text, and has no page-level horizontal overflow.

Mobile configuration-guide QA at 390 x 844 px shows a 34 px wrapped heading, 16 px body text, readable warning/status text, and zero page-level horizontal overflow; wide technical tables remain intentionally scrollable inside their containers. A separate fixture-guide mobile viewport capture was not completed in this run; its shared 390 px CSS breakpoint and source minimums are machine-checked, but that is not substituted for a completed visual inspection.

## Interpretation boundary

The deterministic CAD result proves only that the chosen nominal contact envelopes touch the imported nominal S102 solid and do not intersect the imported nominal XM540 solid. It does not establish contact suitability, received tolerance, deformation, preload, restraint, structural strength, stability, metrology capability, uncertainty, wear, article safety, or a permissible temporary assembly.

No reviewer has accepted the fixture. No Sol blocker, build gate, functional-safety claim, or energization prerequisite closes through R252.

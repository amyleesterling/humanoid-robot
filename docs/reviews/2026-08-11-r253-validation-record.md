# R253 validation record

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

R253 validates a project-owned correction to the nominal fixture locating scheme. It does not validate a physical fixture, received joint stack, purchasing decision, or shop session.

## Executed checks

- dedicated R253 checker: **PASS**;
- P0.1 coplanar frictionless point-contact matrix: **rank 3**, therefore prohibited for fixture fabrication/session use;
- P0.2 normalized 3-2-1 matrix: **6 rows, rank 6, condition number 9.373695**;
- P0.2 exact B-rep screen: **6/6 contacts tangent to intended nominal S102 faces; zero intersection volume with S102, XM540 and H101**;
- smallest nominal contact-envelope clearance to XM540: **3.751956 mm**;
- generated review STEP: **13 solids** — three exact source parts, four structural review envelopes and six contact envelopes;
- controlled source bindings: **6/6 current hashes**;
- manufacturer-evidence rows: **4**, including the preserved XM540 `-T`/`-R` contradiction;
- keepouts: **7 NOT EXECUTED**;
- temporary-stack operations: **14 NOT EXECUTED**;
- selections: **14 SELECTION REQUIRED**;
- holds: **13 OPEN**;
- acceptance criteria: **12 OPEN / NOT EXECUTED**;
- configuration P0.17: **36 current records, 25 supersession records, 70 open holds and 103 open/unexecuted acceptance rows**;
- standard repository sweep: **196/196 PASS after staging and release-manifest regeneration**;
- native KiCad regression under KiCad 10.0: **18/18 PASS**; and
- release manifest: **recorded after staging; clean-tree validation rerun after commit**.

## Browser QA

At a 1280 px desktop viewport, the P0.2 guide renders with 16 px body text, 14 px minimum technical text, zero page-level horizontal overflow, ten tables, 83 data rows, ten downloads, an interactive 1184 × 596 px GLB model, exact preliminary warning and exact supersession/not-buildable status. The model visibly separates the gold A/B/C contact envelopes around the exact source stack. Browser console warning/error count is zero.

The P0.17 guide renders with 16 px body text, 14 px minimum technical text, zero page-level horizontal overflow, five tables, 245 data rows, five downloads, no empty model viewer, exact prohibition/status text, and zero browser console warnings/errors. Mobile visual execution was **NOT COMPLETED**.

## Interpretation boundary

Rank 6 establishes only nominal infinitesimal independence for six rigid frictionless point-contact normals. It does not prove unilateral seating, preload, restraint, stability, friction, edge-contact suitability, deformation, wear, tolerance, access, measurement uncertainty, repeatability, or physical safety. The manufacturer evidence verifies what the live official pages presently state; it does not resolve the same-page XM540 package contradiction or supply a project torque/reuse rule.

No physical result exists. No Sol blocker, build gate, qualified-review gate, functional-safety claim or energization prerequisite closes through R253.

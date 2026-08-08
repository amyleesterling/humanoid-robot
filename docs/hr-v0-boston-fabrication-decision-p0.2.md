# HR-V0 Boston custom-metal decision package P0.2

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Document ID: `HR-V0-BOSTON-FAB-ROUTE-P0.2`

Date: 2026-08-08

Parent geometry: `HR-V0-ARM-ARCH-P0.7`

Sourcing basis: `HR-V0-FAB-SRC-P0.5`

## Decision

The current five custom aluminum parts are plausible conventional CNC-mill work, but no supplier has accepted the drawings and no fabrication release exists. Use one high-requirement 3-axis CNC supplier for C01/C04/C05/C06/C07 after qualified mechanical review. Xometry is the primary capability-inquiry candidate and Protolabs is the alternate. This is a route ranking, not a supplier selection.

The earlier `4.75 mm` SendCutSend suggestion is rejected. Every current part is `9.525 mm` nominal with a `9.00..10.00 mm` finished range. SendCutSend is also excluded as a finished-part route because its published `+/-0.381 mm` accuracy and standard `10 mm` M5 countersink do not satisfy the P0.7 `+/-0.05 mm` feature controls, C06 `+/-0.025 mm` rail datum, C07 `<=0.03 mm` coplanarity, or `11.30 +0.10/-0.00 mm` project countersink.

Artisans Asylum's official page now confirms a Bridgeport CNC mill in Allston. That makes it a credible local capability, fixture, training or supplemental-inspection inquiry. It does not prove the required 6061 policy, operator/workholding/CAM method, tolerances, calibrated CMM result or FAI responsibility.

## Part-to-process decision

| Part | Critical controls | Current route | Release hold |
|---|---|---|---|
| C01 | 48 x 40 x 9.525 mm; four 2.70 mm holes at +/-0.05 mm; two 11.30 mm countersinks; flatness/parallelism | One-stop high-requirement CNC | Drawing/material review, written tolerance acceptance, MTR, separate FAI, received fit and proof |
| C04 | asymmetric H104 hole pattern plus C01 countersink/face controls | Same one-stop supplier | Received H104 fit; no slotting/bending/best-fit shift; FAI |
| C05 | S102 and column patterns at +/-0.05 mm in a controlled datum chain | Same one-stop supplier | Received S102/40-4040 stack, T-slot analysis/proof, FAI |
| C06 | twin striker rail datums at +/-0.025 mm from joint-hole datum | Same one-stop supplier with retained CMM results | Qualified stop review, bumper selection, load/tolerance/contact analysis and proof |
| C07 | 1.000 +/-0.05 mm face step and two rails coplanar <=0.03 mm | Same one-stop supplier with retained surface map | Qualified stop review, bumper selection, CMM surface map and proof |

## Controlled capability/DFM questions

These questions are prepared for a later authorized inquiry. They have not been sent.

1. Can the supplier bind its response to the exact STEP, DXF, drawing, revision, units and SHA-256 values without silent geometry or datum changes?
2. Can it supply 6061-T651 at nominal 9.525 mm and guarantee 9.00..10.00 mm finished thickness with one-heat-lot traceability and an MTR? Any substitute must be stated separately.
3. Can it hold every drawing control rather than portal defaults, including `+/-0.05 mm` locations/profile, specified hole limits, flatness `<=0.15 mm`, parallelism `<=0.10 mm`, and a 0.20..0.50 mm burr-free edge break?
4. Will it provide a first-article report with instrument/calibration identity, pin-gauge results, five-point thickness map, flatness/parallelism and CMM/optical coordinates?
5. For C01/C04/C06/C07, can it machine and report `11.30 +0.10/-0.00 mm`, 90-degree countersinks while preserving at least 5.80 mm measured residual and accepting the received-head functional gauge?
6. For C04, can the four asymmetric H104 coordinates be controlled independently without slotting or best-fit pattern shift?
7. For C05, will it control the S102 and column patterns in one setup or document the datum transfer and their relative-location inspection?
8. For C06, what workholding, datum transfer and CMM method will hold both rail datums to `+/-0.025 mm` relative to the four joint holes and report each rail separately?
9. For C07, can it machine the 1.000 mm step to `+/-0.05 mm` and demonstrate both rails coplanar within `0.03 mm` using a retained surface map?
10. Will it list every DFM exception, automatic radius/edge addition, stock substitution, tolerance relaxation, finish change, inspection exclusion and subcontracted operation before commercial action?
11. Can each distinct first article remain segregated from further work pending written acceptance with complete material and inspection traceability?
12. Does it acknowledge that a capability/DFM response is not authorization to fabricate?

## Controlled web artifacts

- `release/hr-v0/boston-fabrication-route-p0.2/index.html`
- `release/hr-v0/boston-fabrication-route-p0.2/route-comparison.csv`
- `release/hr-v0/boston-fabrication-route-p0.2/source-register.csv`
- `release/hr-v0/boston-fabrication-route-p0.2/geometry-file-register.csv`
- `release/hr-v0/boston-fabrication-route-p0.2/package-status.json`

The 15-row geometry register binds the current C01/C04/C05/C06/C07 DXF, STEP and readable SVG files to their exact byte counts and SHA-256 values for qualified review. Every row says `NO UPLOAD OR QUOTATION AUTHORITY`; it is not a supplier payload.

The [interactive guide](../release/hr-v0/boston-fabrication-route-p0.2/index.html) uses the project sky-blue, dark-blue and golden-yellow palette and exposes the decision by provider and disposition. The CSVs remain the machine-readable authority.

## Before any provider contact or upload

1. Obtain qualified mechanical acceptance of the exact P0.7 drawings, material controls and critical datums.
2. Close the received H104/S102/40-4040 interfaces and the C06/C07 bumper/load/tolerance design inputs.
3. Freeze the inquiry commit, file list and SHA-256 values.
4. Issue a separately authorized capability/DFM inquiry that cannot automatically submit an order.
5. Record the written response in `tests/forms/hr-v0-r69-fabrication-inquiry-template.csv` and resolve every exception.
6. If a supplier is later selected, issue a separate one-piece-per-geometry first-article authorization with numerical FAI acceptance. No existing file provides that authorization.

## Primary sources

- [Xometry CNC capability](https://www.xometry.com/capabilities/cnc-machining-service/), accessed 2026-08-08; live page, no formal revision exposed.
- [Protolabs precision machining tolerances](https://www.protolabs.com/services/cnc-machining/precision-machining-tolerances/), accessed 2026-08-08; live page, no formal revision exposed.
- [Protolabs aluminum CNC](https://www.protolabs.com/services/cnc-machining/aluminum/), accessed 2026-08-08; live page, no formal revision exposed.
- [SendCutSend countersinking](https://sendcutsend.com/services/countersinking/), accessed 2026-08-08; live page, no formal revision exposed.
- [SendCutSend 6061 aluminum](https://sendcutsend.com/materials/6061-aluminum/), accessed 2026-08-08; live page, no formal revision exposed.
- [Artisans Asylum machine shop](https://www.artisansasylum.com/shops/machine), accessed 2026-08-08; live page, no formal revision exposed.
- [OnlineMetals item 1249](https://www.onlinemetals.com/en/buy/aluminum/0-375-aluminum-plate-6061-t651/pid/1249), accessed 2026-08-08; live page, no formal revision exposed.

## Release boundary

No provider has been contacted, no supplier selected, and no file upload, quotation, purchase, first article, fabrication, assembly, motion or energization is authorized. A quote would be commercial evidence only and could not close structural, fit, proof, safety or energization gates.

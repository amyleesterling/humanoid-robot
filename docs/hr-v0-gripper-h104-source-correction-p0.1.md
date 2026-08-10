# HR-V0 FR12-H104K source-provenance correction

Document ID: **HR-V0-GRIP-H104-SRC-P0.1**

Date: 2026-08-08

Parent: `HR-V0-GRIP-CAD-ACQ-P0.1`

Requirements: `GRIP-002`, `MECH-005`, `MASS-002`

Verification: `AUDIT-GRIP-002`

Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

## Correction

The current ROBOTIS XC430-W240 e-Manual exposes official FR12-H104K DWG, PDF and STEP downloads through manufacturer endpoints 646, 647 and 648. R115 controls the endpoint, resolved payload URL, access date, document date, byte count, SHA-256 and file signature for each artifact.

The PDF and STEP are byte-for-byte identical to the H104 files already controlled in `cad/vendor/robotis/`. R115 therefore does not claim a new geometric discovery. It adds the previously uncontrolled DWG and a reproducible manufacturer-endpoint provenance chain for the complete three-file reference set.

## Verified source facts

- The PDF title block identifies `FR12-H104`, date `Aug-31-17`, units `mm`, one sheet, non-scale and `FOR REFERENCE ONLY`.
- The DWG begins with the `AC1015` signature.
- The STEP begins with `ISO-10303-21`, identifies `FR12-H104`, carries a 2017-08-31 file date and parses as one solid.
- The parsed STEP bounding box is 41.000000100 by 30.500000261 by 46.500000015 mm and its source-space volume is 4314.613722204 mm^3. These are file-correlation facts, not received-part tolerances, mass or material claims.
- The existing `FEAT-H104-001` four-cylinder subset remains bound to this identical STEP hash. Its arm-side nominal registration does not establish the separate H104-to-complete-gripper-carrier transform.

## What remains open

`GDC-001` through `GDC-007`, `GRH-001` and `GRH-002` remain open. The source set does not provide:

- the six-degree H104-to-`link5`/carrier assembly transform;
- the complete gripper mechanism, assembly mates or manufacturing tolerances;
- released material, fastener stack, torque, locking, retention or wear data;
- installed mass, center of mass or inertia;
- guarded moving envelope, usable opening or force/current characterization;
- received-part fit, first-article inspection, proof, cycle, drop or qualified review evidence.

No reference drawing or clean source checker is a fabrication release. This correction closes no requirement, physical verification record or energization gate.

## Controlled records

- `cad/vendor/robotis/fr12-h104k-r115/source-manifest-p0.1.csv`
- `cad/vendor/robotis/fr12-h104k-r115/geometry-summary-p0.1.csv`
- `cad/hr-v0/gripper-h104-source-disposition-p0.1.csv`
- `release/hr-v0/gripper-h104-source-p0.1/index.html`

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

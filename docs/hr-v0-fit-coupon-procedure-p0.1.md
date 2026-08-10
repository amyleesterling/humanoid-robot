# HR-V0 ROBOTIS PCD22 Fit-Coupon Procedure P0.1

**PRELIMINARY—UNPOWERED FIT INSPECTION ONLY. NOT A FABRICATION OR ENERGIZATION RELEASE.**

Procedure ID: `INSPECT-MECH-003`  
Coupon ID: `MV0-FC01`  
Mechanical baseline: `HR-V0-MECH-R0.1-PRELIMINARY`  
Record template: `tests/forms/hr-v0-fit-coupon-inspection-template.csv`

## Purpose and boundary

This procedure creates controlled physical evidence for the eight-hole, 22 mm pitch-circle interface used by the proposed HR-V0 ROBOTIS frames. It checks only the broad-face `8-Ø2.5 HOLE THRU / PCD Ø22 / 45°` pattern on received `FR13-H101K` and `FR13-S102K` parts. It does not verify the `FR13-S102K` side-face four-hole pattern, actuator fit, fastener strength, thread engagement, torque, structural capacity, alignment under load, or the final production tolerance stack.

The controlled manufacturer reference drawings are dated 2026-01-07 and marked `NONSCALE` and `FOR REFERENCE ONLY`. Their downloaded files and hashes are recorded in `cad/vendor/robotis/vendor-manifest.csv`. The received parts govern this fit inspection.

## Controlled coupon files

- `cad/hr-v0/generated/fit-coupons/MV0-FC01_robotis_pcd22_fit_coupon.dxf`
- `cad/hr-v0/generated/fit-coupons/MV0-FC01_robotis_pcd22_fit_coupon.step`
- `cad/hr-v0/generated/fit-coupons/MV0-FC01_robotis_pcd22_fit_coupon.stl`
- `cad/hr-v0/generated/fit-coupons/MV0-FC01_robotis_pcd22_fit_coupon_1to1_A4.svg`
- `cad/hr-v0/generated/SOURCE-MANIFEST.csv`

The coupon has eight candidate Ø2.70 mm clearance holes on a Ø22.00 mm pitch circle, a Ø38.0 mm outside diameter, Ø14.0 mm center clearance, and 2.0 mm nominal thickness. These are candidate inspection dimensions, not released production tolerances.

## Required items

- received `FR13-H101K` and `FR13-S102K` parts with packaging/labels retained;
- a coupon made from a low-cost nonstructural material such as PLA, acrylic, or plywood;
- printed 1:1 overlay if used, set to actual size/100% with all fit/shrink options disabled;
- traceable caliper or rule suitable for recording the two 100 mm print-scale checks;
- candidate M2.5 fastener or smooth gauge identified in the record; and
- camera and the controlled CSV record template.

Calibration status, coupon process/material, measuring instrument, fastener/gauge identity, and exact acceptance tolerances remain `SELECTION REQUIRED` before this can become a release inspection.

## Unpowered inspection

1. Confirm there is no electrical connection or stored mechanical energy. This inspection is entirely unpowered.
2. Photograph each received part, its label, packaging, part number, and serial/lot marking if present. Record discrepancies without relabeling the part.
3. Record the repository commit, mechanical revision, coupon filename, coupon SHA-256, and the manufacturer drawing SHA-256 from the controlled manifests.
4. If the paper overlay is used, print at actual size/100%. Measure and record both 100 mm scale bars. Do not use the overlay if either measured scale is outside the still-unreleased acceptance tolerance.
5. Record the coupon manufacturing method, material, nominal settings, and measured thickness. Inspect for obvious warp, burrs, elephant-foot, damaged holes, or print scaling.
6. Place the coupon on the `FR13-H101K` broad face. It must seat without bending, forcing, or removing material. Record center-clearance and flat-seating observations.
7. At each of the eight positions, insert the identified candidate M2.5 fastener or gauge by hand without cross-threading, prying, or drawing the coupon into alignment. Record every position separately and measure X/Y offset where the available method supports it.
8. Repeat steps 6–7 on the `FR13-S102K` broad face. Do not treat its side-face four-hole pattern as inspected.
9. Photograph the coupon seated on each frame and any nonconformance. Preserve raw images using the record references.
10. A failed or ambiguous position blocks production-hole release. Revise the candidate geometry only through configuration control, regenerate all formats and hashes, and repeat the inspection on both received frame types.

## Current disposition rule

This procedure may establish that the controlled coupon physically aligns with the received reference parts. It cannot issue a production release because the exact fastener, measuring method, process capability, positional/diameter tolerances, and acceptance limits remain `SELECTION REQUIRED`. Production metal remains blocked until those inputs are released, the final drawing stack is reviewed, and a qualified mechanical reviewer accepts the evidence.

No completed record authorizes fabrication, procurement, energization, or operation.

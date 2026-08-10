# HR-V0 conventional manufacturing drawing candidate P0.1

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-MECH-DWG-P0.1`

Candidate configuration: `HR-V0-ARM-ARCH-P0.8-DWG-CANDIDATE`

Controlled architecture remains: `HR-V0-ARM-ARCH-P0.7`

## Result

This package converts the R135/R136 file-definition findings into a five-part drawing candidate:

- five conventional SVG drawings with front/side views, overall dimensions, coordinate feature tables, exact source-control tables, thickness/finish/inspection notes and release warnings;
- five finished-profile/feature DXFs derived from the bound STEP outer wires;
- C06/C07 finished DXFs containing twelve LINE plus twelve ARC entities each, including the exact R2 finished corners absent from the earlier pre-fillet references;
- five hash-bound STEP/DXF/drawing triplets, using the R136 nominal-countersink candidates for C01/C04/C06/C07 and unchanged P0.7 C05;
- all 26 existing source controls mapped to explicit drawing content with zero schedule-bound rows;
- ICF-01 repeatable CMM registration for each part; and
- all 30 R134 FAI operations mapped to the candidate drawing, DXF and STEP identities while remaining unexecuted.

## Inspection registration

ICF-01 constrains the +Y broad face as the measurement Y plane; it is the non-countersink face where countersinks are present. It establishes X/Z using a rigid two-dimensional least-squares fit of the four small interface-hole centers to their nominal pattern. Translation and rotation are allowed; scale is prohibited; the transform, raw centers and each residual must be retained. This is a candidate CMM method, not a released ASME Y14.5 datum reference frame. Qualified drafting/metrology review must accept or replace it.

## Configuration boundary

The P0.8 drawing candidate is not selected. P0.7 remains controlled. No provider may receive or quote the files until independent review accepts the drawing/DXF/STEP semantics, formal datum treatment, material controls, inspection plan and supplier inquiry boundary.

## What remains open

Drawing completeness does not prove supplier capability, certified material, achieved tolerance, fastener seating, received fit, structural or stop strength, fatigue, impact, stopping, guarding or safety. Provider DFM, MTR, FAI, CMM records, received-article dry fit, proof testing and qualified release remain mandatory.

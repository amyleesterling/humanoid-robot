# HR-V0 Boston fabrication and RFQ route P0.1

**Identifier:** `HR-V0-FAB-RFQ-P0.1`
**Status:** **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY OR ENERGIZATION**

## Decision

The current custom aluminum parts are physically plausible but not released. `MV0-001` through `MV0-003` have two permitted quotation routes:

1. a one-stop CNC supplier receives the controlled finished STEP, readable drawing and exact hashes; or
2. a profile cutter receives only a hole-free `PROFILE_ONLY_RFQ` blank, followed by a qualified secondary shop drilling/milling to a separately frozen finished-part drawing.

The second route exists because the current 2.70 mm structural holes are not a defensible direct profile-cut feature. SendCutSend's current 6061 page gives an example minimum hole of 0.170 inch (4.318 mm), larger than 2.70 mm. Its quote and DFM response—not this project—determine actual acceptance. The final-geometry DXFs are therefore not permitted inputs to a profile-only order.

`MV0-004` remains on site hold until the Boston bench survey freezes the substrate, anchor fastener, slot geometry, edge distance and pull-out basis.

## Candidate routes

The machine-readable register is [`cad/hr-v0/manufacturing/hr-v0-fabrication-route-register.csv`](../cad/hr-v0/manufacturing/hr-v0-fabrication-route-register.csv). Candidate providers are not selected suppliers:

- Xometry and Protolabs are one-stop CNC quotation candidates. Written DFM and exact quote terms govern. Protolabs' advertised 6061-T651 must be reconciled with the project's current 6061-T6 material callout.
- SendCutSend is a profile-only blank candidate. It is not a released finished-hole supplier for this geometry.
- Artisans Asylum is a promising local Allston capability-confirmation, training, secondary-machining or inspection candidate because its current site lists machine, metal and CNC-plasma shops. The checked page does not establish a particular machine, tolerance, availability or accepted job.
- FabVille is a prototype/training candidate. Its current site explicitly describes education and prototyping rather than small-scale manufacturing.
- Checked Boston Public Library pages document design/software and MakerBot/PLA resources, but no suitable metal-machining capability was documented. BPL is excluded from the structural-metal route unless direct facility evidence changes that conclusion.

## Required quotation package

Use [`tests/forms/hr-v0-fabrication-supplier-quote-template.csv`](../tests/forms/hr-v0-fabrication-supplier-quote-template.csv). Every quote must bind the repository commit, RFQ revision, exact file names and SHA-256 hashes. It must explicitly answer material/temper, stock tolerance, process, finished-hole and location capability, flatness, edge treatment, certificates, inspection/FAI, lead time and cost.

For route `FAB-003`, preserve material traceability between the profile blank and secondary machining. The secondary shop must define its datum/fixture strategy and accept the finished drawing in writing. No shop may infer holes from a model intentionally marked as a blank.

## Release sequence

1. Complete the applicable received-interface coupons.
2. Freeze the finished hole sizes, locations, tolerances and fastener stack.
3. Generate and hash the finished RFQ package.
4. Obtain written DFM and comparable quotes for at least the chosen route.
5. Record qualified mechanical review of the selected route.
6. Issue a separate written authorization for one first article only.
7. Execute `INSPECT-MECH-009`, including certificates, raw measurements, photos and physical fit.
8. Resolve every nonconformance and issue a separate production/fabrication disposition.

No step above authorizes energization.

## Primary evidence

All pages below were rechecked 2026-08-07. No formal revision was exposed unless stated on the linked page.

- SendCutSend, [6061-T6 aluminum laser cutting service](https://sendcutsend.com/blog/6061-t6-aluminum-laser-cutting-service/)
- Xometry, [CNC machining service](https://www.xometry.com/capabilities/cnc-machining-service/)
- Protolabs, [CNC machining aluminum](https://www.protolabs.com/services/cnc-machining/aluminum/) and [machining tolerances](https://www.protolabs.com/services/cnc-machining/precision-machining-tolerances/)
- Artisans Asylum, [current Boston makerspace page](https://www.artisansasylum.com/home)
- FabVille, [current open-shop page](https://fabville.org/)
- Boston Public Library, [KBLIC](https://www.bpl.org/kblic/), [Teen Central](https://www.bpl.org/services-central-library/teen-central/) and [3D-printing guidelines](https://www.bpl.org/about-the-bpl/official-policies/kirstein-business-library-innovation-center-3d-printing-guidelines/)

These sources support capability screening only. A supplier quote, accepted DFM, first article, inspection evidence and qualified review remain mandatory.

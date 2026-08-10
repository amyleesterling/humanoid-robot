# HR-V0 passive arm-receiver detail P0.2

**PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Document ID: `HR-V0-PASSIVE-ARM-RECEIVER-DETAIL-P0.2`

Date: 2026-08-09

Controlled parents: `HR-V0-PASSIVE-ARM-RECEIVER-P0.1` and `HR-V0-PASSIVE-ARM-RECEIVER-VERIFY-P0.1`

Gates: `EG-008` and `EG-009` remain `partial`

## Decision

Advance the R127 raised receiver to a detailed review candidate. Replace its four anonymous linear-guide envelopes and anonymous 10 mm contact allocation with exact manufacturer candidates, add dimensioned fabrication blanks and a four-point independent backup-catch allocation, and make every unresolved interface explicit.

This is not a fabrication release. The issued DXF and STEP files intentionally contain **hole-free blanks**. Drilling, ordering configured rail lengths, purchasing impact components, attaching the receiver to the guard or base, and conducting powered tests remain prohibited until the controlled holds close.

## Controlled geometry

- receiver contact surface: `Z = 320.000 mm`;
- moving platen: `180 x 800 x 6.35 mm`;
- platen bottom: `Z = 304.125 mm`;
- contact layer: three `9.525 mm` nominal pieces covering `180 x 800 mm`;
- four guide axes: X `+/-110 mm`, Y `+/-350 mm`;
- three shock axes: Y `-300/0/+300 mm`;
- independent backup-catch top: `Z = 294.500 mm`;
- nominal catch gap: `9.625 mm`;
- MA30M catalog stroke: `8.128 mm`; and
- nominal residual between catalog full stroke and the backup catches: `1.497 mm`.

The detailed STEP occupies X `-125..125 mm`, Y `-430..430 mm`, and Z `20..320 mm`. Against the current guard reservation, that leaves `75 mm` on each X side and `20 mm` on each Y side. The R127 retained known-commanded-geometry clearance remains `63.106478 mm` because the contact top remains at Z `320 mm`.

The `1.497 mm` residual is not released clearance. Pad thickness tolerance alone is `+/-0.635 mm`; platen thickness, shock mounting, stop height, deformation, alignment and as-built uncertainty remain open. No part may be fabricated from the nominal stack.

## Exact candidates introduced

### Linear guidance

Four igus `TWA-01-20` automatic-clearance carriages on four `TS-01-20` rails are the controlled guide candidates. The candidate rail length is `120 mm`.

The current igus pages establish the product families, hard-anodized rail, carriage clearance behavior and current technical load tables. They do not expose a configuration-specific `120 mm` order code in the controlled evidence. The configured rail order code is therefore `SELECTION REQUIRED`; it is not inferred. Received size-20 CAD, rail holes, mounting interfaces, load orientation, moments, shock effects, life and igus application review remain open.

### Contact layer

Three Sorbothane `0212037-50-10` stock sheets are the exact material candidates. The manufacturer page identifies each as `12 x 12 x 0.375 in`, `50 +/-5` durometer, with `+/-0.025 in` thickness tolerance. Candidate cuts are:

- two pieces `180 x 266.7 mm`; and
- one piece `180 x 266.6 mm`.

Retention is `SELECTION REQUIRED`. Dynamic deflection, shape factor, force-travel behavior, rebound, wear, flammability and manufacturer suitability remain open. The stock material is not credited with absorbing the R125 energy allocation.

### Subframe joints

Eight 80/20 `20-4113` four-hole wide inside corner brackets are the exact post-to-rail candidates. The current manufacturer page identifies suggested hardware per bracket as four `11-5308` M5 x 8 mm BHSCS and four `14122` M5 slide-in economy T-nut blocks. The P0.2 BOM therefore carries 32 of each.

The product page publishes geometry and suggested hardware, not a receiver-specific joint allowable. Torque, engagement, reuse, slip, fatigue, unequal load sharing and proof remain open. The receiver-to-guard/base attachment and all site anchors remain `SELECTION REQUIRED`.

### Impact devices

Three ACE `MA30M` units remain exact evaluation candidates only. P0.2 adds mounting envelopes and a backup-stop allocation but does not close application sizing. Written ACE acceptance using measured mass, velocity, propelling force or torque, cycles, temperature and parallel-unit behavior remains mandatory.

## Fabricated blanks

The source generator issues:

- `FAB-REC-001`: `180 x 800 x 6.35 mm` platen blank;
- `FAB-REC-002`: `160 x 40 x 6.35 mm` shock-plate blank; and
- `FAB-REC-003`: `20 x 50 x 6.35 mm` guide-tab blank.

Each has STEP and DXF output. `FAB-REC-001` also has a dimensioned SVG. All remain hole-free because the received guide CAD, ACE mounting disposition, exact fasteners, tolerances and application reviews do not yet exist. Candidate material is 6061-T651 to the purchase-order edition of ASTM B209/B209M; the exact standard edition, supplier, certificate, thickness tolerance, flatness, edge finish and inspection criteria remain open.

## Load-path status

The retained `2,000 N` input is still a provisional screen, not peak force or proof load. P0.2 adds explicit arithmetic cases:

- three-shock ideal sharing: `666.667 N/unit`;
- two-shock ideal sharing after one unavailable unit: `1,000 N/unit`;
- four-catch ideal sharing: `500 N/catch`; and
- single-catch no-sharing screen: `2,000 N/catch`.

These values do not establish component ratings. Shock reaction, local contact, dynamic amplification, one-sided contact, guide side load, bracket capacity, rail joints, posts, braces, guard/base transfer and anchors remain open.

## Remaining holds

Twelve fail-closed groups remain. Four are `PARTIAL` because exact candidates and nominal geometry now exist; none is closed:

1. complete gripper, object and cable geometry;
2. measured mass, inertia, contact velocity and drive persistence;
3. ACE written application acceptance;
4. received igus CAD, configured rail identity and guide application proof;
5. Sorbothane retention and dynamic characterization;
6. platen material, final holes, tolerance, strength, fatigue and FAI;
7. subframe joints, base/guard path and anchors;
8. complete J1/J2 physical stops;
9. guard access, pinch, rebound and final-rest proof;
10. continued drive, regeneration, elastic and detached-part cases;
11. executed metrology, drop, backdrive and fault tests; and
12. qualified mechanical and functional-safety disposition plus written authorization.

The original 28 R127 physical-evidence records remain `NOT EXECUTED` and `NOT AUTHORIZED`.

## Primary sources

Every source and its access/revision state is recorded in `cad/hr-v0/generated/passive-arm-receiver-detail-p0.2/source-register.csv`. Current primary sources include:

- [ACE MA30M product page](https://www.acecontrols.com/us/products/automation-control/miniature-shock-absorbers/ma30-to-ma900/ma30m.html), live page with no formal revision exposed; accessed 2026-08-09.
- [ACE MA30-MA900 operating and mounting instructions](https://www.acecontrols.com/media/msimages/pdf/ACE_MA30-MA900_Operating-Mounting_EN_21_22_0019.pdf), document `21_22_0019`, Stand 03.2021, Issue 05.2022; accessed 2026-08-09.
- [igus TS-01 standard rail](https://www.igus.com/product/drylin_TS_01), live page with no formal revision exposed; accessed 2026-08-09.
- [igus TWA-01 automatic-clearance carriage](https://www.igus.com/product/drylin_TWA_01), live page, copyright 2026, no formal revision exposed; accessed 2026-08-09.
- [igus drylin T technical data](https://www.igus.com/linear-bearings/linear-guides-technical-data-drylin-t), live page with no formal revision exposed; accessed 2026-08-09.
- [80/20 20-2020](https://8020.net/20-2020.html), [20-2040](https://8020.net/20-2040.html), and [20-4113](https://8020.net/20-4113.html) product pages; live pages, accessed 2026-08-09 except the retained 20-2040 access dated 2026-08-07.
- [Sorbothane 12 x 12 sheet-stock product page](https://www.sorbothane.com/sorbothane-products/standard-industrial-products/product/sheet-stock-12-x-12/), live page, copyright 2026, no formal revision exposed; accessed 2026-08-09.
- [ASTM nonferrous standard listing](https://store.astm.org/products-services/standards-and-publications/standards/nonferrous-metal-standards-and-nonferrous-alloy-standards.html), listing `B209/B209M-21a` active at access; accessed 2026-08-09.

## Controlled artifacts

- `cad/hr-v0/generated/passive-arm-receiver-detail-p0.2/`
- `release/hr-v0/passive-arm-receiver-detail-p0.2/index.html`
- `tools/generate_hr_v0_passive_arm_receiver_detail.py`
- `tools/check_hr_v0_passive_arm_receiver_detail_p02.py`

This package releases no order, cut, hole, joint, adhesive, shock setting, attachment, test, motion or energization.

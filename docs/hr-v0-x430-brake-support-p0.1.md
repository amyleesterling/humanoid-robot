# HR-V0 X430 brake support P0.1

> **PRELIMINARY — BRAKE-SUPPORT/ERRATUM/RFI CANDIDATE ONLY — NOT APPROVED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-X430-BRAKE-SUP-P0.1`

Parents: `HR-V0-X430-LOAD-RIG-P0.1`; `HR-V0-X430-OUTPUT-IF-P0.1`

Date: 2026-08-08

## Controlled PT-series erratum

R102 interpreted the PT-series dimension `D = 14.5 mm` as plate thickness. Visual reinspection of the official `PT SERIES - US 02/2022` profile proves:

- `B = 375.0 mm` plate width;
- `C = 20.0 mm` plate thickness;
- `A = 25.0 mm` slot pitch;
- `D = 14.5 mm` lower T-slot width;
- `E = 8.0 mm` slot opening;
- `F = 12.0 mm` slot depth; and
- `G = 5.0 mm` lip depth.

The R102 generator and exports are corrected to a 600 × 375 × 20 mm envelope. R104 contains the current drawing-derived 15-slot profile. The manufacturer still has not provided PT-600 body CAD, profile tolerances, countersunk-hole locations, T-nut/bolt identities or structural/clamping allowables. The profile model omits countersunk holes and receives no fabrication or capacity credit.

Controlled PT PDF SHA-256: `5B1B991767A5801975485F22430931EBB6990B1E957D554CD8AE9B8D2CC00655`.

## Preferred manufacturer-support route

The current 2025 HB/MHB datasheet identifies Magtrol metric pillow-block assembly `4866` specifically for `HB/MHB-450M`. Its published dimensions are:

- `O = 117.3 mm` overall base width;
- `P = 104 mm` base-hole spacing;
- `Q = 12.7 mm` base thickness;
- `R = 76 mm` axis height;
- `S = 120.4 mm` overall height;
- `T = 14.2 mm`, `X = 6.4 mm`, and `Y = 12.7 mm` axial/base dimensions;
- `ØU = 60 mm` three-position brake pattern, listed for M5; and
- `2 × ØW = 6.6 mm` base holes.

This makes `4866` the preferred inquiry route rather than a project-invented brake bracket. The 2025 datasheet is locally controlled at SHA-256 `51B4AB9868D6E1380DFADA6E7A489A6D37F6A4B202AFF6107C75209AB61A6DC0`.

The accessory table is not production CAD. Magtrol has not supplied the current order/availability record, body CAD, center-opening dimension, material, mass, supplied fastener identities, installed tolerances, structural allowables, tightening method or written acceptance for an HB-450M-2/PT-600 characterization rig.

The R104 model therefore uses a simplified drawing-derived envelope. Its Ø50 center opening is an explicitly unqualified visual clearance that removes the exact brake boss/key envelope from the simplified solid. It is **not** a manufacturer dimension and may not be used for machining.

## FX104-C01 adapter review candidate

Direct nominal mounting does not close: `4866` base holes are 104 mm apart while four 25 mm PT pitches span 100 mm. Centering those patterns leaves a 2 mm offset per side. A separate adapter is required unless Magtrol supplies an accepted direct/special route.

`FX104-C01` is a 90 × 160 × 24 mm review candidate. Its nominal functions are:

1. place two candidate upper axes at the `4866` ±52 mm base-hole positions;
2. place four candidate lower Ø6.6 axes on PT slot centerlines at ±50 mm and at two X locations;
3. raise the pillow-block base by 24 mm; and
4. produce the nominal axis-height arithmetic `20 + 24 + 76 = 120 mm`.

The model contains two blind Ø5 review bores as candidate M6 tapped axes and four Ø6.6 review holes. These are not released threads or fastener selections. Material, heat treatment, finish, flatness, parallelism, perpendicularity, position, thread class/depth, surface finish, edge controls, fasteners, T-nuts, tightening, locking, slip resistance, fatigue, DFM, FAI and proof remain open.

The 24 mm adapter is deliberately not optimized. Its CAD volume is recorded with aluminum/steel mass sensitivities only so stationary fixture mass cannot disappear from the program model. No material is selected.

## Exact brake interface evidence

The controlled HB-450M drawing Rev A states:

- `3 × M5 × 0.8 - 6H`, 10.0 mm minimum depth;
- equally spaced on `Ø60.0` bolt circle;
- `Ø32 h3` front locating feature;
- `Ø15 h4` shaft and two `5 h9 × 5 h9 × 20` keys; and
- concentricity and perpendicularity statements of 0.08 in the drawing notes.

The exact brake STEP is placed on the R103 coaxial chain. The simplified 4866 envelope, adapter and PT profile show zero nominal B-Rep volume intersection after the explicitly nonfabrication center clearance is applied. Contact pairs are zero-volume nominal placement only. No tolerance, deformation, received-fit or alignment credit follows.

## Bounded load arithmetic

The 2025 catalog mass gives `5.85 kg × 9.80665 = 57.368903 N` brake weight. The exact STEP envelope extends at most 100.0082 mm behind the selected nominal mount plane, producing a conservative axial-envelope weight-moment screen of `5.737361 N·m`. This is not the actual center of mass.

Ideal brake-torque couples across the 104 mm `4866` base-hole span are:

- `3.2 / 0.104 = 30.769231 N`; and
- `4.1 / 0.104 = 39.423077 N` at the X430 stall endpoint.

These are ideal two-point arithmetic only. They provide no bracket, adapter, fastener, thread, PT lip, T-nut, friction, fatigue or fault-load capacity credit. The final load cases must include brake weight/COM, commanded and fault torque, coupling reactions, misalignment, start/stop reversal, cable loads, shock, guarding, proof factors and actual support/anchor behavior.

## Evidence boundary and next closures

R104 contains one erratum, four topology dispositions, seven BOM rows, nine dimension records, six interface records, eight bounded calculations, eight unsent RFIs, eight unexecuted inspections, two partial holds and ten open holds.

The package does not close:

- Magtrol application acceptance or the missing 4866/PT files;
- exact brake, pillow-block, adapter or T-slot fasteners;
- adapter or support structural/fatigue analysis;
- installed center height, coaxiality, parallelism, runout, end float or measurement uncertainty;
- coupling full-bearing-support and extraneous-load acceptance;
- brake power/control/flyback/thermal/fault behavior;
- common-bed countersunk attachments, site support, substrate or anchors;
- guard, catch, hot-surface and access protection;
- FUTEK/instrumentation/calibration closure; or
- the final configured FR12-H101 gravity/bearing/cable/moving-mass test and qualified powered-work authorization.

No supplier was contacted. No quote, order, machining, assembly, connection, powered test, motion or energization occurred. Every release flag remains false.

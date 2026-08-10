# HR-V0 FX103 output-adapter fabrication candidate P0.3

> **PRELIMINARY - FASTENER-STACK CORRECTION CANDIDATE ONLY - NOT RELEASED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.3`

Date: 2026-08-08

## Decision

P0.3 supersedes the P0.2 horn-flange fastener stack. It retains the two-piece topology, C02 shaft flange, material candidate, pilot, transfer pattern and coupling interface from R106, but changes `FX103-C01` to P0.3 by deepening the eight horn counterbores from 2.20 to 3.00 mm.

The exact MISUMI `SCB2-8` and `CB4-15` fasteners are controlled candidates on hold. They are not procurement or assembly selections. Torque, clamp load, friction, locking, reuse, corrosion, received-lot identity, manufacturer acceptance and physical proof remain unresolved.

## Defect found in P0.2

The HN12 reference drawing identifies eight `M2.0 x 4 TAP THRU` holes. The current ROBOTIS HN12 set page lists ten supplied `WB M2x3` screws.

P0.2 used an 8.00 mm flange with a 2.20 mm counterbore:

`8.00 - 2.20 = 5.80 mm nominal grip`

A 3.00 mm screw therefore stopped:

`5.80 - 3.00 = 2.80 mm`

before even reaching the horn face. It provided zero thread engagement. P0.2 was dimensioned but not assemblable with the published supplied fastener, so that stack is rejected.

## Corrected held stack

### HN12 to C01

- part: `FX103-C01 P0.3`;
- counterbore: eight `Ø4.0 +0.10/0 x 3.00 ±0.05 mm` on PCD 16;
- through hole: eight `Ø2.2 +0.05/0`;
- fastener candidate: MISUMI `SCB2-8`;
- published candidate: M2 x 0.4 x 8 mm, fully threaded, JIS SUSXM7, A2-70, nominal head Ø3.8 x 2 mm with 1.5 mm hex;
- nominal flange grip: `8.00 - 3.00 = 5.00 mm`;
- nominal horn engagement: `8.00 - 5.00 = 3.00 mm`.

The 3.00 mm result is nominal only. Screw-length tolerance, machined stack, face seating, HN12 thread form, thread start, protrusion, bottoming, material pairing, accepted engagement, torque, locking and reuse require lot-specific inspection and ROBOTIS disposition.

### C02 to C01

- fastener candidate: MISUMI `CB4-15`;
- published candidate: M4 x 0.7 x 15 mm, fully threaded, SCM435, black oxide, 38-43 HRC, catalog strength rank 12.9, nominal head Ø7 x 4 mm with 3 mm hex;
- nominal C02 grip: 8.00 mm;
- nominal C01 engagement: `15.00 - 8.00 = 7.00 mm`;
- nominal hub-face/head axial clearance: `5.05 - 4.00 = 1.05 mm`.

The M4 candidate must be installed and inspected before the coupling hub. The hub must be removed before later M4 service. Current orderability, length tolerance, incomplete-thread allowance, bearing/friction behavior, corrosion protection, torque/preload, locking, reuse and proof remain open.

## Capacity boundary

The P0.3 records retain the R106 7.9 N·m catalog-endpoint arithmetic only. Equal screw load sharing, joint friction, pilot torque transfer, HN12 capacity, thread capacity, slip, fatigue, shock, misalignment and proof acceptance are not established. The smooth Ø10 pilot receives zero positive torque-transfer credit.

The MISUMI property-class information is manufacturer catalog evidence, not a Project Button allowable or installation-torque basis. No preload or torque is released.

## Material and geometry retained

Both custom parts remain certified ASTM A564/A564M Type 630 / UNS S17400 17-4 PH stainless steel in H1150 condition. Finished Condition A remains prohibited. C02 remains `FX103-C02 P0.1`, including the Ø15.000 +0/-0.013 x 20 mm stub and R1 root.

The corrected nominal C01 CAD mass is 74.690841 g using the published typical 7820 kg/m3 density. C02 remains 100.916058 g. These are CAD/density estimates, not received measurements.

## Evidence package

The generated package contains:

- two native STEP part candidates plus STEP/GLB review assembly;
- a dimensioned, readable SVG drawing;
- fifteen feature controls;
- nineteen non-authorizing arithmetic screens;
- two exact fastener-candidate rows;
- six not-executed assembly-sequence rows;
- seventeen unexecuted inspection records;
- eight primary-source records with revision/access metadata;
- five SHA-bound parent-artifact rows;
- seven unsent RFIs; and
- four partial plus seven open holds.

Interactive guide: `release/hr-v0/fx103-output-adapter-p0.3/index.html`

Generated source: `cad/hr-v0/generated/fx103-output-adapter-p0.3/`

Generator/checker:

```powershell
& 'C:\Users\amyle\Documents\New project\.venvs\hr-v0-cad\Scripts\python.exe' tools\generate_hr_v0_fx103_output_adapter_p03.py
python tools\check_hr_v0_fx103_output_adapter_p03.py
```

## Release holds

Before quotation, procurement, machining, assembly or powered work, the package still requires:

1. written ROBOTIS acceptance of the HN12 external-brake application and SCB2-8 stack;
2. written Ruland and Magtrol application acceptance;
3. current orderability and received-lot inspection for both fasteners;
4. qualified torque/preload, friction, locking, corrosion and reuse disposition;
5. machine-shop DFM and returned ballooned inspection plan;
6. qualified joint, slip, thread, fatigue, horn/serration and fault-load analysis;
7. certified H1150 stock, completed FAI and physical fit;
8. executed static proof and post-proof inspection;
9. assembled coaxiality/runout/end-float/full-bearing-support evidence; and
10. the complete guarded brake rig, instrumentation, controls, anchoring and signed work authorization.

Every release flag remains false.

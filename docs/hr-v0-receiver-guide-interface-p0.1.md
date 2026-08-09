# HR-V0 receiver guide interface P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION, MOTION OR ENERGIZATION**

Document ID: `HR-V0-RECEIVER-GUIDE-IF-P0.1`

Date: 2026-08-09

Controlled parent: `HR-V0-PASSIVE-ARM-RECEIVER-DETAIL-P0.2`

Gates: `EG-008` and `EG-009` remain `partial`

## Correction

Reject R129 `FAB-REC-003`, the `20 x 50 x 6.35 mm` guide-tab envelope. The current official igus TWA-01 technical drawing and size-20 table place four K2 mounting threads on a `53 x 40 mm` rectangle. A `20 x 50 mm` face fails by `33 mm` in one orientation; rotated, it fails by `3 mm` and `20 mm`. It cannot connect the receiver platen to a TWA-01-20 carriage.

R130 replaces that invalid interface with the hole-free `FAB-REC-004` right-angle envelope:

- vertical face: `73 x 80 mm`;
- horizontal reach: `40 mm`;
- nominal wall: `6.35 mm`;
- one-piece machined 6061-T651 candidate, not a formed or welded part; and
- nominal mass: `0.142243 kg` each using the already controlled typical `2.70 g/cm3` density assumption.

The new face covers the catalog pattern with nominal `10 mm` transverse edge-center margin and approximately `19.5/20.5 mm` vertical edge-center margins. This is geometric coverage only. Hole diameters, counterbores, screw length and grade, washer, locking, thread engagement, material allowables, tool radii, tolerances, finish, FAI and proof remain `SELECTION REQUIRED`.

## Manufacturer coordinates

The current manufacturer evidence supports these catalog facts:

- exact carriage identity: igus `TWA-01-20`;
- carriage plan envelope: `63 x 81 mm`;
- carriage-body height displayed by the exact CAD viewer: `25 mm`;
- installed TWA/TS system height: `30 +/-0.35 mm`;
- K2 pattern: `53 x 40 mm`;
- K2 thread: `M6`;
- published K2 maximum torque: `1.84 N m`;
- TS-01-20 rail width `20 -0.2 mm`, height `12.3 mm`, pitch `60 mm`; and
- symmetric standard rail end spacing permitted from `20..49.5 mm`.

For the existing `120 mm` rail-length candidate, one `60 mm` pitch with symmetric ends produces `C5 = C6 = 30 mm`. That arithmetic is consistent with the published standard-pattern range. It is not a configured order code, received drawing or released hole definition.

## Controlled candidate centers

Sixteen K2 centers are recorded for the four carriage interfaces. In the receiver coordinate system:

- carriage faces are at X `-95` and `+95 mm`;
- each carriage row is Y `guide center +/-26.5 mm`; and
- the two vertical rows are Z `243.625` and `283.625 mm`.

Eight project-owned platen-attachment center candidates are X `-80/+80 mm`, Y `guide center +/-25 mm`, at platen datum Z `304.125 mm`. These are not manufacturer coordinates. Their diameters, hardware, edge requirements and strength remain open; the existing platen stays a hole-free blank.

## Corrected interface geometry

The review assembly orients each vertical rail so the carriage K2 face is inward toward the platen. A machined L-envelope bridges that vertical face to the platen underside. The revised guide/interface assembly remains inside the existing receiver envelope:

- X `-125..125 mm`;
- Y `-400..400 mm`; and
- Z `184.125..310.475 mm`.

No guard margin is reclaimed and the R127/R128 receiver contact surface remains unchanged.

## Mass and load boundary

The hole-free bracket volume is `52,682.4575 mm3`. Four bracket envelopes plus the R129 aluminum platen have a nominal known subtotal of `3.037851 kg`. This excludes Sorbothane, fasteners and the moving portions of the shock absorbers. It is an input that ACE must review; it is not an approved effective mass.

The official igus table publishes size-20 static values of `7,400 N` for C0Y/C0(-Y), `3,700 N` for C0Z and `85/45/45 N m` for M0X/M0Y/M0Z. They remain catalog data only. R130 does not establish peak impact reaction, which guide carries which component, dynamic amplification, four-guide sharing, life, alignment sensitivity, floating-bearing strategy, bracket strength, plate strength, rail-support strength or proof load.

Four independent fixed rails can overconstrain one rigid platen. The controlled supplier request therefore asks igus to prescribe the fixed/floating arrangement, alignment tolerances and application calculation. It remains `UNSENT`; no external contact has been authorized.

## CAD acquisition boundary

The exact official CADClick page displayed `TWA-01-20` and the `63 x 81 x 25 mm` body. The official technical drawing was inspected at its manufacturer asset URL. No STEP file was successfully acquired. R130 therefore uses catalog-coordinate reconstructions and plainly labels the carriage/rail geometry as envelopes. It does not call them received manufacturer CAD.

## Remaining holds

Ten fail-closed groups remain: two `PARTIAL`, eight `OPEN`, none closed.

1. received TWA and configured-rail CAD/revision identity;
2. configured 120 mm rail code and exact hole/counterbore/end tolerances;
3. complete K2 fastener stack and released torque;
4. platen-side fasteners and local structural evidence;
5. igus vertical shock/load/life/floating/alignment acceptance;
6. bracket material/process/tolerance/finish/FAI;
7. peak reactions and complete structural load-path allowables/proof;
8. received fit, stroke, binding, backlash, pull and fault/drop tests;
9. qualified mechanical and functional-safety review; and
10. written work authorization.

## Primary sources

Every source and revision/access state is recorded in `cad/hr-v0/generated/receiver-guide-interface-p0.1/source-register.csv`.

- [Exact TWA-01-20 product variant](https://www.igus.com/product/drylin_TWA_01?artnr=TWA-01-20), live official page, copyright 2026; accessed 2026-08-09.
- [Official TWA-01 technical drawing](https://igus.widen.net/content/ikczh6imai/png/Zg_drylinT_TWA-01.png), Widen asset `6dcadfe0-55b3-48fa-a7a5-6e20bc4ee05f`; no drawing revision exposed; accessed 2026-08-09.
- [Exact TWA-01-20 CAD viewer](https://www.igus-cad.com/default.aspx?cul=en-US&ArtNr=TWA-01-20&mandant=INT&parammode=), CADClick ccCatalog `1.17.0`, build `20260629.2`, ccAPI `3.5.5.0`; accessed 2026-08-09.
- [Official DryLin T catalog](https://www.igus.com/us/pdf/drylint.pdf), live PDF with no explicit document revision found; accessed 2026-08-09.
- [Official vertical system-design page](https://www.igus.com/linear-bearings/linear-guides-drylin-t-system-design-vertical-ca), live page with no formal revision exposed; accessed 2026-08-09.
- [Official no-hole clear-anodized rail alternate](https://www.igus.com/product/drylin_TS_01_CA), exact `TS-01-20-CA-S` alternate identity; not selected; accessed 2026-08-09.

## Controlled artifacts

- `cad/hr-v0/generated/receiver-guide-interface-p0.1/`
- `release/hr-v0/receiver-guide-interface-p0.1/index.html`
- `tools/generate_hr_v0_receiver_guide_interface.py`
- `tools/check_hr_v0_receiver_guide_interface_p01.py`

This package releases no order, hole, fastener, machining operation, rail configuration, load rating, test, motion or energization.

# HR-V0 FX103 output-adapter fabrication candidate P0.2

> **PRELIMINARY - TWO-PIECE OUTPUT-ADAPTER FABRICATION CANDIDATE ONLY - NOT RELEASED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-FX103-OUTPUT-ADAPTER-FAB-P0.2`

Parent: `HR-V0-X430-OUTPUT-IF-P0.1`

Date: 2026-08-08

## Result

R106 rejects the R103 one-piece `FX103-C01` review geometry and replaces it with two independently inspectable part-definition candidates:

- `FX103-C01 P0.2`, an HN12 horn flange; and
- `FX103-C02 P0.1`, a piloted shaft flange carrying the 15 mm coupling stub.

This is a design correction and independent-review package, not a machining release. No manufacturer, supplier, machine shop, metrology provider or qualified reviewer has accepted it. No stock, fastener, horn, coupling or brake has been ordered or received.

## Defect found in the R103 geometry

R103 placed a `Ø15 mm` integral shaft around eight `Ø2.2 mm` holes on the HN12 `PCD Ø16 mm` pattern. The shaft radius is 7.5 mm and the hole-center radius is 8 mm. The nominal hole envelope therefore overlaps the shaft by:

`7.5 - (8.0 - 1.1) = 0.600 mm`

A nominal `Ø3.8 mm` M2 screw-head review envelope would overlap the shaft by 1.400 mm. A straight driver also cannot reach the recessed horn fasteners through the shaft. The one-piece geometry was therefore not manufacturable or assemblable as represented. It receives no quotation, machining, assembly or load-path credit.

## Corrected topology

`FX103-C01 P0.2` mounts to the HN12 first. Its eight `Ø2.2 +0.05/0 THRU` holes and `Ø4.0 +0.10/0 x 2.20 ±0.05 mm` counterbores remain on `PCD Ø16 BASIC`. The exact M2 screw order identity, head geometry, length, engagement, torque, locking and reuse rules remain **SELECTION REQUIRED** and require ROBOTIS acceptance.

C01 then provides:

- a `Ø10 h6 x 2.00 ±0.03 mm` alignment pilot; and
- four `M4 x 0.7 - 6H`, 6.0 mm minimum-full-thread features on `PCD Ø28 BASIC`, phased `22.5° BASIC` from the HN12 pattern.

`FX103-C02 P0.1` contains:

- the mating `Ø10 H7 x 2.20 ±0.05 mm` pilot pocket;
- four `Ø4.5 +0.10/0 THRU` transfer holes on the same PCD and phase;
- a `Ø15.000 +0/-0.013 x 20.00 ±0.05 mm` coupling stub;
- `0.03 mm` total-runout control and `Ra 0.8 µm` maximum on the stub; and
- a controlled `R1.0 ±0.1 mm` smooth shaft-root fillet.

The 10 mm pilot receives alignment credit only. A smooth circular clearance/transition pilot has zero positive torque-transfer credit without an accepted interference, key or clamped-friction design. Torque transfer remains assigned to the separately reviewed fastened joint.

## Nominal tool-access result

Using review envelopes only:

- C01's `Ø10` pilot has 1.100 mm radial clearance to a nominal `Ø3.8` M2 head envelope;
- the PCD-16 `Ø4.0` counterbore envelope has 2.350 mm radial clearance to the PCD-28 `Ø3.3` tap-drill envelope;
- C02's `Ø15` stub has 3.000 mm radial clearance to a nominal `Ø7.0` M4 head envelope; and
- the 20 mm stub with 14.95 mm hub insertion leaves 5.050 mm nominal axial space between the flange and hub.

These are geometry screens, not tool or assembly acceptance. Exact screw heads, drivers, torque tools, tolerances, chamfers, hub placement and service sequence remain subject to DFM and physical proof.

## Material candidate

Both parts are specified as certified `17-4 PH stainless steel, UNS S17400, ASTM A564/A564M Type 630, condition H1150`, machined from round bar at least 40 mm in diameter. The finished parts may not remain in Condition A. No welding, plating, repair, alloy/condition substitution or unapproved post-machining treatment is permitted.

The controlled Carpenter Custom 630 datasheet has PDF metadata dated 2024-10-03 and no printed revision. It lists ASTM A564, round-bar manufacture and **typical** H1150 properties of 7,820 kg/m³ density, 869 MPa 0.2% yield strength and 993 MPa ultimate strength. R106 uses 600 MPa only as a project screening basis. Neither the typical value nor the project screen is a released allowable or certificate minimum.

Cleaning/passivation, galvanic disposition against the received HN12/coupling, final machining sequence, material certificate content and positive material identification remain subject to qualified materials/DFM review.

## Adapter-only arithmetic

At the Ruland 7.9 N·m peak endpoint:

- ideal equal tangential load is 123.4375 N per HN12 screw at the eight-hole, 8 mm-radius pattern;
- ideal equal tangential load is 141.0714 N per transfer screw at the four-hole, 14 mm-radius pattern;
- nominal solid-shaft torsional shear is 11.9523 MPa at the minimum 14.987 mm stub diameter; and
- a simplified uniform internal-thread shear screen is 2.3085 MPa for each 6 mm-deep M4 thread.

At the Ruland 3.96 N·m rated endpoint, nominal shaft torsional shear is 5.9913 MPa. These values do not establish project duty, fatigue life, preload, slip, horn/serration/thread capacity, fastener suitability, fillet stress concentration, misalignment response, shock capacity, containment or proof acceptance.

Nominal CAD/density masses are 75.130 g for C01 and 100.916 g for C02. Received mass remains unmeasured.

## Controlled evidence

The package contains:

- two nominal part STEP files and a review assembly STEP/GLB;
- a dimensioned human-readable SVG drawing;
- fifteen feature controls;
- fifteen reproducible geometry/material/load-path screens;
- six material/process controls;
- fourteen unexecuted FAI, proof and alignment records;
- six primary-source records with revision/access metadata, including separate exact Ruland hub and two-clamp 92Y bundle records;
- three SHA-bound R103 parent artifacts;
- seven unsent manufacturer/DFM/reviewer RFIs; and
- three partial and eight open release holds.

All thread geometry in the STEP files is represented by nominal tap-drill bores. The drawings and feature register control the thread callouts.

## Remaining release holds

The package remains blocked by:

- qualified review of the topology, GD&T, torque path, joint slip, stress, fatigue and proof basis;
- written ROBOTIS acceptance and exact HN12 fastener/engagement/torque/locking rules;
- written Ruland acceptance of the coupling, fit, support, insertion, gap, reversal spectrum and proof;
- machine-shop and metrology DFM;
- exact M2/M4 fastener order identities and complete joint controls;
- received H1150 certificates, heat/lot trace and signed FAI;
- an approved and executed static proof with post-proof inspection;
- assembled coaxiality, runout, end-float and uncertainty evidence;
- the complete guarded brake rig, controls, instrumentation, anchoring and powered-work authorization; and
- the final configured FR12-H101 gravity/bearing/cable/moving-mass test.

Every quotation, procurement, machining, assembly, connection, powered-test, motion, energization, safety-credit and build-release flag remains false.

## Interactive and machine-readable package

- Interactive guide: `release/hr-v0/fx103-output-adapter-p0.2/index.html`
- C01 STEP: `cad/hr-v0/generated/fx103-output-adapter-p0.2/FX103-C01_P0.2_horn_flange.step`
- C02 STEP: `cad/hr-v0/generated/fx103-output-adapter-p0.2/FX103-C02_P0.1_shaft_flange.step`
- Drawing: `cad/hr-v0/generated/fx103-output-adapter-p0.2/FX103_output_adapter_P0.2_drawing.svg`
- Feature, analysis, process, inspection, source, parent, hold and RFI registers: `cad/hr-v0/generated/fx103-output-adapter-p0.2/`

Automated geometry and arithmetic are not physical evidence or permission to fabricate or energize.

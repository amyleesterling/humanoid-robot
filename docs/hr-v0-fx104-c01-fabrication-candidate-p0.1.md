# HR-V0 FX104-C01 adapter fabrication candidate P0.1

> **PRELIMINARY - ADAPTER FABRICATION CANDIDATE ONLY - NOT RELEASED FOR QUOTATION, PROCUREMENT, MACHINING, ASSEMBLY, CONNECTION, POWERED TEST, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-FX104-C01-FAB-P0.1`

Parent: `HR-V0-X430-BRAKE-SUP-P0.1`

Date: 2026-08-08

## Result

R105 converts `FX104-C01` from an untoleranced review solid into a complete **part-definition candidate for independent review**. It defines the material, nominal STEP, dimensioned SVG drawing, datums, feature tolerances, thread/depth requirements, surface requirements, process restrictions, analysis screens, first-article inspection route and machine-shop DFM questions.

It is not a machining release. No supplier has reviewed it; no material, fastener or T-nut has been ordered; no part has been machined, inspected or proof-tested.

## Controlled part definition

The candidate is a `90.00 x 160.00 x 24.00 mm` plate with:

- two `M6 x 1 - 6H` blind tapped holes at `X = 0`, `Y = +/-52 mm` basic for the published Magtrol `4866` base axes;
- 12 mm minimum full thread and an `Ø5.0 x 18 mm minimum` blind drill requirement;
- four `Ø6.6 THRU` holes at `X = +/-30`, `Y = +/-50 mm` basic for the PT slot axes;
- datum A on the bottom PT-contact face, datum B on the X-min long side and datum C on the Y-min short side;
- datum-A flatness `0.05 mm`, top-face parallelism `0.05 mm` to A and `Ra 3.2 µm` maximum on both contact faces;
- `Ø0.10 mm` position for the two tapped axes and `Ø0.20 mm` position for the four through axes relative to A|B|C;
- 0.2-0.5 mm edge breaks, burr removal and clean/dry delivery; and
- as-machined surfaces with no anodize, conversion coating, welding or heat treatment.

The STEP contains nominal drilled-hole geometry but no modeled thread helix. The drawing and feature register control the threads.

## Material decision

Material is specified as certified `6061-T651 aluminum plate, ASTM B209`, machined from stock at least 25.4 mm thick. Alloy/temper substitution is prohibited. The supplier must provide a certificate containing the alloy, temper, product form, heat/lot trace and applicable ASTM B209 compliance.

Kaiser's controlled technical sheet publishes **typical**, not minimum, T6/T651 properties of 310 MPa ultimate tensile strength, 276 MPa yield strength, 207 MPa ultimate shear strength, 97 MPa reversed-stress fatigue endurance at `5 x 10^8` cycles, 68.3 GPa elastic modulus and 2.70 Mg/m³ density. Its engineering-plate sheet covers 6061-T651 general-engineering plate from 6.35 through 254 mm. R105 uses 240 MPa only as a project screening basis below the published typical value. It is not a material guarantee or released allowable.

Controlled source hashes:

- Kaiser 6061 technical data: `93BF49F80542098953171C9FB72E4AF72505AA8204AE39A4AFB97102A69EEC05`;
- KaiserSelect engineering plate: `7E8CF6D3C71336519DB010D2C908BDBE732E47F7D9F4A4BA6F5CA67063040341`.

## Adapter-only load screens

The candidate screens, but does not release, two project load cases:

1. `3.0 x` the conservative R104 brake-weight moment: `5.737361 x 3 = 17.212082 N·m`.
2. `2.0 x` the X430 4.1 N·m stall endpoint: `4.1 x 2 = 8.2 N·m`.

At the ideal four-hole lower pattern, the weight case gives 143.434 N tension per bolt on the tension-side row and 149.748 N combined tension/shear per lower bolt. Using the deliberately conservative gross-section modulus `90 x 24² / 6 = 8,640 mm³` gives 1.992 MPa nominal bending stress. The 240 MPa project basis divided by that stress is 120.474. Nominal lower-hole bearing is 0.945 MPa. The torque case gives a 78.846 N ideal couple at the two upper axes and a simplified 0.425 MPa uniform internal-thread shear screen at 12 mm engagement.

These ratios are not safety factors for the assembled support. They omit local stress, contact, preload scatter, slip, fatigue spectrum, manufacturing variation, received material properties, 4866 body/load-transfer behavior, PT lip/T-nut capacity, misalignment, shock, cable/guard loads and common-bed behavior. The `4866` has only two base holes at one axial station, so its transfer of the brake's axial weight moment into the adapter cannot be closed without manufacturer geometry/allowables and qualified review.

## Inspection and configuration controls

Nine FAI/proof records remain `NOT EXECUTED`. They require certificate review; overall and thickness measurements; datum flatness/parallelism and surface-finish checks; thread and through-hole CMM/gage inspection; edge/cleaning review; a ballooned signed FAI; and a separately approved proof/reinspection procedure.

Three parent artifacts are SHA-bound so their published 4866/PT axes and load basis cannot silently move. Five DFM/manufacturer/reviewer RFIs are prepared and unsent.

## Remaining release holds

R105 has three partial and seven open holds. They retain:

- Magtrol `4866` and PT current files, tolerances, hardware, allowables and written application acceptance;
- qualified drawing, GD&T, load-case, calculation and proof review;
- machine-shop DFM and traceable stock availability;
- exact fastener/T-nut stacks, preload, locking, torque and reuse controls;
- received material certificate and signed FAI;
- an approved and executed adapter/support proof;
- installed alignment/runout/end-float evidence;
- complete guard, brake controls, instrumentation, anchoring and powered-work authorization; and
- the final configured `FR12-H101` test and qualified acceptance.

Every quotation, procurement, machining, assembly, connection, powered-test, motion, energization, safety-credit and build-release flag remains false.

## Interactive and machine-readable package

- Interactive guide: `release/hr-v0/fx104-c01-p0.1/index.html`
- Nominal STEP: `cad/hr-v0/generated/fx104-c01-p0.1/FX104-C01_P0.1_fabrication_candidate.step`
- Dimensioned drawing: `cad/hr-v0/generated/fx104-c01-p0.1/FX104-C01_P0.1_drawing.svg`
- Feature, analysis, process, inspection, source, parent, hold and DFM registers: `cad/hr-v0/generated/fx104-c01-p0.1/`

Automated geometry and arithmetic are not physical evidence or permission to fabricate or energize.

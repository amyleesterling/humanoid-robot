# HR-V0 gripper requirement and selection correction P0.1

Identifier: **HR-V0-GRIP-SEL-P0.1**
Status: **PRELIMINARY - NO GRIPPER SELECTED; NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**
Date: 2026-08-08
Correction round: R113

## Decision

No HR-V0 gripper candidate is selected. The current 40-70 mm each-principal-dimension payload envelope is retained as the fail-closed selection baseline until an authorized requirement change says otherwise.

R111 incorrectly treated `SYS-002` as the complete object definition and proposed a 25-30 mm foam cube. `SYS-002` supplies an upper bound, but `docs/system-specification.md` revision 0.1 also supplies a 40 mm minimum for every principal dimension. The smaller-object proposal is therefore not part of the current baseline.

This correction supersedes only the R111/R112 **preference conclusion**. It does not erase their controlled manufacturer files, geometry, interface studies, hashes, calculations, KiCad source, or historical records.

## Candidate screen

| Candidate | Controlled opening evidence | Current baseline disposition | Selection state |
|---|---:|---|---|
| ROBOTIS RM-X52 proposal | Manufacturer publishes 20-75 mm stroke; installed padded usable opening remains unverified | Conditionally compatible only | Not selected; source, transform, pad, force, mass, guard and physical evidence held |
| Pololu item 3551 | 32 mm internal opening | **Fails** the retained 40 mm minimum by 8 mm before pads, tolerances and uncertainty | Conditional study only; not selected |
| ServoCity 3219-0002-0002 | No usable-opening value found in the controlled official product, assembly, specification or STEP records | Unverified; receives no numerical compliance credit | Not selected |

The screening rule is conservative: a candidate receives no compliance credit unless the controlled published or measured **installed usable opening**, including released pads and uncertainty, covers the released object grip-axis width. CAD appearance, catalog bounding boxes, foam compressibility and visual estimates are not substitutes.

## Requirement decision

Two branches are possible, but neither is silently assumed:

1. **Retain the current 40-70 mm baseline.** Pololu 3551 is disqualified for this task. Continue the ROBOTIS evidence route or identify another source-controlled gripper with adequate installed opening.
2. **Propose a smaller object.** The 25-30 mm cube becomes eligible for engineering evaluation only after program-owner approval, exact object/nest/receiver definition, requirement and test updates, risk review, pad/tolerance closure and configuration control. Approval is currently `SELECTION REQUIRED`.

`GRIP-002` separately names the ROBOTIS mechanism. Selecting Pololu, ServoCity or any other alternate requires an approved change to that solution-specific requirement even if the object opening closes.

## Sources and verification boundary

- Project Button `requirements/requirements.csv`, `SYS-002` and `GRIP-002`, program baseline HR-30-SYS-R0.2, checked 2026-08-08.
- Project Button `docs/system-specification.md`, document HR-SYS-001 revision 0.1, section 2, checked 2026-08-08.
- Pololu item 3551 official [specification page](https://www.pololu.com/product/3551/specs), [resources](https://www.pololu.com/product/3551/resources), and dimension drawing dated 2018-08-31, accessed and hash-controlled 2026-08-08.
- ROBOTIS official [OpenMANIPULATOR-X e-Manual](https://emanual.robotis.com/docs/en/platform/openmanipulator_x/specification/), accessed 2026-08-08, plus controlled upstream source commit `9187eca0920458be04d2399906388f55242f81f1`.
- ServoCity official [3219-0002-0002 product resources](https://www.servocity.com/servo-driven-gripper-kit-servo-included/), accessed and hash-controlled 2026-08-08. The reviewed official documents do not publish a usable-opening value.

Manufacturer catalog data are not received-part evidence. The ROBOTIS stroke is not credited as installed padded opening. No grip force, retention, drop, wear, lifetime, safety performance or functional-safety credit is claimed.

## Release boundary

This correction closes a configuration ambiguity only. It closes no requirement, risk, fabrication gate, motion gate, physical test, qualified review or energization gate. HR-V0 remains not build-ready and energization remains prohibited.

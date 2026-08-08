# HR-V0 Pololu gripper direct-adapter candidate P0.1

Status: **PRELIMINARY - PREFERRED EVALUATION PATH ONLY - NOT RELEASED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-GRIP-ADAPT-P0.1`
Date: 2026-08-08

## Decision

R112 adds a source-controlled direct adapter between the current 20-2040 forearm end face and the Pololu item 3551 manufacturer geometry. It does not select item 3551 or supersede `HR-V0-GRIP-P0.2`. The adapter is a one-piece machined 6061-T651 clevis candidate that retains the two current beam-face M5 axes and removes the earlier H104 carrier from this comparison path.

## Exact nominal interfaces

- Beam face: two through holes `diameter 5.50 mm` with `diameter 11.30 mm x 90 degree` rear countersinks at `X=0, Z=+/-10.00 mm`.
- Gripper axes: two transverse `diameter 4.40 mm` holes at Project Button coordinates `Y/Z = 10.49/+4.00 mm` and `19.69/-4.00 mm`.
- The gripper axes come from the Pololu drawing dated 31 August 2018 and the controlled manufacturer STEP. In the native STEP they are separated by `9.20 mm` and `8.00 mm`, or `12.191801 mm` true distance.
- Cheeks: `3.00 mm` nominal thickness and `20.40 mm` nominal inside gap around the `19.80 mm` manufacturer ear envelope.
- Nominal transform of the manufacturer STEP: `TX=2.980409242639 mm`, `TY=3.719474107557 mm`, `TZ=17.512087117409 mm`. This yields a `0.500 mm` rear gap and a minimum nominal adapter-to-gripper solid separation of `0.300 mm`.

These are candidate coordinates, not received measurements or released manufacturing tolerances.

## Mass and static screens

The generated adapter solid has `9,366.558784 mm3` nominal volume. At the controlled `2.70 g/cm3` density screen, the calculated adapter mass is `25.289709 g`. Combining the current incomplete moving subtotal, 30 g catalog gripper mass and this adapter gives:

`750 - 577.091 - 30 - 25.289709 = 117.619291 g`

The result is arithmetic headroom only. It omits the guard, pads, exact fasteners, moving cable, adhesive and received tolerances/mass.

An intentionally conservative gravity screen places the 100 g payload and catalog gripper at the far tip and the adapter mass at its farthest extent. It gives `0.085890 N m` at 1x and `0.858897 N m` at 10x. The narrow two-web idealization gives about `13.420 MPa` at 10x, and the two gripper axes carry a `70.449 N` ideal couple over `12.191801 mm`. These values are sensitivity screens, not released load cases, design allowables, fatigue evidence or proof credit.

## Blocking evidence

All twelve `PAH-*` holds remain open. The blocking items are the task/`GRIP-002` selection decision; exact material/finish and allowables; tolerance/GD&T; M5 and M4 fastener stacks; Pololu POM ear grade/strength; accepted static/dynamic load case and proof multiplier; guard/cable/pinch closure; qualified DFM/FAI; received fit/mass/free-motion evidence; physical proof; and qualified mechanical review with separate work authorization.

## Controlled sources

- [Pololu item 3551 resources](https://www.pololu.com/product/3551/resources), drawing dated 31 August 2018 and current STEP payload, accessed 2026-08-08.
- [Kaiser 6061 sheet/coil/plate record](https://www.kaiseraluminum.com/), controlled project copy with Sheet Rev 05 / Plate Rev 06. Density and typical values are screening inputs, not released allowables.

Generated STEP, STL, GLB, SVG and registers are in `cad/hr-v0/generated/pololu-gripper-adapter-p0.1/`. The interactive guide is `release/hr-v0/gripper-adapter-p0.1/index.html`.

No external quotation, machining, purchase, assembly, connection, motion or energization is authorized.

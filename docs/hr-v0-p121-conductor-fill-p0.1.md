# HR-V0 P1.21 conductor and duct-occupancy evidence P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Identifier: `HR-V0-P121-CONDUCTOR-FILL-P0.1`

Date: 2026-08-11

Round: R242

Configuration: Project Button Electrical `V3-P1.21-SRA1-SUPPLY-WATCHDOG-CANDIDATE`, unaccepted; P1.15 remains current

## Outcome

The seven R241 logical conductors now have an exact, orderable physical-construction candidate: Belden `3057 BL005`, blue 16 AWG / approximately 1.31 mm2, 26x30 tinned copper, PVC, 2.3 mm nominal outside diameter, supplied on a 100 ft / 30.48 m reel.

This is a **held candidate**, not a procurement or wiring release. Blue is not declared an accepted code color. The current panel also uses a red `XD24` distribution block and a blue `XD0` distribution block; that component-color convention conflicts with treating blue conductor insulation as self-explanatory positive 24 VDC identification. A qualified Boston/US electrical reviewer must disposition conductor, block and marker colors before any purchase.

## Reproduced geometry screens

- Seven 2.3 mm nominal-OD candidates have a combined circular envelope of 29.08 mm2 in WD5.
- Phoenix Contact publishes 327 mm2 usable cross-section for item 3240187, so the nominal circular-envelope ratio is 8.89 percent.
- Five of the seven conductors traverse WD2. Their circular envelope is 20.77 mm2.
- Over the documented compute-harness segment, six 1.6 mm candidates overlap those five conductors. The largest currently enumerated WD2 cross-section is therefore 32.84 mm2, or 2.66 percent of the 1235 mm2 published usable cross-section for item 3240189.
- The field and compute bundles do not overlap longitudinally in the controlled route model; the screen does not incorrectly sum both at one cross-section.

These are **geometry inputs only**. Total fill is not accepted because the package lacks a complete WD2 occupant register, packing/label/tie/bend/cover effects, terminal drops, junction geometry, ambient, duty, conductor heating and a qualified application rule.

## Length and voltage-drop boundary

The seven R240 route centerlines sum to 6.72325 m / 22.06 ft. The catalog reel is 4.53 times that geometry-only sum, but no cut length is released: terminal entry, 23 mm stationary bend arcs, service loops, stripping, labels, tolerance, waste and received geometry remain unresolved.

The controlled Belden live record does not publish DCR. Numeric voltage drop and conductor loss therefore remain **NOT CALCULATED**. The package records the equations and requires a received-lot four-wire resistance measurement at a recorded temperature, actual cut lengths, worst-case load currents and contact/supply tolerances before acceptance.

## Terminal screen

The 1.31 mm2 candidate is within the published flexible-conductor ranges for:

- Phoenix Contact `3273114` XD24 load contacts;
- Pilz `750104` SR1/SRA1 screw terminals; and
- Phoenix Contact `2967060` KWD1/KWD2 screw terminals.

Gauge fit does not select a ferrule or direct-wire method. Exact ferrule, tool/die, strip length application, torque witness, pull criterion and received-terminal verification remain open.

## Controlled package

Interactive guide: `release/hr-v0/p121-conductor-fill-p0.1/index.html`

Machine-readable registers include the exact candidate, seven-wire schedule, terminal compatibility, route-length, segment-specific duct occupancy, voltage-drop equations, thermal blockers, color conflict, twelve open holds and ten blank inspection rows.

Generate with `tools/generate_hr_v0_p121_conductor_fill_p01.py` and validate with `tools/check_hr_v0_p121_conductor_fill_p01.py`.

No result in this package grants functional-safety credit or authorizes procurement, cutting, fabrication, assembly, wiring, connection, powered testing, motion or energization.

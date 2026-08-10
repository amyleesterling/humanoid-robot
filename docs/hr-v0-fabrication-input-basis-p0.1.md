# HR-V0 fabrication input basis P0.1

> **PRELIMINARY - NOT APPROVED FOR QUOTATION, FABRICATION, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-FAB-INPUT-P0.1`

Review round: R173

## Correction

`HR-V0-BOSTON-FAB-ROUTE-P0.3` correctly refused to treat "not strong" as a numerical requirement, but its open-input register then described payload and motion as though no numerical requirements existed. That is inaccurate.

The controlled draft requirements already establish:

- one soft-foam handoff object, no more than 100 g including measurement uncertainty and 40-70 mm on each principal dimension;
- automatic TCP speed no greater than 0.15 m/s in every released pose;
- automatic joint commands no greater than 30 deg/s, with pose-dependent limits required because this cap is not sufficient by itself; and
- hold-to-run setup motion no greater than 10 deg/s.

R173 binds those values into the fabrication-input chain. It does not promote the draft requirements or pretend that payload identity, acceleration, jerk, duty, stopping, restraint, safety factors, load paths, material, inspection or physical results exist.

## Independent arithmetic

At the 360 mm maximum reach, shoulder-only motion at 30 deg/s produces a kinematic TCP screen of 0.1884955592 m/s, above the 0.15 m/s requirement. The shoulder-only rate corresponding to 0.15 m/s at that reach is 23.87324146 deg/s. Combined-axis motion can require a lower allocation. These are reference screens, not released controller limits.

The 100 g payload at 0.15 m/s carries 0.001125 J translational kinetic energy. A 100 g payload dropped through the candidate 0.950 m enclosure height carries 0.93163175 J gravitational energy. Neither number rates the arm, hard stop, guard or detached-part case.

## Remaining release inputs

`FAB-IN-002` through `FAB-IN-010` retain the unresolved duty spectrum, acceleration/jerk/emergency profile, restraint/fall cases, safety factors, C05 capacity, C06/C07 stop application, material traceability, provider inspection acceptance and separate work authorization. `EG-006` and `EG-007` remain partial.

No provider may be contacted and no geometry may be uploaded under this package. No quotation, purchase, first article, fabrication, assembly, motion or energization authority exists.

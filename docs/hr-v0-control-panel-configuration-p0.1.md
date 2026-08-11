# HR-V0 current control-panel configuration P0.1

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Identifier: `HR-V0-CP-CONFIG-P0.1`

Round: R220

Date: 2026-08-11

## Configuration correction

`HR-V0-CP-P0.6` remains useful as the current enclosure and backplate planning geometry, but its embedded board labels were created against Electrical V3-P1.14, `PCB-P0.7` and `DXL-STAR-P0.1`. Those are not the current build-facing electrical identities.

This overlay binds the unchanged panel geometry to:

- `Project Button Electrical V3-P1.15-CARRIER-CANDIDATE` as the authoritative core schematic and wire schedule;
- `PCB-P1.0-P1.15-DIRECT` as the current watchdog-board identity;
- `DXL-STAR-P0.2-CARRIER-CANDIDATE` as the current star-board identity; and
- `V3-P1.17-OBSERVATION-P0.5-CANDIDATE` only as a supporting observation/integration view.

The overlay does not rewrite P0.6 history. Any installation or review that uses P0.6 coordinates must also cite this overlay. P0.6 alone is prohibited as the current electrical installation configuration.

## Evidence

All 66 P0.6 panel wire endpoints match the current P1.15 schedule exactly across wire number, sheet, reference, terminal, pin name and net. The current stationary-wire schedule carries those P1.15 identities while preserving the existing fail-closed physical fields: conductor, gauge, color, length and both terminations remain `SELECTION REQUIRED`.

The two board planning envelopes are retained:

- WDPCB1: 160 x 100 mm at BP-012, now identified as PCB-P1.0;
- INJ1: 100 x 60 mm at BP-013, now identified as DXL-STAR-P0.2.

This is identity and envelope parity, not received-fit or mounting-hole evidence.

## Remaining build blockers

Twelve controlled holds remain open: both board supplier releases; received enclosure/backplate and device geometry; production hole schedule; rail/duct release; conductors and terminations; protection coordination; grounding/bonding; thermal/separation evidence; unpowered inspection; and qualified release.

No supplier packet, machine XYRS, hole, cut, wire, protection selection or physical result is released. The current watchdog and DXL-star CAM files remain internal review evidence only.

## Authority

Internal configuration review is permitted. Supplier upload or quotation, ordering, cutting, drilling, wiring, assembly, connection, powered testing, motion and energization remain prohibited until separately authorized by the applicable gates.

The [interactive configuration guide](../release/hr-v0/control-panel-configuration-p0.1/index.html) presents the corrected identities and remaining holds.

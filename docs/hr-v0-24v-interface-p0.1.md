# HR-V0 24 V source interface P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Identifier: `HR-V0-24V-IF-P0.1`

Date: 2026-08-08

Electrical dependency: Project Button Electrical `V3-P1.10`

## Outcome

R80 replaces the ambiguous system-level `JC1` block with two explicit functions:

1. `J24` is the held source-to-panel interface candidate.
2. `F24` is the separate, still-unselected 24 V branch-protection function.

This also removes the system-level reference collision with `JC1` on the separate `DXL-STAR-P0.1` board.

The exact candidate chain is:

`PSU2 Mean Well GST40A24-P1J -> Mean Well DC PLUG-P1J-R7B -> Kycon KPJX-PM-4S -> F24 SELECTION REQUIRED -> SAFETY_24V`

This is an exact catalog/topology candidate, not a released connection. No order, panel hole, PCB, harness, wire, fuse, strain relief, connection, or powered test is authorized.

## Pin allocation candidate

Mean Well's current online industrial catalog identifies R7B pins 1 and 4 as `+Vo`, and pins 2 and 3 as `-Vo`. Electrical V3-P1.10 therefore models:

| Reference | Pin | Candidate net |
|---|---:|---|
| `J24` | 1 | `SAFETY_24V_RAW` |
| `J24` | 2 | `SAFETY_0V` |
| `J24` | 3 | `SAFETY_0V` |
| `J24` | 4 | `SAFETY_24V_RAW` |
| `F24` | `IN` | `SAFETY_24V_RAW` |
| `F24` | `OUT` | `SAFETY_24V` |

The duplicate positive and return contacts receive no assumed current-sharing, redundancy, or functional-safety credit. Plug-view and jack-view orientation must be reconciled against the received parts with power removed, then polarity must be confirmed through an approved live-dead-live method before any later connection authorization.

## What the current primary evidence supports

- Mean Well `GST40A-SPEC`, dated 2026-04-03, supports the `GST40A24-P1J` 24 V / 1.67 A source record and P1J center-positive geometry.
- Mean Well's current accessory page lists `DC PLUG-P1J-R7B`.
- Mean Well's current industrial-catalog page identifies the R7B four-pin allocation.
- Kycon's `KPJX-PM` catalog indexed `0126` identifies `KPJX-PM-4S` as the non-shielded panel-mount four-position snap-and-lock jack family.
- Kycon drawing `KPJX-PM-4S`, Rev C2 dated 2026-01-08, supplies the pin view and mechanical dimensions.

Kycon's published maximum of 7.5 A per pin at 48 VDC is a manufacturer product limit, not a Project Button current rating, proof of equal current sharing, a protection selection, or evidence that the complete Mean Well adapter chain is suitable.

## Blocking evidence

The current official Mean Well material found during R80 does not explicitly state that `DC PLUG-P1J-R7B` is approved for `GST40A24-P1J`, nor does it close the adapter cable's current/application envelope. The interface therefore remains in the unresolved-selection register under `COMPATIBILITY AND PHYSICAL VERIFICATION REQUIRED`.

Closure requires all of the following:

- written Mean Well compatibility evidence for the exact source and conversion accessory;
- manufacturer evidence for the adapter current/application envelope and intended use of the paired R7B contacts;
- received identity, keyed orientation, continuity and polarity records;
- selected `F24` hardware/value based on source fault current, inrush, time-current curves and downstream conductor/connector coordination;
- released wire/PCB/harness, terminal, insulation, support and termination design;
- received Kycon geometry, panel/PCB mounting, touch protection, retention, strain relief, cable bend and pullout evidence;
- temperature rise, voltage drop and abnormal-condition results at the accepted worst case;
- qualified electrical review and stage-specific work authorization.

## Controlled files

The machine-readable package is `electrical/interfaces/hr-v0-24v-interface-p0.1/`:

- `interface-bom.csv`
- `pin-allocation.csv`
- `compatibility-holds.csv`
- `source-register.csv`
- `interface-summary.json`
- `HR-V0_24v-interface-guide.html`

Generate with `python tools/generate_hr_v0_24v_interface.py` and check with `python tools/check_hr_v0_24v_interface.py`.

No result in this document approves procurement, fabrication, wiring, connection, energization, motion, human exposure, or child-adjacent use.

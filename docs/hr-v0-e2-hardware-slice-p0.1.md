# HR-V0 E2 control-only hardware slice P0.1

**PRELIMINARY - CONFIGURATION CANDIDATE ONLY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-08

Identifier: `HR-V0-E2-HW-P0.1`

Electrical input: `Project Button Electrical V3-P1.9`

Sequence input: `HR-V0-E2-SEQ-P0.1`

## Result

R79 converts the E2 prose boundary into a machine-checkable hardware slice. It records 22 installed-candidate, physically-absent/disconnected, or DNP states; six exact XT1 position-to-net candidates; three source-domain states; and twelve blocking holds.

This is configuration control, not a build release. The two eventually permitted E2 domains are the accepted 24 V safety/control source and 5.1 V compute source. The 12 V actuator source, its AC and DC connections, branch protection, U2D2 power path and every actuator plug must be physically absent or disconnected, covered, labeled and proven dead. K1 and K2 may be installed only for coil and auxiliary/mirror-contact testing; their load poles remain unsourced and unwired.

## XT1 correction

The panel BOM already carried the exact Phoenix family, while Electrical V3-P1.8 still represented XT1 as a generic selection with `TBD-1` through `TBD-6`. Electrical V3-P1.9 reconciles that configuration defect:

| Position | Net | Catalog candidate |
|---|---|---|
| XT1-01 | `SAFETY_24V` | Phoenix PT 2,5 gray item `3209510` |
| XT1-02 | `SAFETY_0V` | Phoenix PT 2,5 BU blue item `3209523` |
| XT1-03 | `SR1_STATUS` | Phoenix PT 2,5 gray item `3209510` |
| XT1-04 | `SRA1_STATUS` | Phoenix PT 2,5 gray item `3209510` |
| XT1-05 | `K1_STATUS` | Phoenix PT 2,5 gray item `3209510` |
| XT1-06 | `K2_STATUS` | Phoenix PT 2,5 gray item `3209510` |

The candidate group also records D-ST 2,5 end cover `3030417`, two CLIPFIX 35 end brackets `3022218`, and UCT-TM 5 marker sheet `0828734`. Official Phoenix Contact product records were rechecked 2026-08-08. They establish catalog capabilities, not project conductor or protection ratings:

- https://www.phoenixcontact.com/en-us/products/feed-through-terminal-block-pt-25-3209510
- https://www.phoenixcontact.com/en-us/products/feed-through-terminal-block-pt-25-bu-3209523
- https://www.phoenixcontact.com/en-us/products/end-cover-d-st-25-3030417
- https://www.phoenixcontact.com/en-us/products/end-block-clipfix-35-3022218
- https://www.phoenixcontact.com/en-us/products/terminal-marking-uct-tm-5-0828734

The V3 unresolved register therefore remains at 63 rows: XT1's hardware and position allocation are exact candidates, but conductor order codes, ferrule/direct-wire method, protection, current/temperature coordination, received compatibility, strip length, installed retention, marking and point-to-point proof are still unresolved. The six replaced XT1 placeholders reduce the deliberate `TBD-*` terminal count from 24 to 18.

## Controlled artifacts

- `electrical/e2/hr-v0-e2-hardware-p0.1/e2-configuration-slice.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.1/e2-terminal-register.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.1/e2-source-register.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.1/e2-blocking-holds.csv`
- `electrical/e2/hr-v0-e2-hardware-p0.1/e2-hardware-summary.json`
- `electrical/e2/hr-v0-e2-hardware-p0.1/HR-V0_e2-hardware-guide.html`
- `tools/generate_hr_v0_e2_hardware_slice.py`
- `tools/check_hr_v0_e2_hardware_slice.py`

The HTML guide is a responsive review surface with a 16 px body-text floor. CSV and JSON remain the controlled comparison inputs.

## Open release boundary

All twelve hardware holds remain open: site, receiving, RESET/ARM/H1 mapping, JC1, FSR1/FSR2 fuse links, conductors/terminations, enclosure fabrication, watchdog PCB manufacture, firmware/HIL, test equipment/limits, four-role authorization and physical proof that the actuator domain is absent.

Nothing in this package approves procurement, quotation, drilling, cutting, PCB fabrication, assembly, wiring, connection, energization, motion, human exposure or child-adjacent operation.

**CURRENT VERDICT: NOT BUILT; NOT EXECUTED; NOT AUTHORIZED FOR ENERGIZATION.**

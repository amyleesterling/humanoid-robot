# HR-V0 protection and conductor coordination P0.4

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

Applies to: Electrical V3-P1.9, references `F0`, `F1`, `F2`, `F3`, `FSR1`, and `FSR2`; exact `SD1` candidate is a path constraint, not a fuse selection

Status: input and evidence-control package only; physical values and execution evidence remain open

## Decision

No fuse ampere rating is released. R64 retains the exact non-LED DIN holder candidates for `FSR1` and `FSR2`, Phoenix Contact `D-ST 4` item `3030420` as the end-cover candidate, and synchronizes the accessory boundary with `HR-V0-CP-P0.4` and Electrical `V3-P1.9`. Littelfuse `75920-01` is now the exact `SD1` catalog candidate on hold, but this document does not select a fuse link, conductor, splice, cable length, lug/terminal stack, source-load stud assignment, load-break duty, physical cutout, or released enclosure layout.

The machine-readable input register is `electrical/hr-v0-protection-coordination-inputs.csv`. Every value that depends on the received source, harness geometry, installation, measured load, or qualified application review remains `SELECTION REQUIRED`. The execution record is `tests/forms/hr-v0-protection-coordination-template.csv`.

## Controlled architecture

The candidate 12 V path remains:

`GST280A12-C6P -> JA1 -> F0 -> SD1 -> K1 three poles in series -> K2 three poles in series -> F1/F2/F3 -> separate VDD injection -> J1/J2/J3`

- `SD1`: exact catalog candidate Littelfuse `75920-01`, SPST in the positive path. Its identity does not close F0 coordination. The current 75920 Series datasheet's published current-cycle ratings depend on 4/0 cable, which is not a Project Button conductor selection. Source fault/current-limit behavior, conductor/lug system, temperature rise, fault/load-break duty and qualified application review remain open under `HR-V0-SD-P0.2`.

- `F0`: proposed Littelfuse `FHAC0002SXJ` 32 V heavy-duty inline ATO holder, with 12 AWG GXL pigtails and a 30 A holder maximum. The holder maximum is not a fuse selection and is not permission to operate at 30 A. The exact 12-to-16 AWG transition, splice/terminal system, strain relief, enclosure location, and thermal result remain open.
- `F1` through `F3`: proposed Blue Sea Systems `5025` six-circuit ST Blade block with negative bus and cover. It accepts ATO/ATC fuses and publishes 32 VDC, 30 A per circuit, and 100 A per block limits. Those are product limits, not released branch ratings. Exact ring terminals, conductor sizes, unused-position treatment, mounting, cover access, and enclosure integration remain open.
- `F0` through `F3`: proposed Littelfuse `ATOF` 32 V fuse family. The current datasheet identifies a 1000 A interrupting rating at 32 VDC and time-current/temperature data, but the ampere-specific order code remains `SELECTION REQUIRED`.
- `FSR1` and `FSR2`: proposed Phoenix Contact `PT 4-HESI (5X20)` item `3211861`, two non-LED DIN fuse-terminal holders, plus one proposed `D-ST 4` item `3030420` end cover. Phoenix publishes 5 x 20 mm fuse accommodation, a 6.3 A holder maximum, 500 V nominal voltage, 6.2 mm holder width, and a 2.2 x 55.9 x 29 mm end-cover envelope. These are component limits only. Fuse manufacturer/family, ampere rating, speed, voltage and interrupting rating, conductors, ferrules, received compatibility, grouping loss, and application remain `SELECTION REQUIRED`. The Schneider `LC1D25BD` coil's published 5.4 W value gives a nominal arithmetic screen of 0.225 A at 24 V; it does not establish pickup, transient, fault, or protective-device behavior.

The ROBOTIS U2D2 Power Hub remains excluded from actuator VDD. Its current official page publishes a 10.0 A maximum, below the 11.1 A sum of the three actuator stall endpoints. No operational actuator current may be routed through it.

## Connector constraint that must be resolved

ROBOTIS publishes the XM540-W270-T stall endpoint as **4.4 A at 12 V** and identifies the TTL actuator connector as the JST EH family. JST's current EH-series page publishes **3 A AC/DC at AWG 22**. ROBOTIS also states 21 AWG for DYNAMIXEL wire.

These facts do not prove that a received actuator/cable may carry 4.4 A continuously or that a 3 A series rating can be exceeded. Stall is not a continuous operating point, but fuse coordination must protect the connector and harness during overload and fault conditions. Therefore:

1. The two XM540 branches stay blocked by an explicit connector-limit conflict.
2. No conductor or fuse selection may be based only on the 4.4 A stall number or only on the 3 A JST series number.
3. Closure requires written ROBOTIS/JST application evidence or a qualified disposition, received-harness identification, the intended current-limit/duty profile, thermal measurements at connector and conductor, and fault-clearing evidence.
4. Standard full-pin X3P cables may not join separately protected branches because pin 2 carries VDD. The released injection harness must omit VDD on every data-only link and pass continuity/no-backfeed testing.

The XM430-W350-T branch has a published 2.3 A stall endpoint at 12 V, below the 3 A JST series basis, but still requires the same installed-harness, ambient, bundling, temperature, voltage-drop, inrush, regeneration, and clearing evidence.

## Required calculations and measurements

For each of the six references, the controlled record shall identify:

- exact source and source serial number;
- prospective DC fault current or the source's measured current-limit/foldback behavior at the installation point;
- exact fuse and holder order codes, voltage and interrupting ratings, and temperature derating;
- cable one-way length, conductor order code/gauge/insulation, ambient temperature, bundle count, installation method, and terminal/connector limits;
- steady, peak and inrush current, peak duration, duty cycle, simultaneous-load case, and regeneration/bus-rise behavior;
- allowable voltage drop and measured/calculated drop;
- maximum conductor, connector, holder, and enclosure temperatures;
- ampere-specific time-current curve, tolerance, clearing time, and post-test damage/insulation result;
- applicable Boston/Massachusetts installation basis and signed qualified electrical disposition.

`ANALYSIS-ELEC-001` shall compare the measured operating envelope, source limitation, conductor/connector limits, holder limits, and Littelfuse curve/derating data. `INSPECT-ELEC-008` shall verify received identities, terminals, construction, mounting, polarity, torque, and conductor retention. `TEST-ELEC-006` shall execute only in a guarded, current-limited fixture under a qualified electrical test plan: characterize the source with a programmable electronic load and validate clearing in a separate controlled fault fixture. A direct uncontrolled short across the robot source is prohibited.

Acceptance requires all fields in `tests/forms/hr-v0-protection-coordination-template.csv`, calibrated-instrument evidence, raw traces and thermal images, no connector/conductor/holder limit violation, fuse clearing before damage under every released fault case, no nuisance opening in the released operating envelope, and signed electrical and safety dispositions. The assembled robot is not the first fault-test fixture.

## Primary-source register

All live pages without a displayed revision are access-dated 2026-08-06.

| Source | Revision/date recorded | Used for | Not established |
|---|---|---|---|
| [ROBOTIS XM540-W270 e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/) | live page; no revision displayed; accessed 2026-08-06 | 12 V, 4.4 A stall endpoint; TTL pinout; JST EH connector family; 21 AWG wire statement | continuous current, branch fuse, installed cable rating |
| [ROBOTIS XM430-W350 e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xm430-w350/) | live page; no revision displayed; accessed 2026-08-06 | 12 V, 2.3 A stall endpoint; TTL connector basis | continuous current or released protection |
| [JST EH series](https://www.jst-mfg.com/product/index.php?lang=2&series=58) | live page; no revision displayed; accessed 2026-08-06 | 2.5 mm pitch; 3 A AC/DC at AWG 22 | permission to exceed 3 A or exact received cable construction |
| [Littelfuse 287 ATOF datasheet](https://www.littelfuse.com/assetdocs/littelfuse-datasheet-287-atof?assetguid=43dcdce8-8ca2-426f-8998-7e566f048d40) | Rev. 02/04/2025; accessed 2026-08-06 | 32 V family, 1000 A at 32 VDC interrupting screen, time-current and temperature data | ampere rating selection or application release |
| [Littelfuse FHAC holder datasheet](https://www.littelfuse.com/assetdocs/littelfuse-fuse-holder-ato-fhac-datasheet.pdf?assetguid=272e0b1a-a576-4173-8740-c1eb469efd79) | `062923-B`, copyright 2023; accessed 2026-08-06 | exact `FHAC0002SXJ`, 32 V, 30 A holder maximum, 12 AWG GXL leads | fuse rating, splice system, installed thermal result |
| [Blue Sea Systems 5025](https://www.bluesea.com/products/5025) | live page; no revision displayed; accessed 2026-08-06 | six ATO/ATC circuits, negative bus/cover, 32 VDC, 30 A/circuit, 100 A/block, published terminal torques | branch fuse, terminals, conductors, enclosure release |
| [ROBOTIS U2D2 Power Hub](https://www.robotis.us/u2d2-power-hub-board-set/) | live page; no revision displayed; accessed 2026-08-06 | 10.0 A maximum exclusion screen | actuator distribution suitability |
| Schneider `LC1D25BD` product sheet | current controlled project source rechecked 2026-08-06 | 24 VDC, 5.4 W coil screen | coil transient or FSR1/FSR2 selection |
| [Phoenix Contact PT 4-HESI (5X20), item 3211861](https://www.phoenixcontact.com/en-us/products/fuse-terminal-block-pt-4-hesi-5x20-3211861) | official US product page; generated product PDF dated 2026-07-06; rechecked 2026-08-07 | exact non-LED holder identity, 5 x 20 mm format, product limits, connection range and physical dimensions | fuse link, conductor/ferrule selection, installed grouping/thermal result or application release |
| [Phoenix Contact D-ST 4, item 3030420](https://www.phoenixcontact.com/en-us/products/end-cover-d-st-4-3030420) | official US product page; rechecked 2026-08-07 | exact end-cover identity and 2.2 x 55.9 x 29 mm catalog envelope | received compatibility/orientation, installed group width, touch inspection, grouping/thermal result or application release |
| [Littelfuse 75920-01](https://www.littelfuse.com/products/switches-connectors/dc-disconnect-switches/manual-battery-disconnect-switches/75920/75920-01) | active product page; 75920 Series datasheet Rev 091825; 2D print and IF-165 Rev 010320-C; rechecked 2026-08-07 | exact SPST high-side-capable catalog candidate, 3/8-24 studs, mounting pattern, OFF-position padlock provision | conductor/lug selection, source/load designation, fault/load-break duty, cutout, touch protection, lockout procedure, installation acceptance |

## Release state

R64 keeps energization gate `EG-014` **partial**. The six-reference input register freezes exact holder identities for all six references: `FHAC0002SXJ` for F0, `5025` for F1-F3, and two `3211861` terminals plus one `3030420` end cover for FSR1/FSR2. It also records exact `SD1` catalog identity without changing any protection value. It does not close the gate. All six fuse-link ratings/order codes, received end-cover compatibility/orientation, the two XM540 connector-limit conflicts, physical harness construction, fault current, operating current, thermal data, clearing proof, service-disconnect application, installation review, and qualified approval remain unresolved.

# HR-V0 DYNAMIXEL Star-Injection Board P0.1

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

## Purpose and boundary

`DXL-STAR-P0.1` replaces the three undefined Electrical V3 injection-module placeholders with one controlled, reusable central board. It distributes one common DYNAMIXEL TTL data conductor and one common return while keeping the three protected actuator-positive branches electrically separate. It is ordinary interface hardware and receives no functional-safety credit.

Native source: `electrical/kicad/hr-v0-dxl-star/hr-v0-dxl-star.kicad_pro`
System representation: Electrical `V3-P1.6`, sheet `06_branches_and_injection`, reference `INJ1`

## Frozen project pin allocation

| Interface | Exact proposed board header | Project pin | Net or disposition |
|---|---|---:|---|
| `JC1 CTRL` | JST `B3B-EH-A` | 1 | `ACT_0V_PE_BONDED` / DYNAMIXEL GND |
| `JC1 CTRL` | JST `B3B-EH-A` | 2 | no net, no copper; mating cable cavity must be empty |
| `JC1 CTRL` | JST `B3B-EH-A` | 3 | `DXL_TTL_DATA` |
| `JP1 PWR1` | JST `B2P-VH` | 1 | separately protected `J1_VDD` |
| `JP1 PWR1` | JST `B2P-VH` | 2 | `ACT_0V_PE_BONDED` |
| `JP2 PWR2` | JST `B2P-VH` | 1 | separately protected `J2_VDD` |
| `JP2 PWR2` | JST `B2P-VH` | 2 | `ACT_0V_PE_BONDED` |
| `JP3 PWR3` | JST `B2P-VH` | 1 | separately protected `J3_VDD` |
| `JP3 PWR3` | JST `B2P-VH` | 2 | `ACT_0V_PE_BONDED` |
| `JA1`, `JA2`, `JA3` | JST `B3B-EH-A` | 1 | common DYNAMIXEL GND |
| `JA1`, `JA2`, `JA3` | JST `B3B-EH-A` | 2 | respective `J1_VDD`, `J2_VDD`, `J3_VDD` only |
| `JA1`, `JA2`, `JA3` | JST `B3B-EH-A` | 3 | common `DXL_TTL_DATA` |

The `JC1` pin-2 copper omission is deliberate. It implements ROBOTIS's published U2D2 boundary: the interface does not supply actuator power. A fully populated three-wire cable is prohibited at `JC1`.

## Native PCB candidate

The P0.1 board is 100 mm by 60 mm, two layers, with four board-only M3 clearance holes, seven connector footprints, 17 routed segments, three 2.0 mm front-copper positive paths, a 0.25 mm back-copper TTL-data tree, and one back-copper common-return zone. Native KiCad 10.0.5 ERC and DRC both report zero errors, warnings, violations, unconnected routed pads, and footprint errors. The independent checker proves that the three positive nets are mutually isolated and that `JC1:2` has neither an assigned net nor routed copper.

Those results establish only source consistency and routing connectivity. They do not establish conductor ampacity, connector application suitability, thermal rise, signal margin, fault clearing, assembly quality, or fabrication readiness. No Gerber, drill, placement, or assembly package exists.

## Harness construction still required

- `JC1` must use a keyed two-conductor-in-three-position cable with only pins 1 and 3 populated at both ends. Empty-cavity retention and inspection method remain `SELECTION REQUIRED`.
- Each actuator cable requires all three EH conductors. Exact wire order code, length, insulation, color, contact, crimp tool, strain relief, bend radius, flex life, pull requirement, labeling, and routing remain `SELECTION REQUIRED`.
- Each power input requires a VH cable end and a separately protected source end. Exact conductor, `VHR-2N` housing, applicable contact for the selected wire, crimp tool, source-side terminal, protection, and retention remain `SELECTION REQUIRED`.
- The JST EH series page lists 3 A at AWG 22. The proposed XM540-W270-T publishes a 4.4 A stall-current endpoint at 12 V. This conflict is not closed by wide PCB traces or by selecting a higher-current power-input connector. Written application evidence plus measured current limiting, duty, voltage drop, temperature, and fault-clearing evidence are required.
- Exact star-cable lengths and topology must pass oscilloscope testing at the released DYNAMIXEL baud rate and every released power sequence. Termination or other signal-conditioning changes may be required from that evidence.

## Required physical evidence

1. Receive and identify every board, housing, header, contact, conductor, crimp tool, and source-side terminal against the controlled BOM and manufacturer documents.
2. Inspect mating-face orientation and pin numbers before installing contacts.
3. Prove continuity of every intended path, open circuit at `JC1:2`, mutual isolation of `J1_VDD`, `J2_VDD`, and `J3_VDD`, and absence of shorts to data or return.
4. With current-limited simulated loads before any actuator connection, exercise all source-off/source-on permutations and record no-backfeed voltage/current at every positive branch and `JC1:2`.
5. Perform crimp-height or manufacturer-specified crimp inspection, lot pull testing, retention testing, and strain-relief inspection.
6. Measure voltage drop and stabilized connector, conductor, and PCB temperature through the released duty envelope and branch-fault fixtures.
7. Capture TTL waveforms at `JC1` and every actuator connector for all released cable lengths, baud rates, loads, and source transitions.
8. Obtain independent electrical/layout review and qualified disposition before fabrication or connection to robot hardware.

Use `tests/forms/hr-v0-dxl-star-inspection-template.csv`; do not replace `NOT EXECUTED` rows with passes without retained raw evidence and accountable signatures.

## Primary sources

Sources were rechecked 2026-08-07. The live ROBOTIS and JST pages expose no controlled page revision, so their access date must be retained and rechecked at release.

- ROBOTIS U2D2 e-Manual: U2D2 does not supply power; TTL pin 1 GND, pin 2 VDD, pin 3 DATA; JST `B3B-EH-A`/`EHR-03` interface: https://emanual.robotis.com/docs/en/parts/interface/u2d2/
- ROBOTIS XM540-W270-T e-Manual: connector pinout and 12 V 4.4 A stall-current endpoint, with the manufacturer's real-world/performance caveat: https://emanual.robotis.com/docs/en/dxl/x/xm540-w270/
- JST EH series: 2.5 mm pitch, `B3B-EH-A`, `EHR-3`, `SEH-001T-P0.6`, and 3 A at AWG 22: https://www.jst-mfg.com/product/index.php?lang=2&series=58
- JST VH English catalog: `B2P-VH`, `VHR-2N`, contact/application tables and current dependence on header/contact/wire configuration: https://www.jst-mfg.com/product/pdf/eng/eVH.pdf

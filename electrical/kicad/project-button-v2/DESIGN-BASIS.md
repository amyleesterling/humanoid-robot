# Project Button HR-V0 / HR-30 Electrical V2.1 Design Basis

> **PRELIMINARY - NOT APPROVED FOR ENERGIZATION**

This directory is the V2.1 correction pass. It does not approve or supersede the preserved V1 project. The authoritative requirements remain in `C:\Users\amyle\Documents\New project\humanoid-robot` and were synchronized to accept the PNOZ s4 proposal as a preliminary selection.

## Purpose of V2.1

V2.1 retains the connected design intent and corrects manufacturer-evidence gaps identified in the independent review. It is an input to qualified electrical and functional-safety review, not a construction package.

The V2.1 acceptance checks are:

1. Every sheet parses in KiCad 10.
2. The native netlist contains real symbols, pins, and nets.
3. ERC is run and every remaining violation is retained and dispositioned; no safety-relevant error is hidden to obtain a zero count.
4. Mains, protective earth, safety 24 VDC, HR-V0 12 VDC, HR-30 actuator power, and logic power remain distinct nets.
5. Every reference designator is unique to one physical item.
6. Every selection-dependent device or interface is visibly marked `SELECTION REQUIRED`.
7. No unresolved connector order code, terminal number, pinout, fuse rating, conductor size, or contact rating is inferred.
8. Native PDF and SVG exports are generated from the same KiCad source and carry the preliminary warning.
9. Reset establishes eligibility only. A separate ARM command is required before motion can be requested.
10. The design remains blocked from fabrication and energization until selections, calculations, bench evidence, and qualified reviews are complete.

## V2.1 architectural decisions

### Safety relay proposal

The authoritative specification now proposes the Pilz PNOZ s4 used in V2.1. This synchronization accepts only the preliminary device proposal; it is not application approval:

- Proposed device: Pilz PNOZ s4, 24 VDC, order number 750104.
- Current manufacturer product page: <https://www.pilz.com/en-INT/eshop/product/750104>
- Current operating manual: <https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf>, product listing 2026-06-22, PDF metadata 2026-06-17, document colophon 2026-02, SHA-256 `4B6E4768CEFAEDAF54F006347D32A8A04964B59A16F3616D8AC43698D3626BB4`.
- Proposed configuration: the page-13 lower row, third mode column, “with detection of shorts across contacts / monitored start falling edge.”
- Proposed start/feedback wiring: `S12 -> momentary NO reset -> K1 NC -> K2 NC -> S34`, as shown on manual pages 15-16.
- For 750104, falling-edge wait is 250 ms and minimum start pulse is 100 ms (manual page 26).

Closure evidence required:

- qualified review of the exact PNOZ s4 selector setting, sealing, terminal circuit, and application;
- validation of reset-button edge monitoring, channel discrepancy behavior, EDM behavior, and fault reset;
- protected or separate routing and justified fault exclusion because the relay does not recognize shorts or cross-shorts in the start/feedback loop;
- selected protection ahead of the output contacts and selected coil-suppression networks, with measured dropout and stopping time;
- recorded proof that reset or E-stop release never commands actuator motion.

### Watchdog permit

The watchdog relay is supplemental control equipment, not a safety relay. Its normally-open 11-14 contact provides a permit only while the watchdog circuit is healthy. The contact drops open on watchdog power loss, driver failure, or watchdog timeout. The driver stage between the 3.3 V controller and the 24 V relay coil remains `SELECTION REQUIRED` until its circuit, isolation policy, flyback behavior, and fault response are verified.

### Redundant actuator interruption

Actuator power is interrupted by two independently commanded contactors in series. Each contactor coil is controlled by a separate safety output. Both integral normally-closed mirror contacts are included in the monitored-start / external-device-monitoring loop. The watchdog permit is upstream of selected output-contact protection and does not replace either safety output. Terminals `41-42` and `Y32` are diagnostic only and must not close a safety function.

The exact DC utilization suitability remains a coordination calculation, including capacitive make inrush, breaking duty, minimum switching current of auxiliary contacts, prospective fault current, fuse clearing behavior, coil suppression, and measured dropout time. The maximum output-protection values in the Pilz manual are not device selections.

### Reset and ARM separation

Safety reset can only move the system to `SAFE_READY`. It does not assert `ARM`, torque enable, or a motion target. The control state machine must require a subsequent deliberate ARM command, and all actuator goal registers must be initialized to a documented non-motion state before torque enable. Hardware and software validation evidence is required before this requirement can be closed.

### HR-V0 and HR-30 separation

- HR-V0 uses its own 12 V actuator source and distribution.
- HR-30 uses a distinct protected source interface. A tethered source and a battery/BMS source may be alternatives, but they are never drawn as electrically paralleled.
- HR-30 upper-body 12 V loads require a separately selected converter or separate rail when the chosen actuator source is not a verified 12 V source.
- No HR-V0 terminal block is implied to feed the HR-30 leg bus.

### Precharge topology

The proposed HR-30 precharge path is parallel to the main source contact, not in series with it. The sequence is: source disconnect closed, precharge branch closed, DC-link voltage verified, main contact closed, then precharge branch opened. Component values, timing, voltage thresholds, welded-contact detection, discharge path, and fault behavior remain `SELECTION REQUIRED` pending load-capacitance and source data.

### Protective earth and DC 0 V

Protective earth is continuous to the enclosure, required DIN rail points, power-supply protective-earth terminals, robot base bond, and bench earth point. A DC 0 V-to-PE bond is allowed only at one documented, removable star point after EMC and fault-current review. No other shield drain or mounting path may create an unintended parallel bond.

### Communications

- The U2D2 Power Hub is not an actuator-current combiner. ROBOTIS documents 3.5-24.0 V and 10.0 A maximum and permits only one power input.
- Each independent TTL bus has its own physical U2D2 interface.
- ROBOTIS names U2D2 pin 2 `VDD`, not `VDD_SENSE`, and does not publish its internal current path. V2.1 therefore omits pin 2 from the proposed released custom data cable pending written evidence.
- Standard fully populated 3-pin TTL and 4-pin RS-485 DYNAMIXEL cables carry VDD. They are prohibited between individually protected power branches unless a released power-isolating breakout/harness and continuity/no-backfeed tests prove isolation.
- RS-485 termination is located only at the two physical bus ends; biasing is selected according to the verified transceiver implementation.
- Data pairs, shield drains, and power injection are documented separately. Routing and separation from actuator-current conductors remain harness-design inputs.

## Deliberately unresolved selections

The V2 schematics must not convert any item below into an orderable or buildable selection without primary-source evidence and recorded engineering inputs:

- AC inlet, branch protection, disconnect, enclosure, gland, and regional mains configuration;
- E-stop operator/contact blocks and reset operator/contact block;
- 24 V-to-3.3 V watchdog driver / isolation stage;
- safety contactor coordination for actual DC load, capacitance, and fault current;
- PNOZ output-contact protection and all DC contactor-coil suppression networks;
- all fuses and holders;
- all wire sizes, insulation systems, colors, ferrules, terminals, connectors, and pin maps;
- HR-30 battery chemistry, series/parallel configuration, pack voltage window, BMS, charger, service disconnect, source contactors, precharge relay, resistor, discharge path, and telemetry;
- HR-30 tether source and tether/battery source selection mechanism;
- HR-30 upper-body regulated rail;
- RS-485 transceiver, termination, bias, shielding, and a VDD-isolating harness topology;
- U2D2 pin-2 treatment and released TTL/RS-485 data-only cable drawings with continuity/no-backfeed results;
- actuator branch grouping and every connector-current derating calculation;
- jurisdiction, ambient range, bundling, allowable temperature rise, cable lengths, duty cycles, inrush, and prospective fault current.

## Review status

This design basis incorporates the preliminary-review findings but does not close them by assertion. A finding is closed only when the connected source, native export, calculation, primary-source record, received hardware, and test evidence agree.

**Status: PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

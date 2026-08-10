# HR-V0 event-tap disposition P0.1

> **PRELIMINARY — NOT APPROVED FOR PROCUREMENT, FABRICATION, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION.**

Document ID: **HR-V0-EVENT-TAP-DISP-P0.1**

Round: **R178**

Date: **2026-08-10**

Parent candidate: **HR-V0-DYN-EVENT-AIN-P0.1**

Electrical configuration: **Project Button Electrical V3-P1.15-CARRIER-CANDIDATE**

## Decision

No R177 field adapter is released. The seven TI `AMC3330EVM` boards remain output-side evaluation candidates only. Published manufacturer data is sufficient to classify the seven proposed nodes, but it does not define a permissible permanent parallel observer load or a complete transient/fault envelope for the installed Project Button circuits.

Five nodes are within Pilz input, monitored-start or external-device-monitoring paths. A permanent passive tap on those nodes is **not released**. Two nodes are across Schneider 24 VDC contactor coils. Their divider designs remain **held** until the installed transient envelope and application limits are measured and accepted. Direct connection from any 24 V-class node to an AMC3330EVM input remains prohibited.

This is a fail-closed engineering disposition, not a finding that observation is impossible. A temporary or permanent method may proceed only after the ten closure holds in `electrical/analysis/hr-v0-event-tap-disposition-p0.1/selection-holds.csv` are satisfied and separately authorized.

## Exact node disposition

| Net | Exact P1.15 terminals | Circuit type | R178 disposition |
|---|---|---|---|
| `SR1_S12` | `SR1:S12`; `S0:R-2`; `S1:TBD-R1` | Pilz input/start feed | Permanent passive tap not released |
| `SR1_START_RETURN` | `SR1:S34`; `S1:TBD-R2` | Pilz falling-edge monitored RESET return | Permanent passive tap not released |
| `ARM_AFTER_S2` | `S2:TBD-A2`; `K1:21` | Pilz monitored ARM/EDM chain | Permanent passive tap not released |
| `K1_A1` | `FSR1:2`; `K1:A1`; return `K1:A2/SAFETY_0V` | Schneider 24 VDC coil | Divider design held |
| `K2_A1` | `FSR2:2`; `K2:A1`; return `K2:A2/SAFETY_0V` | Schneider 24 VDC coil | Divider design held |
| `EDM_K1_OUT` | `K1:22`; `K2:21` | Pilz EDM chain between mirror contacts | Permanent passive tap not released |
| `SRA1_START_RETURN` | `K2:22`; `SRA1:S34` | Pilz monitored ARM/EDM return | Permanent passive tap not released |

The exact source rows are controlled in `electrical/kicad/project-button-v3/wire-number-table.csv`. R178 does not modify V3-P1.15.

## Manufacturer evidence

### Pilz PNOZ s4 750104

Pilz operating manual `21396-EN-23` publishes 24 VDC and 50 mA for the input, start and feedback circuits. It publishes a 0.2 A / 100 ms input-circuit current pulse and 0.2 A / 15 ms start/feedback pulses. The manual also states:

- a falling-edge monitored start requires the start circuit to close and open again;
- the device does not recognize short circuits or shorts across contacts in the start/feedback loop, so protected or separate installation is required;
- control-circuit cables should be routed separately from energy-transmission cables or shielded; and
- the safety functions require qualified checking after initial commissioning and changes.

Those data do **not** specify an allowed parallel measurement current, capacitance, leakage, ground-reference connection, added wiring topology or diagnostic-pulse distortion limit. The published 50 mA is an input-circuit figure, not permission to add a percentage of extra load. R178 therefore does not invent an acceptance percentage.

Controlled source: Pilz, *PNOZ s4 operating manual*, edition `21396-EN-23`, PDF metadata 2026-06-17, Pilz portal file date 2026-06-22, acquired 2026-08-08, SHA-256 `4B6E4768CEFAEDAF54F006347D32A8A04964B59A16F3616D8AC43698D3626BB4`.

### Schneider LC1D25BD

Schneider's exact product sheet identifies the 24 VDC coil, 5.4 W inrush/hold power at 20 °C, 28 ms time constant, 16–24 ms opening time, 0.7–1.25 `Uc` operational range, 0.1–0.25 `Uc` dropout range, and a built-in bidirectional peak-limiting diode suppressor. The last fact corrects the weaker prior statement that coil suppression itself was wholly unidentified.

The same product sheet does not publish the built-in suppressor clamp-voltage envelope or a maximum permitted external parallel observer current/capacitance. It expressly says the documentation does not determine suitability for a specific user application. FSR1/FSR2, installed wiring, supply behavior, temperature, opening waveform and application suitability also remain open. Therefore no divider or protection values are released for `K1_A1` or `K2_A1`.

Primary source: Schneider Electric, `SQD-LC1D25BD.PDF`, dated 2017-09-13 and accessed 2026-08-10.

### Texas Instruments AMC3330

TI `SBASA34B` defines a ±1 V linear input, ±1.25 V clipping threshold, -6 V to `VHLDOout + 0.5 V` input absolute maximum, 10 mA continuous pin-current limit, 0.1 GΩ minimum input resistance and 2 pF input capacitance. TI's application example limits divider cross current to 100 µA and instructs the designer to calculate a divider from the nominal and maximum overvoltage requirements. TI also states that customers must validate suitability. The EVM guide separately states that the board is not certified for high-voltage operation.

Those device facts define design equations, not the Project Button node envelope or noninterference limit. `electrical/analysis/hr-v0-event-tap-disposition-p0.1/calculation-screen.csv` retains the resulting equations with unresolved Project Button inputs.

## Why catalog-only resistor selection is rejected

Choosing a divider solely from nominal 24 V would omit:

1. allowed loading and capacitance on the Pilz monitored paths;
2. field-node reverse and transient voltage;
3. AMC3330 input behavior after any resistor/protection open, short or drift;
4. added ground-fault and common-cause paths;
5. the start/EDM wiring fault-exclusion obligation;
6. coil-suppressor clamp and installed opening waveforms;
7. threshold delay and channel skew in the stopping-time uncertainty budget; and
8. physical tap-present versus tap-absent proof.

Accordingly, no resistance, capacitance, TVS, diode, fuse, connector, PCB material, creepage, clearance or order code is inferred.

## Native ECAD and interactive guide

`electrical/kicad/hr-v0-event-tap-disposition-p0.1/` contains a native KiCad 10.0.5 root and three child sheets. Each exact existing node terminates at a one-sided observation boundary. There is no AMC3330EVM pin, divider, protection part or field conductor on the right side. ERC is 0 errors / 0 warnings; that result validates only the encoded disposition topology.

The primary human guide is `release/hr-v0/event-tap-disposition-p0.1/index.html`. It filters the seven exact nodes and links the three native SVG exports. The PDF is a synchronized KiCad review export, not the primary guide.

## Gate effect

- `EG-025` remains **open**.
- `EG-026` remains **partial**.
- no procurement, field connection, powered test, motion or energization is authorized;
- no physical trace exists; and
- the DAQ, EVM, adapter and host receive **zero safety credit**.

Sol's resupplied analysis remains the existing independent R12 review and is not counted as a new independent round. R178 is a project-owned correction/disposition pass responding to its physical-instrumentation and stopping-evidence findings.

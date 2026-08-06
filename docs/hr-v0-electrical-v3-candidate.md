# HR-V0 Electrical V3 Candidate Architecture

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Status: controlled design candidate for the next native KiCad correction. It is not a wiring instruction and does not supersede Electrical V2.1 until the connected V3 source, schedules, calculations, review, and tests are complete.

## Purpose

This candidate addresses two material V2.1 defects:

1. the single watchdog permit can reclose when heartbeat returns without forcing a new monitored start; and
2. the safety reset can make the contactor-coil circuit eligible without a separate hardware-enforced ARM stage.

The candidate also removes custom mains wiring from HR-V0. All project-built wiring is extra-low-voltage DC. Listed external adapters retain their unmodified factory AC inlets/cables and are not installed inside the control enclosure.

## Proposed power-source boundary

| Rail | Candidate | Manufacturer facts used | Release state |
|---|---|---|---|
| actuator 12 V | Mean Well `GST280A12-C6P` | 12 V, 21 A, 252 W; IEC C14 inlet; enclosed adapter; `-V` connected to AC protective earth; standard C6P output is a Molex 39-01-2060-equivalent six-position plug with pins 1-3 `+Vo` and 4-6 `-Vo`; file `GST280A-SPEC 2026-04-03` | candidate only; mating connector/contact order codes, source reverse-current behavior, regeneration, branch protection, and received-unit tests remain open |
| safety/control 24 V | Mean Well `GST40A24-P1J` | 24 V, 1.67 A, 40 W; class I IEC C14 adapter; center-positive 2.1 x 5.5 mm plug; `-V` is not connected to AC protective earth; file `GST40A-SPEC 2026-04-03` | candidate only; locking DC connector/interface, load/inrush budget, branch protection, and received-unit tests remain open |
| compute | official Raspberry Pi 27 W USB-C supply | independent compute power remains present for diagnostics when actuator energy is removed | regional order code and cable retention remain open |

The three external AC inputs shall use site-appropriate listed cords/receptacles and branch protection. No project-built mains splitter, inlet, disconnect, fuse holder, exposed terminal, or internal AC wiring is permitted in this candidate. This change can remove the current internal-mains sheet from the HR-V0 implementation, but it does not close site jurisdiction, adapter suitability, EMC, protective-earth, or inspection obligations.

The `GST280A12-C6P` bonds actuator `0 V` to incoming protective earth inside the adapter. Therefore V3 shall not add `SP1` or any second 0 V/PE bond. Any robot-frame or shield connection must be reviewed against this fixed source bond and checked for unintended parallel paths. Replacing the source changes that conclusion and requires a new bonding review.

## Corrected reset, watchdog, ARM, and EDM topology

V3 uses two separately identified PNOZ s4 750104 relays:

- `SR1` is the E-stop eligibility relay. It monitors the two positively opening E-stop NC channels and accepts the physical `RESET` action. Its outputs do not drive K1/K2 directly.
- `SRA1` is the final ARM/EDM relay. Each of its two input channels contains one force-guided output from `SR1` in series with one independent watchdog-channel contact. `SRA1` uses monitored falling-edge start. Its start/feedback loop contains the distinct physical `ARM` pushbutton followed by the valid NC mirror contacts of K1 and K2. Its separate safety outputs drive the K1 and K2 coils.

Proposed logical paths:

```text
E-STOP CH1 ---- SR1 input channel 1
E-STOP CH2 ---- SR1 input channel 2
RESET + SR1 feedback/start mode ---- SR1 S34

SR1 safety output A -- WD relay A NO ---- SRA1 input channel 1
SR1 safety output B -- WD relay B NO ---- SRA1 input channel 2
SRA1 S12 -- physical ARM NO -- K1 mirror NC -- K2 mirror NC -- SRA1 S34

SRA1 safety output 1 -- K1 coil
SRA1 safety output 2 -- K2 coil
K1 and K2 main contacts remain in series in the 12 V actuator rail
```

Required sequence:

1. E-stop channels close and the watchdog channels are healthy.
2. The operator actuates and releases `RESET`; `SR1` becomes eligible.
3. K1 and K2 remain de-energized because `SRA1` has not accepted ARM.
4. The operator separately actuates and releases `ARM`; only then may `SRA1` energize K1/K2.
5. Motion remains inhibited until contactor feedback, actuator state, limits, configuration, and a fresh trajectory all pass in software.

Any E-stop opening, watchdog-channel opening, SR1 dropout, channel discrepancy, K1/K2 mirror-contact fault, or SRA1 fault drops the final outputs. E-stop release, heartbeat restoration, controller reboot, a held RESET, or stale commands cannot energize K1/K2. After any dropout the complete RESET-then-ARM sequence is required.

## Watchdog-channel boundary

The current RP2040-class watchdog is not safety-rated. V3 replaces the single KWD1 contact with two independently driven, normally-open relay channels and routes them separately to SRA1. The final parts, drivers, feedback contacts, startup tests, brownout behavior, diagnostic coverage, common-cause controls, and firmware remain `SELECTION REQUIRED`.

This topology improves restart behavior and single-channel diagnostics. It does **not** establish a Performance Level or SIL because both channels may still share a non-safety controller, power source, clock, firmware, or common-cause failure. Qualified risk assessment shall either:

- allocate and validate an integrity target that this implementation can meet;
- replace the watchdog source with an accepted safety-rated architecture; or
- treat watchdog stopping as a non-safety diagnostic while independent guarding/E-stop functions carry the risk reduction.

## Contactor candidate boundary

`LC1D25BD` remains only a candidate. Current Schneider data identify a 24 VDC coil, mechanically linked 1NO+1NC auxiliaries with an NC mirror contact, built-in bidirectional peak-limiting diode suppression, 16-24 ms opening time, and a 2.5 N m power-terminal torque. The current DC-1 selection table includes an LC1D25-class rating above the screened HR-V0 current at 24 VDC, but the robot is a capacitive, inductive, and potentially regenerative electronic load rather than a proved DC-1 resistive load.

V3 may show all three power poles in series per contactor only after Schneider application guidance confirms the exact 12 VDC making/breaking arrangement. Final release still requires prospective fault current, downstream capacitance, regeneration energy, source behavior, conductor/protection coordination, loaded interruption, contact-weld injection, dropout, rail-decay, and stopping-distance tests. The built-in `BD` suppression shall not be duplicated by an assumed external network.

## Preliminary 24 V load screen

Manufacturer values currently support this screening calculation:

- two LC1D25BD coils: `2 x 5.4 W = 10.8 W`;
- two PNOZ s4 relays: `2 x 2.5 W = 5.0 W`;
- subtotal: `15.8 W`, or `0.658 A` at 24 V before watchdog relays, indicators, interfaces, losses, and transient margin.

The 40 W / 1.67 A adapter has apparent nameplate headroom, but this is not a released load budget. Exact watchdog relays, input currents, simultaneous inrush, output protection, wiring loss, ambient derating, and fault behavior must be added and tested.

## Mandatory V3 deliverables

Before this candidate can replace V2.1:

1. create connected native KiCad sheets with separate `RESET` and `ARM`, two PNOZ devices, two watchdog channels, explicit K1/K2 poles and mirror contacts, and the external-adapter boundary;
2. freeze every terminal and connector from exact manufacturer drawings;
3. regenerate BOM, connector schedule, wire table, netlist, PDF/SVG, unresolved register, source manifest, and ERC output from the same commit;
4. perform PLr/SIL and common-cause analysis without crediting ordinary firmware by assertion;
5. execute `TEST-SAFE-001` through `TEST-SAFE-003` first with contactor loads disconnected and then under the released load; and
6. obtain qualified electrical and functional-safety review.

No part of this document authorizes ordering, wiring, fabrication, or energization.

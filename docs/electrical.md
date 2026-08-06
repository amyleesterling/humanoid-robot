# Electrical and Safety Architecture

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Status: architecture baseline; a reviewed ECAD schematic and panel layout are required before wiring.

## Power domains

| Rail | Source | Loads | Emergency-stop behavior |
|---|---|---|---|
| AC mains | protected lab outlet | enclosed supplies | upstream disconnect removes all power |
| 12 V `ACTUATOR_BUS` | Mean Well LRS-350-12 | three DYNAMIXEL actuators | removed by K1 and K2 |
| 24 V `SAFETY_24V` | Mean Well HDR-30-24 | safety relay, K1/K2 coils, indicators | remains on during E-stop |
| 5 V compute | official Raspberry Pi 27 W USB-C supply | Pi 5 and USB interface | remains on during E-stop |

All exposed AC terminals shall be inside a grounded, tool-access enclosure. Protective earth bonds the enclosure, DIN rail when required, supply chassis, robot base, and bench bonding point. DC 0 V is connected to protective earth at one documented star point only after EMC review.

## Safety chain

Proposed components are an exact-selection-required IDEC XW-series dual-channel emergency-stop switch, Pilz PNOZ s4 24 VDC safety relay order code 750104 configured for monitored start on the falling edge with cross-short detection on the E-stop inputs, and two Schneider LC1D25BD 24 VDC-coil contactors in series. The [PNOZ s4 operating manual 21396-EN-23](https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf) (2026-02 document colophon; product file dated 2026-06-22; verified 2026-08-05) documents the proposed `S11/S12` and `S21/S22` E-stop channels and the `S12 -> momentary NO reset -> K1 NC -> K2 NC -> S34` start/feedback loop. K1/K2 normally closed mirror auxiliary contacts form that external-device-monitor feedback loop. The safety relay outputs shall drive only the contactor coils, not the actuator current directly.

Electrical V2.1 currently represents this logical chain:

`E-STOP CH1 + E-STOP CH2 -> PNOZ s4 falling-edge monitored-start mode -> reset + K1/K2 feedback -> watchdog permit -> separately protected K1 and K2 coils`

That downstream watchdog-permit position is a **BLOCKER**. A lost heartbeat can open K1/K2 while the PNOZ outputs remain closed; restored heartbeat can then reclose the coil path without a new PNOZ reset/EDM cycle. The RP2040-class firmware latch is not a credited safety mechanism. A released revision shall alter the hardware so watchdog dropout forces a hardware-held restart-required state and neither coil can re-energize until a monitored physical reset and a later distinct `ARM` action have both occurred. Candidate remedies include routing watchdog loss into an evaluated safety-device input so it forces a complete monitored-start cycle, or adding an independently reviewed hardware restart interlock. These are alternatives, not selections; the exact circuit and hardware remain **SELECTION REQUIRED**.

Required restart sequence:

`heartbeat invalid -> watchdog permit opens -> K1 and K2 drop -> EDM proves dropped -> heartbeat may become healthy but coils stay inhibited -> valid falling-edge physical reset -> SAFE_READY with coils still inhibited -> distinct ARM -> contactors may energize -> fresh trajectory validation -> torque/motion`

Power chain:

`LRS-350-12 +V -> F0 (SELECTION REQUIRED) -> K1 pole -> K2 pole -> branch protection (SELECTION REQUIRED) -> J1/J2/gripper`

Opening either contactor removes actuator VDD. The control computer detects loss through isolated auxiliary status inputs and records it, but software indication is not part of the energy-removal safety function. Physical reset shall not re-energize contactors, create torque, or cause motion by itself. A separate deliberate `ARM` command is required after all state checks pass, and a fresh command is required before torque or motion.

For the proposed 750104, the mode selector shall be set with supply removed to the manual page-13 lower-row, third-column mode: “with detection of shorts across contacts / monitored start falling edge.” The setting shall be sealed and inspected against the received device. In this mode the reset control must close and then open; the published falling-edge wait for 750104 is 250 ms and the minimum start pulse is 100 ms. These are device characteristics, not proof that the application is safe.

The PNOZ s4 does not detect shorts or cross-shorts in its `S12 -> reset -> K1 NC -> K2 NC -> S34` start/feedback loop. That loop therefore requires protected or separate routing and a documented fault exclusion accepted by the qualified safety review. A normal schematic/ERC result cannot validate that physical routing or exclusion. Terminals `13-14`, `23-24`, and `33-34` are the safety normally open outputs; `41-42` and `Y32` are diagnostic only and shall not close, bypass, or claim any safety function.

PNOZ output-contact protection `FSR1`/`FSRH1` and the K1/K2/KH1/KH2 coil-suppression networks remain **SELECTION REQUIRED**. Manufacturer-published maximum protection values are limits, not released fuse selections. Protection shall be coordinated with exact coil inrush, safety-supply fault behavior, conductor ampacity, prospective fault current, and interrupting capacity. Suppression shall be selected against both the safety-relay and contactor instructions and validated for fault behavior, coil release time, contactor dropout time, residual travel, and total stopping time.

## Branches and conductors

| Branch | Load | Fuse | Conductor |
|---|---|---|---|
| F1 | J1 XM540-W270-T | SELECTION REQUIRED | SELECTION REQUIRED |
| F2 | J2 XM540-W270-T | SELECTION REQUIRED | SELECTION REQUIRED |
| F3 | gripper XM430-W350-T | SELECTION REQUIRED | SELECTION REQUIRED |

No fuse or conductor value is released. Coordination requires prospective fault current, cable length, ambient temperature, bundling, insulation and installation method, connector limits, actuator inrush and regeneration, duty cycle, simultaneous load, acceptable voltage drop, and jurisdiction. The LRS-350-12 specification revision 2025-09-12 lists a 110-140% rated-power overload threshold with hiccup recovery, a one-second maximum 150% peak load allowance, and 60 A typical cold-start AC inrush, but does not publish the maximum, duration, waveform, T50, or I-squared-t needed to select protection. Its 115/230 V selector position must be inspected and controlled before any permitted energization.

The ROBOTIS U2D2 Power Hub documentation gives a 3.5-24.0 V range and 10.0 A maximum, and permits only one of its three power inputs. It shall not carry summed robot actuator current. Star-injected power is allowed only with a released custom data interconnect or breakout that omits or isolates VDD on every inter-actuator and U2D2 data link. Standard fully populated 3-pin TTL and 4-pin RS-485 DYNAMIXEL cables carry VDD on pin 2 and can parallel individually protected branches; they are prohibited in this topology until an end-to-end continuity and no-backfeed test proves the released harness.

## Pin-level net rules

- DYNAMIXEL TTL: pin 1 `DGND`, pin 2 `ACTUATOR_12V`, pin 3 `DXL_DATA`; confirm connector orientation against the exact actuator manual before crimping.
- U2D2 USB connects to the Pi. ROBOTIS calls interface pin 2 `VDD`; it does not document that pin as a sense input or publish the internal current path. Omit pin 2 from the released custom data cable unless ROBOTIS supplies applicable written evidence and qualified review accepts it.
- E-stop uses two normally closed, positively opening contacts on separate safety-relay channels.
- Reset is a normally open momentary switch outside the swept envelope.
- No software-controlled device may bridge or bypass either E-stop channel.
- Coil flyback suppression shall follow contactor and safety-relay instructions and shall not extend unsafe dropout time.

## Required electrical drawings before release

ECAD shall include terminal numbers, wire numbers, connector part numbers, contact cross-references, PE/grounding, fuse types, conductor gauges/colors, cable shield treatment, enclosure layout, creepage/clearance, supply input protection, and measured prospective short-circuit assumptions. A qualified person shall review mains and safety wiring before energization.

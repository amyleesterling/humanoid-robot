# Electrical and Safety Architecture

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

Proposed components are an exact-selection-required IDEC XW-series dual-channel emergency-stop switch, Pilz PNOZ s4 24 VDC safety relay order code 750104 configured for monitored start on the falling edge with cross-short detection on the E-stop inputs, and two Schneider LC1D25BD 24 VDC-coil contactors in series. The PNOZ s4 operating manual 21396-EN-23 (2026-02 document colophon; product file dated 2026-06-22) documents the proposed `S11/S12` and `S21/S22` E-stop channels and the `S12 -> momentary NO reset -> K1 NC -> K2 NC -> S34` start/feedback loop. K1/K2 normally closed mirror auxiliary contacts form that external-device-monitor feedback loop. The safety relay outputs shall drive only the contactor coils, not the actuator current directly.

Logical chain:

`E-STOP CH1 + E-STOP CH2 -> PNOZ s4 falling-edge monitored-start mode -> reset + K1/K2 feedback -> watchdog permit -> separately protected K1 and K2 coils`

Power chain:

`LRS-350-12 +V -> F0 (SELECTION REQUIRED) -> K1 pole -> K2 pole -> branch protection (SELECTION REQUIRED) -> J1/J2/gripper`

Opening either contactor removes actuator VDD. The control computer detects loss through isolated auxiliary status inputs and records it. Reset shall not cause motion; it only restores actuator power eligibility. A separate deliberate `ARM` command is required after all state checks pass. The PNOZ s4 does not detect shorts or cross-shorts in its start/feedback loop, so that loop requires protected or separate routing and fault exclusion justified by the qualified safety review. Terminals `41-42` and `Y32` are diagnostic only and shall not close any safety function. Output-contact protection and coil suppression are `SELECTION REQUIRED`; suppression shall follow the device manuals and shall be validated not to extend dropout or stopping time unacceptably.

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

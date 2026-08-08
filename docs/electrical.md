# Electrical and Safety Architecture

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Status: architecture baseline with a native connected V3 candidate; qualified review, exact selections, panel/harness release, and physical validation are required before wiring.

## Power domains

| Rail | Source | Loads | Emergency-stop behavior |
|---|---|---|---|
| AC mains | site receptacles and three unmodified factory AC inputs | external adapters only | upstream site disconnect removes all power |
| 12 V `ACTUATOR_BUS` | proposed Mean Well GST280A12-C6P external adapter | three DYNAMIXEL actuators | removed by K1 and K2 |
| 24 V `SAFETY_24V` | proposed GlobTek `WR9QI1660YL4NKITR6B` Class II/floating wall adapter with factory `YL4/C40337` locking cord | SR1/SRA1, K1/K2 coils, watchdog relays, indicators | remains on during E-stop; received plug identity/fit, F24, startup, thermal and fault behavior remain held |
| 5 V compute | official Raspberry Pi 27 W USB-C supply | Pi 5 and USB interface | remains on during E-stop |

The V3 candidate contains no project-built mains wiring, exposed AC terminal, internal AC supply, or project mains splitter. The factory adapters remain external and unmodified. Site cords, receptacles, branch protection, GFCI/code basis, source application review, and disconnect access remain open.

The GST280A12-C6P manufacturer schematic bonds output `-V` to incoming protective earth inside the adapter. V3 therefore marks the former project `0 V`/PE star point `SP1` **DNP - PROHIBITED**. Robot-frame and cable-shield treatment remain open pending EMC and parallel-path review; replacing the source requires a fresh bonding assessment.

## Safety chain

The V3 candidate uses an exact-but-unreleased IDEC `XW1E-BV402M-R` dual-NC E-stop candidate, two separately identified Pilz PNOZ s4 24 VDC relays order code 750104, a distinct RESET candidate, a visually distinct ARM candidate, two separately driven watchdog relay contacts, and two Schneider `LC1D25BD` 24 VDC-coil contactors in series. Schneider Catalog 2026 now supports the represented one-through-three-pole series topology at its published 24 V row and the integrated NC mirror/linked-contact evidence, but the catalog's lower-current critical-current warning applies to the 11.1 A HR-V0 screen. Exact 12 V electronic/regenerative duty, written application confirmation, protection and physical loaded tests remain open. All devices remain proposed or `SELECTION REQUIRED`; V3 does not establish functional-safety performance.

The [PNOZ s4 operating manual 21396-EN-23](https://www.pilz.com/download/open/OM_PNOZ_s4_21396-EN-23.pdf) (2026-02 document colophon; product file dated 2026-06-22; verified 2026-08-06) supports the proposed cross-short-detection and monitored falling-edge start mode. `SR1` monitors two series paths, each containing one positively opening E-stop NC contact and one watchdog NO contact, and accepts RESET. Heartbeat loss therefore opens both SR1 input returns and forces the RESET stage to drop. SR1's outputs feed the two SRA1 input channels but do not drive the contactors. `SRA1` accepts a later distinct physical ARM action through the K1/K2 mirror-contact EDM return. Separate SRA1 outputs feed the K1 and K2 coil-protection paths.

Electrical V2.1 currently represents this logical chain:

`E-STOP CH1 + E-STOP CH2 -> PNOZ s4 falling-edge monitored-start mode -> reset + K1/K2 feedback -> watchdog permit -> separately protected K1 and K2 coils`

That V2.1 downstream watchdog-permit position remains a **BLOCKER** for V2.1. The corrected native V3-P1.11 source routes one watchdog contact through each SR1 input return. A watchdog dropout therefore requires a new monitored RESET at SR1 and then a separate monitored ARM at SRA1. P1.8 retains the exact Phoenix `3211861` FSR1/FSR2 holders and `D-ST 4` item `3030420` group end-cover candidate, and freezes active Littelfuse `75920-01` only as the exact SPST high-side SD1 catalog candidate. `TBD-HA/TBD-HB`, `SD1:TBD-IN/TBD-OUT`, both FSR fuse links, received accessory compatibility/grouping, SD1 conductor/fault/load-break/touch-protection/lockout application and all protection coordination remain unresolved. H1 is diagnostic-only and has no safety credit or motion authority. PCB-P0.5 and DXL-STAR-P0.1 are routed and DRC-clean source candidates, but neither is a fabrication release. R64 adds `HR-V0-CP-P0.4` and `HR-V0-SD-P0.2`; it releases no drilling, cutting, conductors, protection values, lockout procedure, PE bond, glands, assembly or PCB fabrication. Received-device proof, cable construction, connector-current application, passive measurements/derating, RESET/ARM/H1 terminals, panel depth/heat/duct-fill/bonding/human factors, source current division, converter brownout, supplier acceptance, physical test access, COM-slew, protection/conductors, no-backfeed, signal integrity, EMC, thermal, fault injection and HIL remain open. R44 classifies this ordinary heartbeat path as `DF-01` with **NO SAFETY CREDIT**: welded contacts and shared controller/supply/clock/firmware failures are assumed possible. Physical routing and fault analysis must still prove that `DF-01` cannot impair the separately credited-candidate `SF-01` E-stop or `SF-03` restart-prevention paths. See `docs/hr-v0-functional-safety-allocation-p0.1.md`.

Required restart sequence:

`heartbeat invalid -> watchdog permit opens -> K1 and K2 drop -> EDM proves dropped -> heartbeat may become healthy but coils stay inhibited -> valid falling-edge physical reset -> SAFE_READY with coils still inhibited -> distinct ARM -> contactors may energize -> fresh trajectory validation -> torque/motion`

Power chain:

`GST280A12-C6P +V -> F0 (SELECTION REQUIRED) -> SD1 Littelfuse 75920-01 (exact catalog candidate; installed application held) -> all three K1 poles in series -> all three K2 poles in series -> F1/F2/F3 (SELECTION REQUIRED) -> DXL-STAR-P0.1 separate J1/J2/J3 VDD paths`

Opening either contactor removes actuator VDD. The control computer detects loss through isolated auxiliary status inputs and records it, but software indication is not part of the energy-removal safety function. Physical reset shall not re-energize contactors, create torque, or cause motion by itself. A separate deliberate `ARM` command is required after all state checks pass, and a fresh command is required before torque or motion.

For the proposed 750104, the mode selector shall be set with supply removed to the manual page-13 lower-row, third-column mode: “with detection of shorts across contacts / monitored start falling edge.” The setting shall be sealed and inspected against the received device. In this mode the reset control must close and then open; the published falling-edge wait for 750104 is 250 ms and the minimum start pulse is 100 ms. These are device characteristics, not proof that the application is safe.

The PNOZ s4 does not detect shorts or cross-shorts in its start/feedback return. In V3 these are two distinct circuits: SR1 uses its physical RESET return, while SRA1 uses the physical ARM followed by K1 and K2 NC mirror contacts. Both returns therefore require protected or separate routing and documented fault exclusions accepted by the qualified safety review. A normal schematic/ERC result cannot validate that physical routing or exclusion. Terminals `13-14`, `23-24`, and `33-34` are safety normally open outputs; `41-42` and `Y32` are diagnostic only and shall not close, bypass, or claim any safety function.

PNOZ output-contact protection `FSR1` and `FSR2` remains **SELECTION REQUIRED**. Manufacturer-published maximum protection values are limits, not released fuse selections. Protection shall be coordinated with exact coil behavior, safety-supply fault behavior, conductor ampacity, prospective fault current, and interrupting capacity. The proposed `LC1D25BD` coil already contains a bidirectional peak-limiting diode; V3 does not add an assumed external flyback network. The Schneider contactor evidence and exact closure route are controlled in `docs/hr-v0-contactor-application-p0.1.md`. The received contactor, coil release time, critical-current/application disposition, dropout time, rail decay, residual travel, and total stopping time still require validation.

## Branches and conductors

| Branch | Load | Fuse | Conductor |
|---|---|---|---|
| F1 | J1 XM540-W270-T | SELECTION REQUIRED | SELECTION REQUIRED |
| F2 | J2 XM540-W270-T | SELECTION REQUIRED | SELECTION REQUIRED |
| F3 | gripper XM430-W350-T | SELECTION REQUIRED | SELECTION REQUIRED |

No fuse or conductor value is released. Coordination requires prospective DC fault current and source current limiting, cable length, ambient temperature, bundling, insulation and installation method, connector limits, actuator inrush and regeneration, duty cycle, simultaneous load, acceptable voltage drop, clearing behavior, and jurisdiction. The GST280A12-C6P is only a proposed source; mating connector/contact selection, reverse-current and regeneration behavior, branch coordination, received-unit inspection, and open-circuit/loaded tests remain unresolved.

R36 freezes only a protection hardware boundary for analysis: Littelfuse `FHAC0002SXJ` is the proposed F0 holder, Blue Sea Systems `5025` is the proposed F1-F3 block, and Littelfuse `ATOF` is the proposed fuse family. No ampere-specific order code is released. The [P0.1 coordination package](hr-v0-protection-coordination-p0.1.md) identifies every missing input and records the material connector conflict: XM540's 4.4 A published stall endpoint exceeds the JST EH series' 3 A published basis. Physical duty/current limiting, harness identity, connector temperature and fault-clearing evidence must resolve that conflict before a branch rating can be selected.

The ROBOTIS U2D2 Power Hub documentation gives a 3.5-24.0 V range and 10.0 A maximum, and permits only one of its three power inputs. It shall not carry summed robot actuator current. Star-injected power is allowed only with a released custom data interconnect or breakout that omits or isolates VDD on every inter-actuator and U2D2 data link. Standard fully populated 3-pin TTL and 4-pin RS-485 DYNAMIXEL cables carry VDD on pin 2 and can parallel individually protected branches; they are prohibited in this topology until an end-to-end continuity and no-backfeed test proves the released harness.

## Pin-level net rules

- DYNAMIXEL TTL: pin 1 `GND` is the common actuator/data reference `ACT_0V_PE_BONDED`, pin 2 receives only that actuator's separately protected `J1_VDD`/`J2_VDD`/`J3_VDD`, and pin 3 is common `DXL_TTL_DATA`; confirm plug/socket orientation against the exact actuator manual before crimping.
- U2D2 USB connects to the Pi. ROBOTIS calls interface pin 2 `VDD`; it does not document that pin as a sense input or publish the internal current path. Omit pin 2 from the released custom data cable unless ROBOTIS supplies applicable written evidence and qualified review accepts it.
- V3 models the non-isolated watchdog converter, Pico, relay drivers, ISO1212 logic and field grounds, and debug connector on common `SAFETY_0V`. The 24 V relay diagnostic nets terminate at the `UFB1` threshold/current-limit networks and shall never connect directly to a Pico GPIO. Because `GND1`, `FGND1`, and `FGND2` share `SAFETY_0V`, no galvanic-isolation or safety-integrity credit is claimed for the ISO1212 barrier. A separated-ground implementation would be a different architecture and requires a new schematic and grounding/fault review.
- E-stop uses two normally closed, positively opening contacts on separate safety-relay channels.
- Reset is a normally open momentary switch outside the swept envelope.
- No software-controlled device may bridge or bypass either E-stop channel.
- Coil flyback suppression shall follow contactor and safety-relay instructions and shall not extend unsafe dropout time.

## Required electrical drawings before release

ECAD shall include terminal numbers, wire numbers, connector part numbers, contact cross-references, PE/grounding, fuse types, conductor gauges/colors, cable shield treatment, enclosure layout, creepage/clearance, supply input protection, and measured prospective short-circuit assumptions. A qualified person shall review mains and safety wiring before energization.

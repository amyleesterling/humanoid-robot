# HR-V0 Electrical V3 Candidate Architecture

> **PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Status: native connected design candidate `V3-P1.10`. It is not a wiring instruction and does not supersede the independently reviewed Electrical V2.1 package until exact selections, calculations, physical tests, and qualified review are complete. `V3-P0.1` through P1.9 are retained as historical configurations. P1.3 records current Schneider contactor application evidence and the catalog's lower-current/critical-current blocker without releasing K1/K2. P1.4 adds a received-lot terminal-control boundary for RESET and ARM. P1.5 freezes exact amber H1 and retains two project placeholder terminals pending received evidence. P1.6 freezes the Phoenix `3211861` FSR1/FSR2 holder candidates; P1.7 freezes `D-ST 4` item `3030420` as the group end-cover candidate. P1.8 freezes active Littelfuse `75920-01` only as the exact SPST high-side SD1 catalog candidate. P1.9 reconciles the exact XT1 Phoenix family and six position-to-net candidates with the physical-panel record. P1.10 replaces the ambiguous system `JC1` block with `J24` and separate `F24`, and freezes the held Mean Well `DC PLUG-P1J-R7B` / Kycon `KPJX-PM-4S` four-pin topology. Written source/accessory compatibility, adapter current/application limits, received polarity, PCB/harness, panel mounting/retention, F24 selection and physical tests remain open. `TBD-IN/TBD-OUT`, conductor/lug, source fault, load-break, touch protection, cutout, zero-energy/padlock application, human factors and qualified Boston review remain open, as do both FSR fuse links, received compatibility/grouping, XT1 conductor/protection/physical evidence, protection coordination and physical evidence. The separate PCB-P0.5 watchdog board and DXL-STAR-P0.1 actuator board are routed native candidates while retaining supplier acceptance, received, protection, harness, derating, physical, fault, EMC and qualified-review gates.

- Native source: `electrical/kicad/project-button-v3/project-button-v3.kicad_pro`
- Generator: `tools/generate_hr_v0_electrical_v3.py`
- Consistency checker: `tools/check_hr_v0_electrical_v3.py`

## Purpose

This candidate addresses two material V2.1 defects:

1. the single watchdog permit can reclose when heartbeat returns without forcing a new monitored start; and
2. the safety reset can make the contactor-coil circuit eligible without a separate hardware-enforced ARM stage.

The candidate also removes custom mains wiring from HR-V0. All project-built wiring is extra-low-voltage DC. Listed external adapters retain their unmodified factory AC inlets/cables and are not installed inside the control enclosure.

## Proposed power-source boundary

| Rail | Candidate | Manufacturer facts used | Release state |
|---|---|---|---|
| actuator 12 V | Mean Well `GST280A12-C6P` with proposed project-side Molex `39012066` housing and six `444783112` HCS male contacts | 12 V, 21 A, 252 W; IEC C14 inlet; enclosed adapter; `-V` connected to AC protective earth; C6P output is a Molex 39-01-2060-equivalent receptacle with pins 1-3 `+Vo` and 4-6 `-Vo`; project contacts are 16 AWG HCS candidates with an 11 A/contact manufacturer guideline for 4-6 circuits | candidate only; source-side contact construction, actual current division, exact wire/length, crimp/retention, strain relief, reverse-current behavior, regeneration, branch protection, thermal evidence, and received-unit tests remain open |
| safety/control 24 V | Mean Well `GST40A24-P1J` | 24 V, 1.67 A, 40 W; class I IEC C14 adapter; center-positive 2.1 x 5.5 mm plug; `-V` is not connected to AC protective earth; file `GST40A-SPEC 2026-04-03` | candidate only; locking DC connector/interface, load/inrush budget, branch protection, and received-unit tests remain open |
| compute | official `Raspberry Pi 27W USB-C Power Supply US` | independent compute power remains present for diagnostics when actuator energy is removed; official brief `RP-008245-DS-1` identifies the US/Canada Type-A model, 5.1 V / 5 A profile, 1.2 m 17 AWG fixed cable, and production through at least January 2035 | the primary portal lists twelve family SKUs but does not map them to region/color; exact SKU, color, mechanical retention, site receptacle, and received-unit test remain open |

The three external AC inputs shall use site-appropriate listed cords/receptacles and branch protection. No project-built mains splitter, inlet, disconnect, fuse holder, exposed terminal, or internal AC wiring is permitted in this candidate. This change can remove the current internal-mains sheet from the HR-V0 implementation, but it does not close site jurisdiction, adapter suitability, EMC, protective-earth, or inspection obligations.

The `GST280A12-C6P` bonds actuator `0 V` to incoming protective earth inside the adapter. Therefore V3 shall not add `SP1` or any second 0 V/PE bond. Any robot-frame or shield connection must be reviewed against this fixed source bond and checked for unintended parallel paths. Replacing the source changes that conclusion and requires a new bonding review.

P0.7 allocates `JA1` pins 1-3 to three separate `ACT_12V_RAW` conductors and pins 4-6 to three separate `ACT_0V_PE_BONDED` conductors. The idealized screen is `21 A / 3 = 7 A/contact` versus the project-side HCS 11 A guideline, but neither equal sharing nor source-side contact capacity is assumed. `INSPECT-ELEC-004` requires received-part identity, controlled crimping, destructive pull samples, retention/continuity/polarity checks, six-leg current measurement and stabilized thermal evidence in the released arrangement before this interface can be released.

## Corrected reset, watchdog, ARM, and EDM topology

V3 uses two separately identified PNOZ s4 750104 relays:

- `SR1` is the E-stop/watchdog eligibility relay. Each input path contains one positively opening E-stop NC contact in series with one independent watchdog NO contact. It accepts the physical `RESET` action. Its outputs do not drive K1/K2 directly.
- `SRA1` is the final ARM/EDM relay. Its two input channels are fed by separate force-guided outputs from `SR1`. `SRA1` uses monitored falling-edge start. Its start/feedback loop contains the distinct physical `ARM` pushbutton followed by the valid NC mirror contacts of K1 and K2. Its separate safety outputs drive the K1 and K2 coils.

Proposed logical paths:

```text
SR1 S11 -- E-STOP CH1 NC -- WD relay A NO -- SR1 S12
SR1 S21 -- E-STOP CH2 NC -- WD relay B NO -- SR1 S22
RESET + SR1 feedback/start mode ---- SR1 S34

SR1 safety output A ---- SRA1 input channel 1
SR1 safety output B ---- SRA1 input channel 2
SRA1 S12 -- physical ARM NO -- K1 mirror NC -- K2 mirror NC -- SRA1 S34

SRA1 safety output 1 -- K1 coil
SRA1 safety output 2 -- K2 coil
K1 and K2 main contacts remain in series in the 12 V actuator rail
```

Required sequence:

1. E-stop channels close and heartbeat recovery closes both watchdog contacts, but SR1 remains dropped.
2. The operator actuates and releases `RESET`; `SR1` becomes eligible.
3. K1 and K2 remain de-energized because `SRA1` has not accepted ARM.
4. The operator separately actuates and releases `ARM`; only then may `SRA1` energize K1/K2.
5. Motion remains inhibited until contactor feedback, actuator state, limits, configuration, and a fresh trajectory all pass in software.

P0.5 freezes `S1` as IDEC `HW1B-M1F10-B` (black) with the explicit `RESET` legend and `S2` as IDEC `HW1B-M1F10-G` (green) with the explicit `ARM` legend. IDEC's current US pages and `HW Series Catalog_Screw` dated 2026-07-23 identify both as flush momentary 1NO screw-terminal complete assemblies and identify `B` and `G` as the black and green color codes. This corrects the earlier same-black-operator ambiguity. P1.4 adds a fail-closed received-lot control: IDEC's 2026-07-14 specification-change notice says prior and redesigned assemblies may ship under the same complete order codes and internal BOM codes changed, while the live product-page BOM returned no component detail on 2026-08-07. The project therefore freezes no internal contact block or terminal number. S1/S2 physical terminals, panel spacing, guarding, location and human-factors acceptance remain open until `docs/hr-v0-reset-arm-receiving-p0.1.md` and `tests/forms/hr-v0-reset-arm-receiving-template.csv` are executed and independently checked.

P1.5 freezes H1 as IDEC `HW1P-1FQD-A-24V`, which the current IDEC USA page identifies as an amber round-flush pilot light with black plastic bezel, screw terminals and 24 VAC/DC illumination. The previous value `SAFE ELIGIBLE indicator interface` and `+/-` pin names were misleading because H1 reports only `SR1_STATUS` and received terminal/internal-circuit/polarity evidence does not exist. H1 is now **RESET STAGE READY - DIAGNOSTIC ONLY / NO MOTION AUTHORITY**, receives no safety credit, and uses `TBD-HA/TBD-HB` project placeholders. Execute `docs/hr-v0-h1-receiving-p0.1.md` and its fourteen-row evidence form before replacing either placeholder or issuing a wire instruction.

P0.6 freezes only the manufacturer-supported XW E-stop contact positions. In the IDEC screw-terminal non-illuminated 2NC bottom view, with `TOP` up, one NC pair marked `1-2` is on the right and one is on the left. Project channel 1 is allocated to the right pair and channel 2 to the left pair. KiCad uses `R-1`, `R-2`, `L-1`, and `L-2` to keep the duplicate manufacturer markings unique; `R-` and `L-` are project prefixes, not markings claimed to exist on the switch. Received orientation, markings, positive-opening continuity and channel separation remain mandatory.

Any E-stop opening, watchdog-channel opening, SR1 dropout, channel discrepancy, K1/K2 mirror-contact fault, or SRA1 fault drops the final outputs. E-stop release, heartbeat restoration, controller reboot, a held RESET, or stale commands cannot energize K1/K2. After any dropout the complete RESET-then-ARM sequence is required.

## Watchdog-channel boundary

The current RP2040-class watchdog is not safety-rated. V3 replaces the single KWD1 contact with two independently driven, normally-open relay channels and routes one through each SR1 input return. This makes physical RESET part of the nominal recovery after heartbeat loss; SRA1 then still requires the later physical ARM. P0.9 freezes the ordinary signal interface, driver and feedback-passive candidates, but startup tests, brownout behavior, diagnostic coverage, common-cause controls, firmware binding, PCB, physical derating and HIL remain unreleased.

The modeled relay-coil path is `SAFETY_24V -> relay coil -> default-off low-side driver -> SAFETY_0V`. P0.7 proposes the non-isolated TRACO POWER `TSR 1-2450`: pin 1 `+VIN` to `SAFETY_24V`, pin 2 `GND` to `SAFETY_0V`, and pin 3 `+VOUT` to `WD_5V`. Its 6.5-36 V input and 5 V/1 A output support a candidate, not an application release. Branch protection, load budget, startup, slow-ramp brownout, fast dropout/recovery, stuck/overvoltage faults, EMC and enclosure thermal behavior remain open under `INSPECT-ELEC-004`. Selecting an isolated converter would require isolated output drivers and a fresh grounding/fault review. The official Phoenix product PDF freezes the candidate terminal designations `A1/A2`, `11-12-14`, and `21-22-24`, while received continuity and polarity evidence remain mandatory. P0.4 uses `11-14` in the SR1 return and `21-22` for a separate 24 V NC diagnostic feed. The latter terminates at the `UFB1` ISO1212DBQ field-input network and is prohibited from reaching a Pico GPIO directly.

The feedback sheet uses TI's exact DBQ pinout and Type-3 values: 1 kOhm `RTHR` from module input to `SENSE`, 562 Ohm `RSENSE` between `SENSE` and `IN`, and 10 nF `CIN` from `SENSE` to `FGND` per channel. A calculated 2.70 kOhm 1%, 0.5 W parallel wetting load raises the screened minimum Phoenix contact current above its documented 10 mA minimum at the Mean Well rail minimum. Outputs use 1 kOhm series resistors and 10 kOhm pulldowns before the Pico. P0.9 freezes the exact proposed Vishay, Panasonic, TDK and Murata passive order codes listed in `docs/hr-v0-watchdog-feedback-passive-closure-r30.md`. `GND1`, `FGND1`, and `FGND2` all return to `SAFETY_0V`, so no galvanic-isolation or safety-integrity credit is claimed. PCB, received measurements, DC-bias/power/pulse derating, terminals, EMC, thermal, brownout, fault injection and HIL remain open.

P0.8 routes `PI_HEARTBEAT` through Panasonic `ERJ6ENF9100V` and Vishay `VO618A-4X017T`; the watchdog collector is pulled to `WD_3V3` by `ERJ6ENF1002V`. Two distinct `TPL7407LPWR` packages use only channel 1: unused inputs are tied low, unused outputs are explicit no-connects, COM connects to `SAFETY_24V`, and each package has a proposed `GRM21BR71H104KA01L` bypass. See `docs/hr-v0-heartbeat-driver-closure-r29.md`. The bypass does not prove TI's COM-slew limit, and none of these parts receives safety credit before `TEST-ELEC-005`, FMEA and qualified review.

This topology improves restart behavior and single-channel diagnostics. It does **not** establish a Performance Level or SIL because both channels share or may share a non-safety controller, power source, clock, firmware, ordinary relays, or common-cause failure. R44 selects the only presently supportable HR-V0 classification: this is `DF-01`, an uncredited diagnostic whose failure is assumed. `SF-01` E-stop, `SF-03` restart prevention and the physically released `PG-01` fixed guard must carry the HR-V0 risk reduction. Any HR-V0 configuration whose fixed guard cannot contain assumed diagnostic failure, and all exposed HR-30 motion, require a separately selected and validated safety-rated `SF-02`. See `docs/hr-v0-functional-safety-allocation-p0.1.md`.

## Contactor candidate boundary

`LC1D25BD` remains only a candidate. Current Schneider data identify a 24 VDC coil, mechanically linked 1NO+1NC auxiliaries with an NC mirror contact, built-in bidirectional peak-limiting diode suppression, 16-24 ms opening time, and a 2.5 N m power-terminal torque. Schneider catalog `MKTED210011EN` (Catalog 2026, pp. A5/120-A5/123) gives 32 A at 24 V for the LC1D25 column with one, two or three poles in series. The same catalog warns that lower currents can have durability below the IEC 60947-4-1 definition because of critical current and directs the application to Schneider technical support. The 11.1 A HR-V0 summed-stall screen is below that row, and the robot is a capacitive, inductive, and potentially regenerative electronic load rather than a proved DC-1 resistive load.

V3 shows all three power poles in series per contactor as a proposed topology because the catalog expressly publishes one-through-three-pole series arrangements; it does not treat the 24 V row as a released 12 V application rating. Final release still requires measured break current and voltage, Schneider's identifiable application disposition for the low-current electronic/regenerative load, prospective fault current, downstream capacitance, regeneration energy, source behavior, conductor/protection coordination, loaded interruption, contact-weld injection, dropout, rail-decay, and stopping-distance tests. The built-in `BD` suppression shall not be duplicated by an assumed external network. See `docs/hr-v0-contactor-application-p0.1.md`.

## Preliminary 24 V load screen

Manufacturer values currently support this screening calculation:

- two LC1D25BD coils: `2 x 5.4 W = 10.8 W`;
- two PNOZ s4 relays: `2 x 2.5 W = 5.0 W`;
- subtotal: `15.8 W`, or `0.658 A` at 24 V before watchdog relays, indicators, interfaces, losses, and transient margin.

The 40 W / 1.67 A adapter has apparent nameplate headroom, but this is not a released load budget. Exact watchdog relays, input currents, simultaneous inrush, output protection, wiring loss, ambient derating, and fault behavior must be added and tested.

## TTL power-injection boundary

The U2D2 and all three actuator ports share `ACT_0V_PE_BONDED` as the TTL reference and share `DXL_TTL_DATA`. Electrical V3-P1.9 represents one central `INJ1`; its separate native `DXL-STAR-P0.1` project fixes `JC1:1` to return, `JC1:2` to no net/no copper and `JC1:3` to TTL data. `JP1`-`JP3` accept separately protected VDD branches and common return; `JA1`-`JA3` carry only their respective VDD plus common data/return. No VDD conductor joins actuator branches or reaches U2D2. The common reference means the Pi/U2D2 path can couple compute ground to actuator 0 V/PE, so exact USB and actuator cables, shields, frame, protection, EMC, signal integrity, thermal and power-sequencing/no-backfeed behavior still require physical review and test. See `docs/hr-v0-dxl-star-injection-p0.1.md`.

## Mandatory V3 deliverables

Before this candidate can replace V2.1:

1. **candidate complete:** create connected native KiCad sheets with separate `RESET` and `ARM`, two PNOZ devices, two watchdog channels, explicit K1/K2 poles and mirror contacts, and the external-adapter boundary;
2. freeze every remaining terminal, connector and passive order code from exact manufacturer drawings and application evidence;
3. regenerate BOM, connector schedule, wire table, netlist, PDF/SVG, unresolved register, source manifest, and ERC output from the same commit;
4. perform PLr/SIL and common-cause analysis without crediting ordinary firmware by assertion;
5. execute `TEST-SAFE-001` through `TEST-SAFE-003` first with contactor loads disconnected and then under the released load; and
6. obtain qualified electrical and functional-safety review.

## Native candidate validation record

The generated `V3-P1.10` candidate currently contains:

- one root index plus twelve focused child sheets;
- 77 component blocks and 297 modeled terminals;
- 100 native nets: 64 named connected nets plus 36 deliberate auto-generated unconnected nets;
- 261 unique wire labels synchronized to `wire-number-table.csv`;
- 75 nonzero-quantity V3 BOM records;
- 65 unresolved component/interface records; and
- 14 terminal designations deliberately retained as `TBD-*`.

KiCad 10.0.5 parsed the root and all twelve children, exported the native netlist, a thirteen-page A3 PDF and thirteen SVG pages, and reported `0 errors / 0 warnings` in ERC. The checker independently compares all 76 native component references and all 295 exported `(reference, terminal, net)` nodes against the generated schedules, including the 36 deliberate no-connect terminals. It freezes every ISO1212, VO618A and TPL7407L pin, their supporting networks, the watchdog-board terminals and the 18-terminal DXL-star system boundary. Clean ERC did not detect the historical P0.4 `RSENSE` application error, illustrating why exact-net, primary-source and physical checks remain separate.

The export is rendered at 150 dpi and visually checked after each material layout change. P1.3 retains the pin-level watchdog circuits, exact test points and DXL-star boundary while adding the controlled K1/K2 application evidence; it has 259 synchronized wire labels. The separate native PCB-P0.5 watchdog source retains 42 schematic references, 201 segments, 56 vias and three filled B.Cu zones. DXL-STAR-P0.1 has seven connector references, four board-only holes, 17 segments and one return zone. Both native DRC runs report zero violations/routed unconnected pads; neither project has fabrication outputs.

The KiCad CLI logs Windows registry-access messages for `HKCU\Software\kicad-cli` in this restricted execution environment. Every command still returned exit code 0 and produced the expected artifact; the messages are retained in `validation/kicad-cli.log` rather than hidden.

ERC ignores singleton-global-label, four-way-junction, SPICE-model, and footprint-filter checks in this generated block-level candidate. Clean ERC therefore proves only that the modeled annotation and connectivity rules passed. It does not validate received-device terminal orientation, conductor/protection sizing, application suitability, restart performance, fault tolerance, functional safety, fabrication, or permission to energize.

The current candidate is ready for another detailed electrical/design review, but not for wiring or energization. Deliverables 2 through 6 above remain open.

No part of this document authorizes ordering, wiring, fabrication, or energization.

# HR-V0 control-panel physical-definition candidate P0.5

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Package identifier: `HR-V0-CP-P0.5`
Electrical input: Project Button Electrical V3-P1.13
Purpose: synchronize the held panel candidate with the corrected watchdog-gated SR1 supply topology.

## Disposition

P0.5 inherits the bounded enclosure and provisional component envelopes from P0.4. It releases no enclosure, backplate, DIN-rail, wire duct, door, sidewall, or cable-entry fabrication. No backplate, enclosure, DIN-rail, duct, or door hole coordinate is released. All wire part numbers, gauges, colors, lengths, terminations, protection, cable entries, PE hardware, and final routing remain `SELECTION REQUIRED`.

The P0.1 reserve is physically insufficient for the retained protection and disconnect candidates. The nominal Hoffman `PJ242010RT` enclosure and `18P2117` backplate remain exact candidates only; procurement inspection and qualified layout review are required. The P0.4 geometry screening result and its 84.20 x 124.31 mm watchdog-PCB envelope are retained without creating fabrication authority.

## Corrected circuit boundary

Electrical V3-P1.13 removes KWD1 and KWD2 from both E-stop return paths:

- channel 1 is `SR1:S11 -> S0:R-1/R-2 -> SR1:S12`;
- channel 2 is `SR1:S21 -> S0:L-1/L-2 -> SR1:S22`;
- the ordinary KWD NO contacts instead form a series gate on `SR1:A1`: `SAFETY_24V -> KWD1:11/14 -> WD_SUPPLY_INTERMEDIATE -> KWD2:11/14 -> SR1_A1_WD_GATED -> SR1:A1`.

KWD1/KWD2 receive zero functional-safety credit. Their gate is a diagnostic availability interlock, not a safety function. A KWD contact or internal fault may defeat heartbeat-based dropout, but the encoded topology no longer connects that fault directly to either E-stop return. Physical conductor separation, terminal construction, internal-fault analysis, protection coordination, endurance, brownout behavior, and fault-injection evidence remain open.

Heartbeat restoration must not command motion. The intended sequence is heartbeat loss, SR1 supply loss, restored heartbeat, physical RESET, physical ARM, and a fresh trajectory. That sequence is not released until controlled tests demonstrate it for every relevant power, reset, watchdog, contactor, controller, and communications state.

## Preliminary contact-load screen

The current Pilz PNOZ s4 750104 technical data lists 2.5 W DC power consumption and a maximum A1 start pulse of 0.5 A for 5 ms. The steady arithmetic screen is `2.5 W / 24 V = 0.10417 A`. Phoenix Contact's published data for candidate 2967060 provides a preliminary current/inrush envelope only. It does not establish contact suitability for this electronic supply load, application endurance, protective coordination, fault current, derating, or service life. Those items require manufacturer-confirmed application evidence and physical measurement before release.

## Package contents

- `panel-bom.csv`: 26 held component or material candidates.
- `backplate-layout.csv`, `door-layout.csv`, and `sidewall-placement.csv`: provisional envelopes only.
- `terminal-allocation.csv`: six non-bridged terminal positions.
- `cable-entry-schedule.csv`: six entries with no holes or gland selections released.
- `stationary-wire-schedule.csv`: 66 V3 wire-number endpoints synchronized to native ECAD, with all physical conductor fields unresolved.
- `thermal-space-screen.csv`: twelve fail-closed space and heat questions.
- `supply-gate-routing-register.csv`: twelve exact topology and segregation controls.
- `panel-layout.svg` and `watchdog-supply-gate.svg`: explanatory views, not manufacturing drawings.

The protection candidates remain held, including Phoenix Contact `PT 4-HESI (5X20)` item `3211861` and `D-ST 4`, item `3030420`, plus Littelfuse `75920-01`. Fuse values and conductor sizes are not released.

## Grounding and physical release boundary

A project-added DC 0 V/PE star point remains prohibited. Protective-earth topology, bonding hardware, conductor sizing, coating removal, torque, verification current, enclosure entry, and jurisdictional review remain unresolved. The manufacturer-defined power-supply output/PE behavior must be verified for the exact received unit before any bonding decision.

This package provides no hole coordinates, cut lengths, drill files, wire cuts, labels for application, fuse values, terminal torque releases, or assembly permission. The qualified electrical reviewer must resolve the open selections, inspect the received components and terminal markings, approve the circuit and physical segregation, and authorize a controlled test plan. Even then, first power must follow the separately approved pre-energization and zero-motion procedures.

**PRELIMINARY - NOT APPROVED FOR FABRICATION OR ENERGIZATION**

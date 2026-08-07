# HR-V0 control-panel physical-definition candidate P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Document ID: `HR-V0-CP-P0.1`

Date: 2026-08-07

Electrical input: `Project Button Electrical V3-P1.4`

Scope: stationary HR-V0 bench control enclosure, backplate, operator door, terminal strip, reserved cable entries, and a source-traceable stationary-wire boundary

## Result

This package converts the connected V3 model into a physical allocation candidate without pretending that unresolved parts or measurements are known. It selects a catalog enclosure/backplate envelope, allocates the current relay/contactor/PCB candidates, proposes a six-position terminal strip, assigns door-device centers, and carries every applicable V3 wire number into a physical-work schedule. It deliberately releases no drilling, cutting, conductor, protection, bonding, cable-entry, PCB-fabrication, assembly, or energization work.

The package is useful now for received-part fit planning, supplier questions, thermal/duct-fill analysis, qualified review, and commissioning-fixture design. It is not a build drawing.

## Controlled artifacts

- `electrical/panel/hr-v0-control-panel-p0.1/panel-bom.csv`: exact catalog candidates and unresolved selections.
- `backplate-layout.csv`: nominal P1868 coordinate allocations, origin at the usable panel's top-left, x right and y down.
- `door-layout.csv`: nominal PJU face coordinates for S0, S1, S2, and H1.
- `terminal-allocation.csv`: proposed physical positions XT1-01 through XT1-06 mapped to V3 `TBD-1` through `TBD-6` and named nets.
- `cable-entry-schedule.csv`: functional entry zones only; every hole and gland is unreleased.
- `stationary-wire-schedule.csv`: the 66 V3 wire-number endpoints for S0/S1/S2/H1/SR1/SRA1/KWD1/KWD2/K1/K2/XT1, with physical conductor fields held `SELECTION REQUIRED`.
- `thermal-space-screen.csv`: ten bounded screens and explicit no-conclusion states.
- `panel-layout.svg`: readable visual view; geometry is controlled by the CSV coordinates rather than SVG scaling.
- `tests/forms/hr-v0-control-panel-receiving-assembly-template.csv`: twenty unexecuted evidence records from receiving through authorization.
- `tools/check_hr_v0_control_panel.py`: fail-closed consistency checks against V3 source tables.

## Exact catalog candidates

The planning envelope uses Hammond `PJU181610H` and steel inner panel `P1868`. The nominal catalog outside enclosure size is 18.30 x 16.52 x 10.13 in, and the panel is 16.875 x 14.875 in (428.625 x 377.825 mm). Series or component ratings do not establish the rating of a drilled, populated, cabled system. Received dimensions, usable depth, cover ribs/inserts, cable entries, installation instructions, and qualified system disposition remain required.

XT1 proposes five gray Phoenix Contact `PT 2,5` item `3209510` terminals, one blue `PT 2,5 BU` item `3209523`, one `D-ST 2,5` item `3030417` end cover, two `CLIPFIX 35` item `3022218` end brackets, and `UCT-TM 5` item `0828734` markers. Proposed DIN rail is `NS 35/7,5 PERF 500MM` item `1207650`; proposed duct stock is `CD 40X40` item `3240189`. These selections establish identity and layout inputs only. They do not establish conductor ampacity, protection, temperature rise, termination method, or code acceptance.

H1 proposes amber IDEC `HW1P-1FQD-A-24V`. The V3 modeled net remains `SR1_STATUS` to `SAFETY_0V`; received terminal identity, polarity and current must be verified before any source connection. The legend is **RESET STAGE READY - DIAGNOSTIC ONLY / NO MOTION AUTHORITY**. H1 must never be described as “safe” or “armed,” and it receives no safety credit.

S0, S1, S2, SR1, SRA1, KWD1, KWD2, K1 and K2 retain the exact V3 candidate identities and holds. In particular:

- S1 and S2 remain `TBD-R1/TBD-R2` and `TBD-A1/TBD-A2` until the received lot is inspected; the panel package does not infer terminal marks.
- KWD1/KWD2 are ordinary diagnostic/watchdog relays with zero functional-safety credit.
- K1/K2 remain blocked on written DC application/critical-current disposition and loaded interruption evidence.
- SR1/SRA1 remain blocked on qualified safety application and validation.

## Layout rules

Coordinates in `backplate-layout.csv` are millimetres from the nominal top-left of P1868. Every current rectangle fits inside the nominal 377.825 x 428.625 mm boundary. That is a planar allocation result only. It does not prove component depth, connector overhang, terminal bend radius, service access, heat, cover closure, fastener edge distance, or received fit.

The lower 270 x 43 mm area is a deliberate selection reserve for `JC1`, `FSR1`, `FSR2`, `F0`, `F1`, `F2`, `F3`, and `SD1`. Its adequacy is not proven. If exact selected devices do not fit with required access and thermal/segregation margins, the enclosure/layout must be revised; the parts must not be squeezed into the reserved zone.

No backplate, enclosure, DIN-rail, duct, or door hole coordinate is released. Device-center coordinates cannot become cutout coordinates until received manufacturer templates, rear-body envelopes, cover construction, tool access, door flex, loom motion, and human-factors review are recorded.

## Wiring boundary

The stationary-wire schedule copies the source fields for the bounded V3 references and adds empty physical fields rather than inventing them. Conductor part number, gauge, insulation/color, measured length, ferrule/lug/contact at both ends, and final route remain `SELECTION REQUIRED`. Closure requires, at minimum:

- source and load current envelopes, fault current and protective-device clearing data;
- each route length, voltage-drop limit, ambient, enclosure temperature, bundling, duty cycle, insulation temperature and jurisdiction;
- connector and terminal conductor ranges, contact ratings, strip length, crimp/tool qualification, pull-test method and replacement rules;
- door-flex, abrasion, minimum-bend-radius, strain-relief, separation and service-loop requirements; and
- exact point-to-point continuity, isolation, polarity, labeling and independent inspection evidence.

XT1 positions are proposed physical labels, not changes to V3 schematic terminal designations. No bridges are proposed. A bridge or commoning accessory may not be added without a schematic/configuration change and exact accessory evidence.

## Cable entries, PE and grounding

`CE-01` through `CE-06` reserve functional zones only. No hole diameter, gland, connector, conduit fitting, cable OD, pullout rating or enclosure-rating claim is released. Cable-entry hardware must be selected only after exact cables and bend/strain requirements are known.

The fiberglass shell does not eliminate protective-bonding questions. The steel backplate, DIN rails, contactor/relay hardware, frame, shields and external Class I source construction require a qualified fault-path and bonding review. The Mean Well GST280A12-C6P source has a documented factory PE/-V relationship in the current design basis. A project-added DC 0 V/PE star point remains prohibited; this package adds none. Exact studs, lugs, conductor, coating preparation, fastener retention, torque and calibrated continuity/impedance limits remain unresolved.

## Thermal and spacing boundary

No enclosure temperature-rise or wire-duct fill result exists because loss, duty, installed wire, ambient and ventilation inputs are incomplete. Before layout release, a qualified reviewer must accept a calculation with component losses and derating and then a powered worst-case soak must verify the received assembly using calibrated instrumentation. Powered testing itself requires the applicable staged authorization; it cannot be performed merely because the layout checker passes.

## Closure sequence

1. Close the exact protection, service-disconnect, JC1, conductor, termination, gland and bonding selections without inventing ratings.
2. Obtain the exact catalog candidates and record received identity, dimensions, terminal marks and mounting templates.
3. Update the layout with received 3D/depth and bend/service envelopes; calculate duct fill and temperature rise.
4. Obtain qualified electrical, mechanical-layout, functional-safety, enclosure-system and human-factors dispositions as applicable.
5. Issue controlled drill/cut/wire/assembly drawings and travelers as a later revision.
6. Fabricate only after a separate written fabrication authorization.
7. Execute 100 percent unpowered inspection, continuity, isolation, polarity, bonding, labeling and fault-readiness evidence.
8. Apply the independent E2 gate and four-role authorization process. A physical panel does not itself authorize energization.

## Primary manufacturer evidence

Manufacturer evidence and access dates are recorded per row in `panel-bom.csv`. The principal official sources are Hammond's PJU series and P1868 pages, Phoenix Contact product pages for `3209510`, `3209523`, `3030417`, `3022218`, `0828734`, `1207650`, and `3240189`, IDEC's current H1/S0/S1/S2 pages/catalog, Pilz order `750104` manual/product data, Schneider catalog `MKTED210011EN`, and the controlled V3/PCB sources. Manufacturer facts establish component candidates only; they are not project application approval.

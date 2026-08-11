# HR-V0 Panel Point-to-Point Candidate P0.1

**PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: `HR-V0-PANEL-P2P-P0.1`

Round: R222

Date: 2026-08-11

System baseline: `HR-30-SYS-R0.2`

## Outcome

R222 converts the R221 one-ended panel endpoint register into an explicit candidate point-to-point topology. The controlled schedule contains 55 physical conductor records, each with exactly one from terminal and one to terminal. All 66 unique R221 endpoint labels are mapped exactly once. The count decreases because eleven previously implicit multi-drop relationships are now represented by explicit distribution or junction hardware rather than by treating every endpoint label as a separate wire.

The candidate native ECAD is `V3-P1.18-PANEL-TOPOLOGY-CANDIDATE`. It preserves the P1.15 control and safety logic and adds physical topology nodes only. P1.15 remains the current system electrical identity until independent review and formal configuration disposition accept or reject P1.18.

## Explicit nodes

| Reference | Candidate item | Modeled use | Unused live positions |
|---|---|---|---|
| `XD24` | Phoenix Contact `PTFIX 6/18X2,5-NS35 RD`, item `3273114` | `SAFETY_24V`: `LINE` plus positions `01..14` | `15..18`; covering and marking remain required |
| `XD0` | Phoenix Contact `PTFIX 6/18X2,5-NS35 BU`, item `3273112` | `SAFETY_0V`: `LINE` plus positions `01..07` | `08..18`; covering and marking remain required |
| `XN1` | Phoenix Contact `PT 2,5-TWIN`, item `3209549` | three-way `SR1_S12` junction | none |
| `XN2` | Phoenix Contact `PT 2,5-TWIN`, item `3209549` | three-way `SRA1_S12` junction | none |
| `XN3` | Phoenix Contact `PT 2,5-TWIN`, item `3209549` | three-way diagnostic `SR1_STATUS` junction | none |

Phoenix Contact's current official records describe items 3273114 and 3273112 as 19-connection NS35 distribution blocks with one line connection and eighteen load connections. The official 3209549 record describes three independent push-in connections. These catalog facts support candidate terminal capacity only. They do not establish Project Button current loading, protection coordination, installed spacing, suitability, acceptance, or functional-safety performance.

## Controlled topology rules

- No logical multi-drop net may be implemented as an undocumented splice or two conductors in one clamp.
- Every physical conductor must keep its controlled `P2P-###` identity from the schedule.
- `XD24` is fed from `F24:OUT`; its R221 loads and watchdog-panel supply interface receive separate positions.
- `XD0` is fed from `J24:3`; its R221 returns and watchdog-panel return interface receive separate positions.
- `XN1`, `XN2`, and `XN3` provide one clamping position per attached conductor.
- The existing `FSR1`/`FSR2`, `JWP1`, and `JWF1` interfaces are represented as explicit opposite ends for formerly single-ended panel records.
- Native ERC 0/0 establishes parser, annotation and connectivity consistency only. It does not validate conductor sizing, terminal application, fault response, separation, stopping performance, or safety integrity.

## Conductor state

Forty-five fixed-internal conductors inherit only the R221 Belden 3057 16 AWG family/gauge candidate. Ten conductors involving `S0`, `S1`, `S2`, or `H1` remain `NO DYNAMIC-FLEX CANDIDATE`. Every exact color/order code, cut length, detailed route, service loop, end preparation, ferrule/lug decision, tool/die, strip length, torque and inspection method remains `SELECTION REQUIRED`.

No DCR, voltage-drop, ampacity, bundle derating, duct-fill, inrush, fault-current, protection-coordination or temperature-rise calculation is released. Those calculations require accepted route lengths, continuous and transient currents, ambient temperature, bundling, conductor temperature rating, connector limits, source impedance/fault current, protective-device characteristics and the applicable Boston/US installation basis.

## Open holds

1. Independent electrical review and formal P1.18 configuration disposition.
2. Project-specific loading and protection coordination for `XD24` and `XD0`.
3. Exact dynamic-flex cable selection and evidence for ten door conductors.
4. Exact conductor colors and order codes.
5. Received-geometry cut lengths, detailed routes, service loops and duct allocation.
6. Direct/ferrule/lug selection, tooling, preparation, torque, inspection and pull testing.
7. DCR, voltage drop, ampacity, bundling, fill and thermal calculations.
8. Accepted rail coordinates, bend/access proof, covers and markers for all five new nodes.
9. Received-device identity, continuity, polarity and accessory reconciliation.
10. Installed point-to-point, pull, label, torque, separation, continuity, polarity, isolation, thermal and fault evidence with qualified review.

## Controlled artifacts

- Native KiCad candidate: `electrical/kicad/project-button-v3-p1.18-panel-topology-candidate/`
- Interactive guide and schedules: `release/hr-v0/panel-point-to-point-p0.1/`
- Gate supplement: `requirements/hr-v0-gate-evidence-supplement-r222.csv`
- Dedicated checker: `tools/check_hr_v0_panel_point_to_point_p01.py`

This artifact is a review candidate. It is not a wire list for shop use and does not authorize procurement, fabrication, assembly, connection, powered testing, motion, or energization.

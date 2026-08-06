# Open Decisions and Release Gates

These questions intentionally remain open. They must be answered with evidence, not guessed during fabrication.

| Gate | Decision | Evidence required | Owner | Due before |
|---|---|---|---|---|
| G-01 | Final J1/J2 actuator and allowable current | CAD mass properties, torque model, single-joint thermal test | mechanical + controls | actuator procurement release |
| G-02 | Custom link/bearing geometry | released CAD, shaft/bearing load calculation, tolerance stack | mechanical | fabrication |
| G-03 | Exact safety-relay and contactor wiring | manufacturer manuals, reviewed ECAD, dropout test plan | electrical safety reviewer | panel wiring |
| G-04 | Fuse types and conductor sizing | measured/inferred fault current, connector ratings, coordination review | electrical | energization |
| G-05 | Guard material/thickness and clearances | swept-volume CAD, stopping-travel test, impact assessment | mechanical safety | integrated motion |
| G-06 | Final software current/temperature limits | T3 characterization data | controls | payload motion |
| G-07 | Receiver fixture sensing method | fault analysis and validation data | systems | handoff test |
| G-08 | Any adult handoff | completed fixture endurance, contact-force assessment, new risk review | independent reviewer | human exposure |
| G-09 | Any child-adjacent use | applicable legal/standards review, qualified safety assessment, guardian/site controls | program owner | child access |
| G-10 | HR-30 locomotion target | **resolved: untethered level-floor walking is required** | program owner | resolved 2026-08-05 |
| G-11 | Final 762 mm external proportions | 1:1 front/side review and full CAD mass properties | industrial design + mechanical | HR-30A CAD freeze |
| G-12 | HR-30A 12 V distribution and safety disconnect | simultaneous-motion model, DC switching ratings, ECAD review | electrical | upper-body procurement |
| G-13 | Full-height restraint and support frame | rated design, proof load, swept-volume review | mechanical safety | HR-30B assembly |
| G-14 | Leg actuator baseline A or B | instrumented primary-joint and complete-leg thermal/impact data | mechanical + controls | leg actuator bulk order |
| G-15 | Foot force sensor architecture | calibrated force and center-of-pressure accuracy at 500 Hz | controls + electrical | double-leg integration |
| G-16 | Real-time balance controller | measured bus timing, estimator latency, deadline-fault response | controls | weight transfer |
| G-17 | HR-30W battery pack | measured gait power, fault current, runtime target, qualified supplier review | electrical safety | untethered test |
| G-18 | Safe power-loss behavior while untethered | fall analysis and validated mitigation independent of high-level software | functional safety | human-facing walking |
| G-19 | Product classification, jurisdiction, and intended users | qualified legal/standards assessment and documented intended-use boundary | program owner + qualified reviewer | procurement and any public operation |
| G-20 | Mass and inertia reserve policy and full-body closure | controlled part-level target/estimate/measured ledger, COM/inertia report, reserve disposition, and independent review | systems + mechanical | HR-30A CAD freeze and leg sizing |
| G-21 | Output-side sensing for every reduced leg joint | selected encoder and mounting, accuracy/error budget, disagreement detection, calibration retention, and full-envelope test | controls + mechanical + electrical | reduced-joint release |
| G-22 | Joint-bus capacity and physical topology | byte-level 250 Hz packet budget, measured worst-case timing/jitter, termination/shielding/isolation design, and fault-injection results | controls + electrical | integrated leg motion |
| G-23 | Full-body response to sudden energy loss | pose-by-pose collapse analysis; selected brake, passive, retained-control, restraint, or other mitigation; measured fault tests | functional safety + mechanical + controls | unrestrained full-body power |
| G-24 | Requirements and risk governance | named owners, rationale, acceptance thresholds, evidence locations, approvers, change history, FMEA/FTA and common-cause review | systems + independent reviewer | design review baseline |

## Inputs needed from Amy

Before the procurement baseline is frozen: available bench/floor footprint and anchoring, budget range, fabrication capabilities (machining/printing), and country of build/use. Overall height is frozen at 762 mm nominal and untethered level-floor walking is a required end-state.

# Open Decisions and Release Gates

These questions intentionally remain open. They must be answered with evidence, not guessed during fabrication.

| Gate | Decision | Evidence required | Owner | Due before |
|---|---|---|---|---|
| G-01 | Final J1/J2 actuator and allowable current | CAD mass properties, torque model, single-joint thermal test | mechanical + controls | actuator procurement release |
| G-02 | Custom link/bearing geometry | R21 corrects the invalid symmetric PCD22 assumption and adds FC01/FC02 plus the expected frame-kit schedule; R22/R23 add stop and moving-mass evidence routes; still requires physical coupon/receiving records, measured mass/COM/inertia, released gripper and hard stops, shaft/frame load calculation, exact fasteners, tolerance stack and proof | mechanical | fabrication |
| G-25 | Watchdog restart interlock | reviewed hardware topology proving heartbeat restoration cannot restore contactor power without monitored physical reset; fault analysis and TEST-SAFE-002 record | functional safety | energization |
| G-26 | Actuator-rail battery architecture | selected chemistry, series count or regulated conversion, full-charge and loaded end-of-discharge bounds, transient/regeneration data, thermal and efficiency evidence | electrical/power | HR-30W design |
| G-27 | Full-body mass feasibility | supplier and measured part-level ledger closing all subsystem allocations, center of mass, inertia, wiring, fasteners, covers, guards, battery/conversion, and contingency | mechanical/systems | actuator procurement |
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

The following program inputs are now frozen:

- Build/use location: Boston, Massachusetts, USA.
- Nominal building supply basis: 120 VAC, 60 Hz. The actual receptacle, branch-circuit protection, grounding, GFCI requirements, and site permission remain to be inspected before any energization.
- HR-V0 use boundary: indoor, bench-mounted experimental machinery operated by adults in a controlled work area. Children are excluded from the build and test area.
- HR-V0 payload: one soft foam object, 100 g maximum and 70 mm maximum characteristic dimension.
- Cost/strength direction: favor a low-cost, low-mass, low-force demonstrator; this does not relax structural proof, guarding, current limiting, stopping, or fault-response requirements.
- Program end-state: 762 mm nominal overall height and untethered level-floor walking, reached only through the staged HR-30 release sequence.

Inputs still required before procurement or fabrication is frozen are: available bench/floor footprint, anchoring permission and substrate, ambient range, exact workshop/site, and budget ceiling. The verified fallback does not require a library metal CNC: flat plates can be quoted online and local makerspaces used for supervised inspection or secondary work. For any library or makerspace CNC, still record the machine make/model, approved materials, work envelope, stock thickness limits, tooling, CAM/file formats, training/certification, attainable tolerance, supervision rules, fees, and whether outside stock is permitted. See [Boston fabrication and sourcing research](hr-v0-fabrication-sourcing-boston.md).

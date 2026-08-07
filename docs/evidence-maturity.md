# Project Button Evidence Maturity

Document ID: HR-EVID-001  
Revision: 0.2  
Program baseline: HR-30-SYS-R0.2  
Status: planning baseline; no release approval

Evidence maturity is recorded separately from design intent. A clean parser, ERC result, simulation, or reviewed concept is not physical validation.

## Maturity scale

| Level | Meaning | Permitted claim |
|---|---|---|
| E0 | requirement or hazard identified | open question only |
| E1 | concept documented and internally checked | design intent |
| E2 | primary-source-backed selection or released calculation | candidate engineering basis |
| E3 | bench or component test passed on the controlled configuration | component evidence |
| E4 | integrated subsystem test passed with fault injection | subsystem evidence |
| E5 | release test passed and independently reviewed | approved capability within the stated operating boundary |

## Current program dashboard

| Domain | Current maturity | Evidence present | Blocking evidence |
|---|---:|---|---|
| HR-V0 configuration control | E1 | `HR-V0-RC-P0.1` product metadata; deterministic all-file SHA-256 manifest; generator/checker; clean-clone route | merged or otherwise accepted exact commit; remote release record; deviation closure; configuration-manager and qualified-review signatures |
| HR-V0 bill of materials | E1 | 70-group system BOM; complete closure classification; 17 exact evaluation-only candidate lines; 13 formerly hidden assembly-dependency groups; receiving quarantine route | 33 selection-required groups; grouped-component expansion; received evidence; exact harness/enclosure/guard/fastener/protection choices; signed hierarchical release BOM |
| HR-V0 electrical connectivity | E2 | connected KiCad V2.1; 15 sheets; 0 ERC errors and 0 warnings; manufacturer source register | qualified electrical and functional-safety review; selected physical parts; fault, stop, and reset tests |
| HR-V0 mechanism | E1 | native quote geometry; separately modeled H101, S102 and selected FR12-H104K candidate interfaces; three hashed fit coupons; proposed orderable gripper parent kit and allocation; hard-stop coordinate, inertia and load-case study; generated guard/catch space envelope and five cable zones; 13-row moving-mass ledger with 565.4 g known and 184.6 g unresolved; unpowered/guarded validation procedures | received-part fit and kit records; released load-path CAD; measured stopping/drop/sweep envelope; exact guard/receiver/harness parts and fasteners; gripper force limit; bearings, shafts, physical hard-stop parts and bumper data; tolerances, measured mass/COM/effective inertia, proof/impact tests |
| HR-30 full-body CAD | E0 | controlled external dimensions and joint inventory | dimensioned assembly, packaging, collision, service, cable, mass, COM, and inertia evidence |
| Leg drivetrain | E1 | candidate actuator and 1.5:1 reduction concept | instrumented joint article; output encoder selection; continuous/cyclic/impact/thermal/backlash tests |
| Foot and IMU sensing | E1 | functional interfaces and sample-rate requirements | complete component circuits, PCB/layout, calibration, overload, saturation, latency, and fault-injection evidence |
| HR-V0 control implementation | E1 | canonical states; portable watchdog C candidate; executable supervisor and actuator-readback models; 25 unit tests; source manifest | received actuator identities; external branch-current envelope; exact interfaces; compiled reproducible binaries; selected kinematics/transport; HIL, deadline, stale-data and reset-to-motion traces; qualified review |
| Safe power-loss response | E0 | hazard and release gate recorded | selected mitigation and pose-by-pose restrained fault evidence |
| HR-30 energy system | E0 | preliminary topology and required protections | chemistry, pack, fault current, contactors, fuses, precharge, charger interlock, enclosure, and test evidence |
| Requirements and risk governance | E0 | 70 draft requirements; 40 open risks; 90 procedure records; traceability links; controlled safety-allocation/FMEA/BOM inputs | accountable owners, qualified PLr/SIL allocation, acceptance thresholds, executed evidence, approvers, change history, complete FMEA/FTA/common-cause review |
| Walking capability | E0 | W0-W5 acceptance definitions | all preceding releases and physical test evidence |

## Release rule

No row advances because a website label changes. Advancement requires a linked evidence artifact for the exact configuration, an identified reviewer, and a controlled change record. The package remains **PRELIMINARY - NOT APPROVED FOR ENERGIZATION**.

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
| HR-V0 bill of materials | E1 | 73-group system BOM; complete closure classification; 16 exact evaluation-only candidate lines; 20 exact candidates on hold including S102 body frames, 20-2040 arm stock/end service, the base frame set, amber H1, Phoenix `3211861` FSR holders and `3030420` end cover; receiving quarantine routes | 29 selection-required groups plus grouped-component expansion; all six fuse links and SD1; received evidence; exact harness/enclosure-application/guard/remaining-fastener/protection choices; signed hierarchical release BOM |
| HR-V0 electrical connectivity | E2 | connected KiCad V2.1; 15 sheets; 0 ERC errors and 0 warnings; manufacturer source register | qualified electrical and functional-safety review; selected physical parts; fault, stop, and reset tests |
| HR-V0 mechanism | E1 | `HR-V0-MECH-P0.3` correction hold; exact-source `HR-V0-ROBOTIS-IF-P0.1`; `HR-V0-ARM-ARCH-P0.4` STEP/GLB/SVG/DXF candidate with explicit transforms, mathematical J1/J2 parallelism, controlled adapter drawing/tolerances, exact material/fastener candidates, ten analytical screens and a 221-pose collision screen; zero active fabrication packets; base five-cut 1980 mm profile schedule; six frame-joint candidates under `HR-V0-FRAME-P0.2`; exact-bench survey/proof procedure | received MTR/FAI and fit; qualified calculation/allowable acceptance; complete received fastener stacks and torque/locking rules; continuous-between-sample collision proof; released hard stop and stopping-overtravel/uncertainty margin below first contact; cable/guard study; slip, fatigue and impact proof; executed bench/frame-joint, mass/COM/inertia, guard/catch and cycle evidence; qualified review |
| HR-30 full-body CAD | E0 | controlled external dimensions and joint inventory | dimensioned assembly, packaging, collision, service, cable, mass, COM, and inertia evidence |
| Leg drivetrain | E1 | candidate actuator and 1.5:1 reduction concept | instrumented joint article; output encoder selection; continuous/cyclic/impact/thermal/backlash tests |
| Foot and IMU sensing | E1 | functional interfaces and sample-rate requirements | complete component circuits, PCB/layout, calibration, overload, saturation, latency, and fault-injection evidence |
| HR-V0 control implementation | E1 | canonical states; portable watchdog C candidate; executable supervisor and actuator-readback models; 25 unit tests; source manifest | received actuator identities; external branch-current envelope; exact interfaces; compiled reproducible binaries; selected kinematics/transport; HIL, deadline, stale-data and reset-to-motion traces; qualified review |
| Safe power-loss response | E0 | hazard and release gate recorded | selected mitigation and pose-by-pose restrained fault evidence |
| HR-30 energy system | E0 | preliminary topology and required protections | chemistry, pack, fault current, contactors, fuses, precharge, charger interlock, enclosure, and test evidence |
| Requirements and risk governance | E0 | 80 draft requirements; 40 open risks; 102 procedure records; traceability links; controlled safety-allocation/FMEA/BOM/mechanical-release/frame-joint/bench-anchor/J2-limit/E2 commissioning inputs | accountable owners, qualified PLr/SIL allocation, acceptance thresholds, executed evidence, approvers, change history, complete FMEA/FTA/common-cause review |
| HR-V0 E2 commissioning | E1 | `HR-V0-E2-SEQ-P0.1`; 15 fail-closed steps; 20 disconnected-load logic cases; five evidence forms; actuator-source-absent invariant; authorization/revocation matrix | accepted as-built configuration; site/PE/insulation and ELV evidence; received devices/harness; calibrated measurements; executed raw traces; four-role signed authorization; qualified electrical and functional-safety dispositions |
| Walking capability | E0 | W0-W5 acceptance definitions | all preceding releases and physical test evidence |

## Release rule

No row advances because a website label changes. Advancement requires a linked evidence artifact for the exact configuration, an identified reviewer, and a controlled change record. The package remains **PRELIMINARY - NOT APPROVED FOR ENERGIZATION**.

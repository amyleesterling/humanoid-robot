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
| HR-V0 bill of materials | E1 | 85-group system BOM; complete closure classification; 17 evaluation-only candidate lines including two S102 body-frame sets; seven-line/nine-article unpowered mechanical subset; 36 exact candidates on hold including the P0.6 enclosure/compute set, R122 USB cable and R123 rail/duct/DR1-DR3 bracket groups; receiving quarantine routes | program-owner purchase approvals; 24 selection-required groups plus grouped-component expansion; residual panel fasteners/holes/DR4 retention/bonding; all six fuse links; received cable/U2D2/Pi-case identity and fit; complete SD1 application; exact remaining harness/guard/fastener/protection choices; shop/physical/electrical/EMC proof; signed hierarchical release BOM |
| HR-V0 electrical connectivity | E2 | connected KiCad V2.1; 15 sheets; 0 ERC errors and 0 warnings; manufacturer source register | qualified electrical and functional-safety review; selected physical parts; fault, stop, and reset tests |
| HR-V0 mechanism | E1 | `HR-V0-MECH-P0.6` integrated hold; `HR-V0-ARM-ARCH-P0.7` STEP/GLB/SVG/DXF candidate with A00-A07 plus HS-J2-POS, a 40,001-pose body sweep, 69-pair continuous body certificate, C06/C07 stop geometry, nominal 117.999985-degree metal contact, sensitivity/load screens and six stop controls; nonselected `HR-V0-MASS-REDUCTION-P0.1` exact-subset study; `HR-V0-GRIP-P0.2` exact-commit official gripper mesh/URDF reference with three checked poses and seven open holds; `HR-V0-GRIP-CAD-ACQ-P0.1` source-state register with two evidence routes and zero measurements; `HR-V0-HS-P0.3`; zero active fabrication packets | complete gripper part definition; H104-to-URDF registration; received opening calibration and mass/COM; guard/receiver/force/drop/cable evidence; bumper selection/characterization; received MTR/FAI/fit; qualified load/contact/tolerance acceptance; mass-study prying/local-bending/notch/fatigue/impact disposition; T-slot and fastener proof; measured contact/stopping/backlash/compliance/uncertainty; cable/guard/as-built collision; J1/J2-negative stops; executed mass/COM/inertia and cycle evidence; qualified review |
| HR-V0 missing-stop regions | E1 | `HR-V0-STOP-REGION-P0.1`; 6,411 sampled boundary poses; 131 continuous pair-region certificates; 5.743912 mm conservative nominal lower bound; 20 open received/interface inputs; three candidate routes remain unselected and two prohibited routes rejected | execute HSI-001..020; select topology only from received evidence; integrated native CAD and drawings; material/fastener/bumper/tolerance/load/fatigue/impact closure; cable/guard sweep; FAI; measured contact/stopping/backlash/compliance/uncertainty; qualified review |
| HR-V0 stopping budget | E1 | `HR-V0-STOP-BUDGET-P0.1`; current J2 narrative/firmware both 15–115 degrees; 3-degree nominal positive-stop approach; 300/100 ms setup/automatic traversal screens; explicit proof that 300 ms `DF-01` detection leaves no downstream margin at 10 degrees/s and exceeds the approach at 30 degrees/s; sixteen blank cases | exact speeds/profiles; missing J1/J2-negative stops; selected bumper; accepted instruments/timebase; synchronized input/output/pole/rail/motion traces; rail-decay threshold; statistical/uncertainty bound; guard reconciliation; PLr/SIL allocation and signed validation |
| HR-30 full-body CAD | E0 | controlled external dimensions and joint inventory | dimensioned assembly, packaging, collision, service, cable, mass, COM, and inertia evidence |
| Leg drivetrain | E1 | candidate actuator and 1.5:1 reduction concept | instrumented joint article; output encoder selection; continuous/cyclic/impact/thermal/backlash tests |
| Foot and IMU sensing | E1 | functional interfaces and sample-rate requirements | complete component circuits, PCB/layout, calibration, overload, saturation, latency, and fault-injection evidence |
| HR-V0 control implementation | E1 | canonical states; portable watchdog C candidate; executable supervisor, actuator-readback and fail-closed DYNAMIXEL transport models; P0.4/P0.3 binding to MECH-P0.6/ARM-P0.7/HS-P0.3 and the 15–115° J2 command/raw-conversion envelope; 47 source tests; pinned SDK adapter and source manifest | accepted as-built stop/stopping/calibration evidence hash; received actuator identities; external branch-current envelope; selected device path, kinematics, calibration, profiles and physical limits; target installation/execution; HIL, deadline, stale-data and reset-to-motion traces; qualified review |
| Safe power-loss response | E1 | `HR-V0-POWERLOSS-P0.1`; passive fixed-guard/receiver/object-catch strategy with zero actuator/software/watchdog credit; controlled 0.750 kg and 0.360 m inputs; 5.295591 J gravitational-only bound; ten strategy rows and seventy-two blank physical cases | exact receiver/catch/guard and bidirectional stops; as-built mass/COM/inertia and continuous collapse/rebound envelope; continued-drive/regeneration/stored-energy/detached-part cases; accepted force/travel/rebound/access limits and uncertainty; physical all-pose evidence and qualified review |
| HR-30 energy system | E0 | preliminary topology and required protections | chemistry, pack, fault current, contactors, fuses, precharge, charger interlock, enclosure, and test evidence |
| Requirements and risk governance | E0 | 81 draft requirements; 40 open risks; 104 procedure records; traceability links; controlled safety-allocation/FMEA/BOM/mechanical-release/frame-joint/bench-anchor/J2-limit/gripper-datum/E2 commissioning/transport-HIL inputs | accountable owners, qualified PLr/SIL allocation, acceptance thresholds, executed evidence, approvers, change history, complete FMEA/FTA/common-cause review |
| HR-V0 E2 commissioning | E1 | `HR-V0-E2-SEQ-P0.1`; 15 fail-closed steps; 20 disconnected-load logic cases; five evidence forms; actuator-source-absent invariant; authorization/revocation matrix | accepted as-built configuration; site/PE/insulation and ELV evidence; received devices/harness; calibrated measurements; executed raw traces; four-role signed authorization; qualified electrical and functional-safety dispositions |
| Walking capability | E0 | W0-W5 acceptance definitions | all preceding releases and physical test evidence |

## Release rule

No row advances because a website label changes. Advancement requires a linked evidence artifact for the exact configuration, an identified reviewer, and a controlled change record. The package remains **PRELIMINARY - NOT APPROVED FOR ENERGIZATION**.

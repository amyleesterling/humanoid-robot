# Preliminary Safety-Function Requirements

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Status: requirements framework only. This document does not assign a required Performance Level, claim a category, claim a Safety Integrity Level, or approve a safety architecture.

## Purpose and limits

This register defines the safety functions that must be analyzed before qualified functional-safety review. It closes the documentation-format gap identified in the independent review; it does not close the engineering work. Required Performance Level (`PLr`) under ISO 13849-1:2023, or an applicable SIL under IEC 62061, remains **ANALYSIS AND SELECTION REQUIRED** for every function. The applicable standards, jurisdiction, machinery classification, intended users, lifecycle boundaries, and validation method also remain to be determined by qualified reviewers.

Fixed shielding, an exclusion boundary, a trained operator, logging, and software diagnostics reduce exposure or support evidence. They do not make an electrical safety function safety-rated. No safety credit is taken for Linux, the Raspberry Pi, the RP2040-class watchdog firmware latch, ROS, network services, website status, or ordinary application software.

## Draft function register

| ID | Hazard and requirement | Required safe response | Initiating inputs and final elements | Restart behavior | Required PLr/SIL | Current status |
|---|---|---|---|---|---|---|
| `SF-01` emergency stop | Crushing, impact, or runaway; `SAFE-001`, `SAFE-002`, `ELEC-002`, R-001/R-003 | Remove actuator-rail energy through both series interruption paths within the validated stopping/clearance budget; compute and safety-control power may remain for diagnostics | Two positively opening NC E-stop channels into proposed PNOZ s4 750104; safety outputs command K1 and K2/KH1 and KH2 | E-stop release cannot restart. EDM healthy, falling-edge physical reset, then a distinct `ARM`; reset and ARM cannot command motion | **ANALYSIS REQUIRED** | Concept is defined. Exact E-stop, contactors, output protection, suppression, wiring, category, and validation are open |
| `SF-02` control-loss/watchdog stop | Stale or uncontrolled motion after supervisor loss; `SAFE-003`, `CTRL-003`, `WALK-008`, R-003/R-020 | Remove actuator-rail energy within the released heartbeat, dropout, and clearance budget | Independent heartbeat monitor and hardware restart interlock; two series contactors are the final energy-removal elements | Heartbeat restoration, reboot, or software fault clearing cannot restore either coil. Physical reset and a later distinct physical `ARM` are both required | **ANALYSIS REQUIRED** | V2.1 remains blocked. Corrected V3-P1.0 nominally opens both SR1 input returns on watchdog dropout, then requires black RESET and distinct green ARM. It adds exact optical heartbeat, separate ordinary driver packages, proposed feedback-passive identities and an explicitly unrouted PCB-P0.1 placement/interface source, but received proof and derating, RESET/ARM terminals, panel human factors, routed PCB/stack-up, protection/conductors, current-division/thermal/brownout, COM-slew, welded-contact behavior, timing, fault tolerance, common-cause analysis and HIL validation remain open; firmware and ordinary interface parts receive no safety credit |
| `SF-03` prevention of unexpected restart and external-device monitoring | Motion or re-energization during reset/maintenance; `SAFE-008`, `ELEC-002`, R-001/R-030 | Keep contactors and torque inhibited when feedback is inconsistent, a contactor is welded, reset is invalid, or state/order is wrong | Falling-edge RESET path, separate falling-edge ARM/EDM path, K1/K2 normally closed mirror contacts, and fail-closed non-safety supervisor authority model | Cause removal -> watchdog contacts healthy -> accepted physical RESET -> `SAFE_READY` with coils inhibited -> distinct physical `ARM` -> fresh validated command; no stale target resumes | **ANALYSIS REQUIRED** | V3 and FW-P0.1 now model the sequence, but protected routing, fault exclusions, mirror-contact validity, compiled code, HIL and qualified validation are open |
| `SF-04` prevention of access to hazardous motion | Access to arm/leg pinch, impact, and fall zones; `SAFE-004`, `SAFE-005`, `WALK-010`, R-001/R-008/R-016 | Prevent exposure while hazardous motion or fall energy is available | V0 fixed shield and controlled exclusion boundary; HR-30 guarded cell and restraint concept | Access occurs only after verified energy isolation and the applicable maintenance/lockout procedure | **ANALYSIS REQUIRED if credited** | Current measures are physical/administrative and no interlocked guard safety function is selected. If an access interlock is required, device, architecture, reset, and validation are **SELECTION REQUIRED** |
| `SF-05` drive-energy-loss and fall response | Collapse, toppling, or hazardous arrest after E-stop/power loss; `SAFE-009`, `WALK-011`, `WALK-012`, R-013/R-016/R-017/R-021 | Reach a pose-specific protective state or contain the fall without exceeding released human-exclusion, structural, head/tool, restraint, and contact-energy limits | Drive-energy state, estimator/fall inputs, selected brakes/counterbalances/ride-down or accepted-fall design, and engineered restraint through gated phases | Recovery requires inspection, restraint confirmation, physical reset, distinct `ARM`, and a fresh pose/trajectory | **ANALYSIS REQUIRED** | **BLOCKER for untethered walking:** the unbraked geared-joint collapse path is uncharacterized and the safe state is not yet selected |
| `SF-06` charge/motion incompatibility | Charging fault, high-current fault, or motion while charger is connected; `WALK-009`, `SAFE-009`, R-018/R-032/R-033 | Inhibit actuator-power enable while the charge connection/state is present and prevent charging outside the selected pack/BMS limits | Charge-presence interface, pack/BMS, charger, service disconnect, source contactors, and independent interlock | Removing the charger does not initiate enable; normal reset and `ARM` sequence is still required | **ANALYSIS REQUIRED if credited** | Battery chemistry, pack, BMS, charger, connector, interlock circuit, diagnostics, and validation are **SELECTION REQUIRED** |

## Analysis required before architecture release

For each function, the qualified review shall record:

1. hazard boundaries, operating modes, foreseeable misuse, severity, exposure frequency/duration, possibility of avoidance, and the resulting `PLr` or applicable SIL target;
2. the complete sensor/logic/final-element boundary, energy sources, stop category, safe state, response-time budget, and restart behavior;
3. claimed architecture/category, subsystem MTTFd or reliability data, diagnostic coverage, common-cause-failure measures, environmental assumptions, mission time, and proof-test/maintenance intervals;
4. every fault exclusion with engineering justification, especially protected routing of the PNOZ `S12 -> reset -> EDM -> S34` loop, which the device does not monitor for shorts or cross-shorts;
5. dependent failures involving common 24 V supply, common enclosure, shared terminals, coil suppression, contact welding, software/firmware, grounding, EMC, communication, and mechanical final elements;
6. calculation files and manufacturer evidence tied to exact order codes and document revisions; and
7. validation procedures, acceptance limits, traceable measurements, injected faults, reviewer independence, and residual-risk disposition.

Selecting a PL e-capable component does not establish a PL e function. A clean ERC, successful schematic parse, or passing nominal motion test is not functional-safety validation.

## Immediate release blockers

- Independently review, select and validate the corrected Electrical V3 watchdog-in-SR1-return architecture; prove that heartbeat restoration cannot restore SR1 before physical RESET or SRA1/K1/K2 before distinct physical ARM, including welded-contact and common-cause faults.
- Derive the stopping/clearance budget from released CAD and measure the complete sensor-to-energy-removal-to-motion-stop time.
- Select exact E-stop, contactors/mirror contacts, output protection, coil suppression, terminals, conductors, and protected routing; then update ECAD and all synchronized schedules.
- Select and validate the HR-30 response to sudden drive-energy loss for every released pose before reducing restraint dependence.
- Complete the PLr/SIL risk determination and the architecture, diagnostic, CCF, reliability, and fault-exclusion calculations for every credited safety function.

Until those items close, this package is not approved for fabrication, energization, functional-safety acceptance, or operation around people or children.

# Preliminary Safety-Function Requirements

> **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Status: requirements framework only. This document does not assign a required Performance Level, claim a category, claim a Safety Integrity Level, or approve a safety architecture.

## Purpose and limits

This register defines the safety functions that must be analyzed before qualified functional-safety review. It closes the documentation-format gap identified in the independent review; it does not close the engineering work. Required Performance Level (`PLr`) under ISO 13849-1:2023, or an applicable SIL under IEC 62061, remains **ANALYSIS AND SELECTION REQUIRED** for every function. The applicable standards, jurisdiction, machinery classification, intended users, lifecycle boundaries, and validation method also remain to be determined by qualified reviewers.

Fixed shielding, an exclusion boundary, a trained operator, logging, and software diagnostics reduce exposure or support evidence. They do not make an electrical safety function safety-rated. No safety credit is taken for Linux, the Raspberry Pi, the RP2040-class watchdog, its firmware, relay drivers, ordinary relays, bus watchdog, ROS, network services, website status, or ordinary application software. R44 freezes the current allocation boundary in `docs/hr-v0-functional-safety-allocation-p0.1.md` and `safety/hr-v0-safety-function-allocation.csv`.

## Draft function register

| ID | Hazard and requirement | Required safe response | Initiating inputs and final elements | Restart behavior | Required PLr/SIL | Current status |
|---|---|---|---|---|---|---|
| `SF-01` emergency stop | Crushing, impact, or runaway; `SAFE-001`, `SAFE-002`, `ELEC-002`, R-001/R-003 | Remove actuator-rail energy through both series interruption paths within the validated stopping/clearance budget; compute and safety-control power may remain for diagnostics | Two positively opening NC E-stop channels into proposed PNOZ s4 750104; safety outputs command K1 and K2/KH1 and KH2 | E-stop release cannot restart. EDM healthy, falling-edge physical reset, then a distinct `ARM`; reset and ARM cannot command motion | **ANALYSIS REQUIRED** | Concept is defined. Exact E-stop, contactors, output protection, suppression, wiring, category, and validation are open |
| `SF-02` future safety-rated control-loss stop | Control loss where assumed ordinary-diagnostic failure can expose a person; `SAFE-003`, `WALK-008`, R-003/R-020 | Reach the qualified safe state within the released response and clearance budget | **SELECTION REQUIRED** safety-rated initiator, logic and final elements | Cause removal, inspection, safety reset, distinct `ARM`, and fresh command | **PLr/SIL SELECTION REQUIRED** | Not selected. Required for HR-30 and for any HR-V0 configuration whose released fixed guard cannot contain the assumed control-loss case |
| `DF-01` ordinary HR-V0 heartbeat diagnostic | Equipment protection and diagnostic stop demand after supervisor loss; `CTRL-003`, `CTRL-007`, R-003 | Nominally demand SR1/K1/K2 dropout; failure to operate is assumed in the safety assessment | Raspberry Pi heartbeat, ordinary RP2040 firmware/drivers/relays, SR1 demand path | Restoration cannot bypass physical RESET and later physical ARM | **NO SAFETY CREDIT** | V3 nominal topology and source exist. Physical timing, routing, stuck-contact/brownout/common-cause tests and proof that faults cannot impair `SF-01`/`SF-03` remain open. Fixed guard and hard stops must contain motion with this diagnostic failed |
| `SF-03` prevention of unexpected restart and external-device monitoring | Motion or re-energization during reset/maintenance; `SAFE-008`, `ELEC-002`, R-001/R-030 | Keep contactors and torque inhibited when feedback is inconsistent, a contactor is welded, reset is invalid, or state/order is wrong | Falling-edge RESET path, separate falling-edge ARM/EDM path, K1/K2 normally closed mirror contacts, and fail-closed non-safety supervisor authority model | Cause removal -> accepted physical RESET -> `SAFE_READY` with coils inhibited -> distinct physical `ARM` -> fresh validated command; no stale target resumes | **PLr/SIL SELECTION REQUIRED** | V3 and FW-P0.1 model the sequence, but allocation, protected routing, fault exclusions, mirror-contact application evidence, HIL and qualified validation are open. `DF-01` dropout may enter this sequence but receives no safety credit |
| `PG-01` fixed physical guard and receiver | Access to HR-V0 pinch, impact and drop zones with `DF-01` failed; `SAFE-004`, `SAFE-010`, R-001/R-002/R-003 | Prevent exposure and contain arm/payload travel | Tool-removable fixed guard, receiver/catch, bench anchor and controlled exclusion boundary | Access only after verified energy isolation and maintenance control | **NOT AN SRP/CS** | Exact panels/frame/fasteners, access prevention, worst-case sweep/stop/drop envelope, impact/retention proof and qualified review remain open |
| `SF-04` future interlocked access prevention | Access to arm/leg pinch, impact, and fall zones; `SAFE-005`, `WALK-010`, R-001/R-008/R-016 | Prevent exposure while hazardous motion or fall energy is available | **SELECTION REQUIRED** if a movable/interlocked guard is required | Access only after verified energy isolation and the applicable maintenance/lockout procedure | **PLr/SIL SELECTION REQUIRED if required** | No interlocked guard safety function is selected. A fixed guard remains a physical measure; any movable guard requires a new allocation and validation |
| `SF-05` drive-energy-loss and fall response | Collapse, toppling, or hazardous arrest after E-stop/power loss; `SAFE-009`, `WALK-011`, `WALK-012`, R-013/R-016/R-017/R-021 | Reach a pose-specific protective state or contain the fall without exceeding released human-exclusion, structural, head/tool, restraint, and contact-energy limits | Drive-energy state, estimator/fall inputs, selected brakes/counterbalances/ride-down or accepted-fall design, and engineered restraint through gated phases | Recovery requires inspection, restraint confirmation, physical reset, distinct `ARM`, and a fresh pose/trajectory | **ANALYSIS REQUIRED** | **BLOCKER for untethered walking:** the unbraked geared-joint collapse path is uncharacterized and the safe state is not yet selected |
| `SF-06` charge/motion incompatibility | Charging fault, high-current fault, or motion while charger is connected; `WALK-009`, `SAFE-009`, R-018/R-032/R-033 | Inhibit actuator-power enable while the charge connection/state is present and prevent charging outside the selected pack/BMS limits | Charge-presence interface, pack/BMS, charger, service disconnect, source contactors, and independent interlock | Removing the charger does not initiate enable; normal reset and `ARM` sequence is still required | **ANALYSIS REQUIRED if credited** | Battery chemistry, pack, BMS, charger, connector, interlock circuit, diagnostics, and validation are **SELECTION REQUIRED** |

## Analysis required before architecture release

For each function, the qualified review shall record:

1. hazard boundaries, operating modes, foreseeable misuse, severity, exposure frequency/duration, possibility of avoidance, non-control risk reduction, and the resulting `PLr` or applicable SIL target for each credited SRP/CS;
2. the complete sensor/logic/final-element boundary, energy sources, stop category, safe state, response-time budget, and restart behavior;
3. claimed architecture/category, subsystem MTTFd or reliability data, diagnostic coverage, common-cause-failure measures, environmental assumptions, mission time, and proof-test/maintenance intervals;
4. every fault exclusion with engineering justification, especially protected routing of the PNOZ `S12 -> reset -> EDM -> S34` loop, which the device does not monitor for shorts or cross-shorts;
5. dependent failures involving common 24 V supply, common enclosure, shared terminals, coil suppression, contact welding, software/firmware, grounding, EMC, communication, and mechanical final elements;
6. calculation files and manufacturer evidence tied to exact order codes and document revisions; and
7. validation procedures, acceptance limits, traceable measurements, injected faults, reviewer independence, and residual-risk disposition.

Selecting a PL e-capable component does not establish a PL e function. A clean ERC, successful schematic parse, or passing nominal motion test is not functional-safety validation.

## Immediate release blockers

- Execute `ANALYSIS-SAFE-001` to allocate PLr/SIL only to credited functions. Keep `DF-01` at zero safety credit; prove through `ANALYSIS-SAFE-002` that its open, short, welded, cross-channel, shared-supply and contamination faults cannot impair `SF-01` or `SF-03`.
- Release `PG-01` against the maximum motion/stopping/drop envelope with `DF-01` failed, or select and validate `SF-02` before any configuration that can expose a person.
- Derive the stopping/clearance budget from released CAD and measure the complete sensor-to-energy-removal-to-motion-stop time.
- Select exact E-stop, contactors/mirror contacts, output protection, coil suppression, terminals, conductors, and protected routing; then update ECAD and all synchronized schedules.
- Select and validate the HR-30 response to sudden drive-energy loss for every released pose before reducing restraint dependence.
- Complete the PLr/SIL risk determination and the architecture, diagnostic, CCF, reliability, and fault-exclusion calculations for every credited safety function.

Until those items close, this package is not approved for fabrication, energization, functional-safety acceptance, or operation around people or children.

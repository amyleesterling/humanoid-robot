# Independent Review Disposition - Sol Pass

Review received: 2026-08-05  
Disposition revision: 0.2  
Authority: this repository  
Status: preliminary; no approval for fabrication or energization

## Already closed in electrical V2.1

The independent review inspected an older package in several places. These items were already corrected before this disposition:

- the obsolete PNOZ X2.8P entry was replaced by the proposed PNOZ s4 750104 record;
- unverified fuse values were removed and remain `SELECTION REQUIRED`;
- safety-output protection and contactor-coil suppression placeholders were added without inventing ratings;
- U2D2 pin 2 is no longer described as a sense input and is omitted from the required custom data harness;
- the U2D2 Power Hub is not used to carry summed actuator current;
- native KiCad 10.0.5 parsing and ERC complete with 0 errors and 0 warnings, with the explicit warning that passive functional blocks and ERC do not establish safety or buildability.

## Accepted in this correction pass

| Review finding | Disposition | Controlled correction |
|---|---|---|
| sudden power loss can collapse the robot | accepted as a blocker | requirements `SAFE-009`; gates `G-18` and `G-23`; risks `R-013`, `R-017`, `R-021`, and `R-039`; expanded fault testing |
| 17.6 N.m wording can be misread | accepted | walking specification and website now say ideal, momentary, zero-speed reduced stall; not continuous, thermally sustainable, or impact-rated |
| reduced joints need output sensing | accepted as baseline, part unresolved | `WALK-013` and `G-21`; exact encoder and safety role remain `SELECTION REQUIRED` |
| mass and inertia are not closed | accepted | controlled target/estimate/measured ledger required by `MASS-001` and `G-20` |
| character rig is not mechanical CAD | accepted | evidence dashboard labels HR-30 CAD E0 and preserves the rig as packaging/reference context only |
| sensor pages are functional blocks | accepted | evidence dashboard keeps sensing at E1; complete circuits and PCB evidence remain required |
| timing descriptions need one contract | accepted | canonical multi-rate schedule and message metadata added by `CTRL-005` and `WALK-014` |
| requirements and risk governance are incomplete | accepted as a blocker | `GOV-001`, `G-24`, and the evidence dashboard require owners, thresholds, evidence, approvers, history, and structured hazard analysis |
| operating boundary is ambiguous | accepted with qualification | project rule states adult-operated experimental robotic machinery, not a toy, while legal classification remains unresolved at `G-19` |
| running reference is outside scope | accepted | running animation removed from the public rig explorer; source reference retained as provenance only |

## Requires selection or test evidence

The review does not justify selecting a brake, counterbalance, passive knee, retained-control architecture, encoder, RS-485 isolator, bus split, battery, fuse, conductor, contactor configuration, or safety performance level. Those remain controlled decisions. A specific solution enters the baseline only after calculations, primary manufacturer evidence, configuration-controlled drawings, and the applicable component, subsystem, and fault tests.

## Review readiness

The correction makes the system boundaries and missing evidence clearer. It does not make the package ready for fabrication or energization. It is suitable for another qualified electrical, mechanical, controls, and functional-safety review after owners and evidence plans are assigned.

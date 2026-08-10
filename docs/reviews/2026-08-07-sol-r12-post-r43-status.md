# Sol R12 status after R43 flat-plate manufacturing control

Status: **PROJECT-OWNED RECONCILIATION—NOT AN INDEPENDENT REVIEW OR APPROVAL**

Date: 2026-08-07

Baseline reviewed by Sol: the R12 pre-correction configuration

Current correction: R43 / `HR-V0-PLATE-RFQ-P0.1`

## What R43 changes

R43 narrows the custom-flat-plate portion of Sol finding `B-003` without closing it:

- adds a machine-checked process register for all four custom part numbers;
- corrects `MV0-001`, `MV0-002`, and `MV0-003` from generic profile-cut candidates to CNC mill/drill RFQ parts because their 2.70 mm candidate holes are smaller than the 4.75/6.35 mm stock;
- holds `MV0-004` behind the real Boston bench survey;
- adds readable RFQ process, no-bend/no-weld, do-not-scale, unresolved-tolerance and FAI notes to every drawing;
- adds a controlled supplier DFM/first-article record and `INSPECT-MECH-009`; and
- links the process package into energization gate `EG-006`, which remains partial.

The correction uses current SendCutSend, Xometry and Protolabs process documentation as RFQ screening evidence. It does not treat a web capability statement as application approval.

## Finding disposition

| Sol finding | R43 status | What remains |
|---|---|---|
| `B-003` no buildable HR-V0 mechanical definition | **Narrowed; open** | Received ROBOTIS hardware, executed coupons, selected hole/location tolerances, exact fasteners, supplier DFM, separately authorized first articles, executed FAI, hard stops, guard, receiver, cable path, bench anchors, measured mass/COM/inertia, proof tests and qualified mechanical review. |
| `M-004` mechanical calculations absent | **Unchanged; open** | Final fastener/interface/load calculations must use the physically verified geometry and material/first-article evidence. |
| `M-006` cable routing lacks geometric verification | **Unchanged; open** | Full routed sweep, bend/twist, clamp, abrasion, strain-relief and endurance evidence. |
| `M-007` guard definition incomplete | **Unchanged; open** | Exact panel/frame/fastener construction, stopping/drop envelope and physical tests. |

All other R12 BLOCKER, MAJOR and MINOR findings retain their previous dispositions. R43 releases no process tolerance, cutting order, production quantity, structural acceptance, functional-safety credit or permission to energize.

## Current verdict

- **HR-V0 fabrication readiness:** not ready. The RFQ/FAI route is controlled, but physical inputs and qualified release are absent.
- **HR-V0 energization readiness:** prohibited. No energization gate closes in R43.
- **HR-30W walking feasibility:** unchanged; physically plausible but not demonstrated.
- **Qualified mechanical review readiness:** improved for the flat-plate process question, but not ready for final sign-off.

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

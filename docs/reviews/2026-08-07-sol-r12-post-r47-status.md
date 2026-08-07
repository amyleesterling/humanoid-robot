# Sol R12 status after R47 mechanical-release coordination

Status: **PROJECT-OWNED RECONCILIATION—NOT AN INDEPENDENT REVIEW OR APPROVAL**

Date: 2026-08-07

Baseline reviewed by Sol: the R12 pre-correction configuration

Current correction: R47 / `HR-V0-MECH-P0.2`

## What R47 changes

R47 advances mechanical configuration completeness without claiming that physical build evidence exists:

- creates a 24-row controlled mechanical parameter contract;
- creates a 12-interface mounting/fastener register and 19-group assembly schedule tied to the system BOM;
- freezes five exact candidate `40-4040` profile cuts totaling 2140 mm;
- defines one six-datum neutral assembly chain from the bench plane through J1, J2, the gripper frame and 360 mm reach ceiling;
- corrects the native assembly-space transforms and rotates the candidate anchor plates into the bench plane;
- adds a generated web-readable general-arrangement SVG and unexecuted inspection route; and
- removes four structural STL files after regeneration proved that distinct link interfaces produced byte-identical meshes. Structural custom parts now require DXF/STEP only.

## Sol finding disposition

| Finding | R47 status | Remaining evidence |
|---|---|---|
| No buildable mechanical definition | **Materially advanced; still open** | One datum/interface contract and general arrangement now exist, but every fit coupon, final tolerance, fastener, stop, guard, catch, cable and anchor boundary still requires closure. |
| Missing dimensioned assembly and fabricated-part chain | **Assembly chain defined; fabrication still prohibited** | Exact extrusion cuts are controlled; custom plates remain RFQ/first-article candidates pending received fit, supplier DFM, material certificates and FAI. |
| Mass/COM/inertia and load-path closure absent | **Unchanged in outcome** | No received moving item has been weighed; fasteners, stops, harness and gripper mechanism remain unresolved; proof and impact evidence do not exist. |
| Guard, stopping and power-loss containment unproven | **Unchanged in outcome** | The 900 x 400 x 950 mm guard remains a space reservation, not a safety distance. Physical sweep, stopping, access-probe, drop and retention evidence remain mandatory. |

## Current verdict

- **HR-V0 fabrication readiness:** not ready.
- **HR-V0 mechanical review readiness:** improved configuration clarity; physical evidence and exact selections remain incomplete.
- **HR-V0 energization readiness:** prohibited.
- **E1 mechanical gates:** `EG-005` through `EG-008` remain partial.
- **E2 gate status:** 0 closed, 16 partial, 5 open; all 21 applicable gates remain unresolved.

The P0.2 automated checker validates repository agreement only. The SVG passed XML structure, warning, required-dimension and minimum 14 px text checks. Browser rendering of the local `file:` artifact was blocked by browser policy and is not claimed as completed visual approval.

R47 issues no cutting order, assembly release, structural proof, safety approval or permission to energize.

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION.**

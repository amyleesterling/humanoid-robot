# HR-V0 J2 positive hard-stop design basis P0.3

> **PRELIMINARY—CANDIDATE GEOMETRY ONLY—NOT APPROVED FOR QUOTATION, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION.**

Date: 2026-08-07

Mechanical candidate: `HR-V0-MECH-P0.6`

Arm candidate: `HR-V0-ARM-ARCH-P0.7`

Stop candidate: `HR-V0-J2-STOP-P0.1`

Requirements: `SAFE-007`, `MECH-006`

## R69 result

P0.3 supersedes P0.2. It retains the unreleased J2 software/metal-stop allocation of `115/118 deg` and replaces the missing positive-stop geometry with an analytical twin-rail CAD candidate:

- `MV0-C06` is the moving forearm adapter and provides two outside metal striker rails;
- `MV0-C07` is the fixed upper-link adapter and provides two recessed metal catch rails;
- the rails lie outside the XM540 case and transfer load through the metal adapters and member/frame joints;
- nominal first metal contact is `117.999985 deg`;
- nominal metal clearance at the `115 deg` software ceiling is `1.072358 mm`;
- the maximum reserved, undeformed `0.75 mm` bumper envelope retains `0.322358 mm` nominal clearance at `115 deg` and first contacts at `115.861085 deg`; and
- the existing non-stop body pair retains `2.114900 mm` nominal clearance at metal-stop contact.

The bumper envelope is a space claim, not a selected part. Bumper material, manufacturer, order code, retention, force/stroke curve, energy capacity, temperature range, aging, life and replacement rule remain **SELECTION REQUIRED**.

## Nominal allocation

| Boundary | Candidate value | Release effect |
|---|---:|---|
| software ceiling | `115.000000 deg` | configuration candidate; not released |
| maximum bumper-envelope contact | `115.861085 deg` | nominal CAD result for the unselected maximum envelope |
| positive metal contact | `117.999985 deg` | analytical CAD result; target `118 deg` |
| continuous nominal body contact | `121.643289 deg` | numerical model result; not an as-built limit |
| software-to-metal allowance | `3.000000 deg` | must contain every accepted stopping case |
| metal-to-body-contact separation | `3.643289 deg` | nominal separation before physical uncertainty |
| reserved nominal collision guard | `1.000000 deg` | may not be consumed |
| candidate physical-uncertainty budget | `2.643289 deg` | maximum combined stack before additional qualified margin |

The geometry sensitivity screen varies the striker height by `±0.025 mm` and the catch-face recess by `±0.05 mm`. The largest modeled change is `0.150397 deg`. This is not a complete tolerance stack and releases no angle.

## Load-screen boundary

The load register evaluates three inputs: the project proof-screen moment, the RAW 800 ideal stall-line screen, and the published 12 V momentary stall endpoint. It assumes two equal rails and omits impact amplification, reflected rotor inertia, prying, notches, fatigue, local contact stress and unequal sharing. The output is therefore an indicative demand screen only; it is not a material allowable, structural release, life prediction or permission to drive into the stop.

The kinetic-energy entries use the allocated link inertia excluding reflected rotor inertia. They are not complete impact-energy results.

## Evidence required before release

1. Select and receive the exact bumper and retention hardware; characterize force/stroke, energy, rebound, temperature, aging and life.
2. Obtain supplier DFM, MTR and first-article evidence for C06/C07; inspect all `STOP-001..006` controls.
3. Close the complete dimensional stack from actuator/frame/link receipt through both stop faces and encoder calibration.
4. Complete qualified load, contact, prying, fatigue, impact, parent-structure and fastener analysis using accepted allowables.
5. Prove cable, guard and access clearance across the full stopping and tolerance envelope.
6. Measure contact angle, backlash, compliance, coast/drive persistence and stopping overtravel in a guarded single-axis fixture at every proposed speed, payload, temperature, voltage and fault case.
7. Demonstrate both allocation inequalities with measurement uncertainty and retain high-speed video, synchronized position/current/voltage data and post-test inspections.
8. Obtain signed mechanical and functional-safety dispositions for the exact configuration.

## Controlled evidence

- `cad/hr-v0/generated/arm-architecture-p0.7/j2-positive-stop-analysis.json`
- `cad/hr-v0/generated/arm-architecture-p0.7/j2-positive-stop-sweep.csv`
- `cad/hr-v0/generated/arm-architecture-p0.7/j2-positive-stop-tolerance-screen.csv`
- `cad/hr-v0/generated/arm-architecture-p0.7/j2-positive-stop-load-screen.csv`
- `cad/hr-v0/generated/arm-architecture-p0.7/j2-positive-stop-controls.csv`
- `cad/hr-v0/generated/arm-architecture-p0.7/HR-V0_J2_positive_stop_contact_candidate.step`
- `cad/hr-v0/generated/arm-architecture-p0.7/HR-V0_J2_positive_stop_contact_candidate.glb`
- `tests/forms/hr-v0-j2-limit-stop-template.csv`

J1 minimum/maximum and J2-negative physical stops remain `DESIGN REQUIRED`. No source in this package authorizes fabrication, motion or energization.

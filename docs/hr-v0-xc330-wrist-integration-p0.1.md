# HR-V0 source-bound XC330 wrist integration P0.1

> **PRELIMINARY WRIST-INTEGRATION CANDIDATE - NOT SELECTED - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: **HR-V0-XC330-WRIST-P0.1**
Round: **R192**
Date: 2026-08-10

## Disposition

R192 connects the nonselected `HR-V0-GRIP-XC330-P0.2` branch to the controlled `HR-V0-ARM-ARCH-P0.7` coordinate chain using exact ROBOTIS H104, XC330 and FPX330 geometry plus two project-owned bridge candidates. It does not select XC330, change `GRIP-002`, replace the active XM430 baseline, or release any part.

The nominal gripper-to-H104 transform is Rx +90 degrees with translation `(0, 4.0, 13.5)` mm. Composed with the controlled H104 world transform, the gripper root is Rx 270 degrees at `(0, 327.6, -13.5)` mm. The retained nominal pad/object datum is `(0, 358.6, -13.5)` mm in world coordinates, 1.4 mm inside the prior 360 mm reach-reserve plane.

This is a coordinate and nominal-geometry result—not proof of delivered reach, fit, tolerance, stiffness, strength, payload, collision-free continuous motion, cable behavior, guarding, or physical performance.

## H104 evidence

The archived manufacturer H104 sources are:

| Record | Date/status | Size | SHA-256 |
|---|---|---:|---|
| `FR12-H104K.stp` | controlled retrieval; drawing family dated 2017-08-31 | 229,070 bytes | `75BA58D2668D7D25802D1277A5393445C4FB7A8C565566E56CE76FEFC0E59F7D` |
| `FR12-H104K.pdf` | 2017-08-31; **FOR REFERENCE ONLY** | 72,806 bytes | `3FA377719C8FAA1235054D76D0913511A4EB37FBA746C60392385E40BE18E5B0` |

The STEP imports as one solid with aggregate bounds X `-20.5..20.5`, Y `-2.5..28.0`, Z `-11.25..35.25` mm and volume 4,314.613722 mm3. The reference drawing labels a 38 mm inside width, 1.5 mm side stock and four M2 taps. The exact STEP minor-cylinder axes used by the candidate are parallel to X at H104 `(y=22.5, z=+/-8.0)` mm on both sides; represented minor diameter is 1.567 mm. These are source observations only. Received threads, acceptance limits, engagement and fasteners remain open.

The current ROBOTIS e-Manual lists FR12-H104K as an XL/XC-series back-mount frame and links the manufacturer drawing and STEP source: https://emanual.robotis.com/docs/en/dxl/x/xc430-w240/

## Bridge candidates

Two mirrored project-owned bridge parts span the 3.0 mm nominal side gap between the existing P0.2 U-base ears and H104 inner faces. Each has a 3.0 x 20.0 x 31.5 mm envelope and 1,821.576112005 mm3 modeled volume.

The bridge holes represent:

- two H104-side 2.20 mm candidate clearances per bridge at the observed M2 tap axes; and
- four transformed S101/U-base PCD16-axis 2.20 mm candidate clearances per bridge.

Every screw, nut, washer, length, head, tool access, engagement, seating, torque, locking and reuse rule remains `SELECTION REQUIRED`. The 6061-family 2.70 g/cm3 value is only a screening density. Exact stock, alloy, temper, MTR, finish, grain direction, machining process, tolerances, FAI and acceptance remain held.

## Nominal geometry screens

Closed, mid and open gripper poses reproduce zero positive-volume intersection against the exact H104 and zero nominal minimum distance at the intentional mounting contact. Each bridge similarly shows zero positive-volume intersection and zero distance at the intended H104 and U-base faces.

The arm screen sampled J1 `-20..70` degrees and J2 `15..115` degrees at endpoint-aligned 5-degree increments: 399 joint pairs. The new wrist components produced zero positive-volume intersections against the controlled P0.7 fixed and upper bodies in those samples.

This screen excludes every between-sample pose, tolerance, cable, guard, deformation, backlash, received variation and physical motion. It is not a continuous collision proof or permission to move hardware.

## Incomplete mass screen

The two full-density bridge candidates add 9.836511 g to the R191 incomplete subtotal:

`679.124713 + 9.836511 = 688.961224 g`

Incomplete headroom to the retained 750 g screen is 61.038776 g. H104, FPX frames, all hardware, cable, strain relief, guard/bellows and physical variation remain excluded. Therefore moving mass, COM and inertia remain open.

## Configuration conflict and open evidence

`GRIP-002` still names the controlled OpenMANIPULATOR mechanism path. Selecting this branch requires a formal requirement/configuration disposition and synchronized mechanical, electrical, firmware, BOM, mass and verification updates. The active moving-mass ledger intentionally still names XM430.

All 18 `WRI-Hxx` holds remain open. R192 closes zero requirements, zero energization gates and zero Sol R12 blockers. It does not change Sol's verdict: HR-V0 is not build-ready; energization is prohibited; HR-30W remains plausible but unproved.

## Artifacts

- Generator: `tools/generate_hr_v0_xc330_wrist_integration_p01.py`
- Independent checker: `tools/check_hr_v0_xc330_wrist_integration_p01.py`
- Native bridge STEP/STL, integrated reference STEP/GLB and registers: `cad/hr-v0/generated/xc330-wrist-integration-p0.1/`
- Interactive guide: `release/hr-v0/xc330-wrist-integration-p0.1/index.html`

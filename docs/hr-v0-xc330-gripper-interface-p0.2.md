# HR-V0 source-bound XC330 gripper interface P0.2

> **PRELIMINARY INTERFACE CANDIDATE - NOT SELECTED - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: **HR-V0-GRIP-XC330-P0.2**

Round: **R191**

Date: 2026-08-10

## Disposition

R191 supersedes the **interface and tooth assumptions** in the R190 P0.1 feasibility branch. It does not select XC330, update `GRIP-002`, or change the active RM-X52/XM430 electrical, firmware, CAD, BOM or mass baseline.

The correction closes two source-definition deficiencies:

1. the provisional frame is replaced by two exact manufacturer `FPX330-S101` B-Reps registered to exact XC330 body-hole axes; and
2. the trapezoidal feasibility teeth are replaced by a project-owned module 0.8, 20-tooth, 20-degree involute pinion and conjugate straight rack candidate.

It does **not** close received fit, tolerances, material/process, tooth-root definition, fasteners, guarding, force/current/thermal limits, cable/power, mass/COM/inertia, physical tests or qualified review.

## Controlled manufacturer evidence

Four manufacturer files are archived and hash-bound in `cad/vendor/robotis/xc330/source-manifest-p0.1.csv`:

| Record | Embedded date | Size | SHA-256 |
|---|---:|---:|---|
| XL/XC330 official STEP | 2021-03-04 STEP timestamp | 791,238 bytes | `E2F7B060801A1D6A21F23BCA2554F29A402F7D73B8498CB201C9E6ADF3139EB6` |
| XL/XC330 reference drawing | 2020-05-28 | 149,731 bytes | `948B707CB26A64501C03FC45B1A9557B69A554DD5D6934F02E8E6F86CF2B46C2` |
| FPX330-S101 official STEP | 2021-06-09 STEP timestamp | 933,875 bytes | `4FFEE845A49FADF7B91862EBECEE8DEBFE3801E7213F35BEBC3D9007CC25300E` |
| FPX330-S101 reference drawing | 2021-03-19 | 86,902 bytes | `177C5F3EA6803CD1F68DC1342C5BA6F687E3580EEB8C8D90F53B523E1606C357` |

Both drawings are marked **FOR REFERENCE ONLY**. They establish nominal design controls for review, not a released project tolerance or acceptance specification. Received identity and metrology remain mandatory.

The official XC330 source imports as 15 solids. The official S101 source imports as one solid with a 34.0 x 7.0 x 28.600000001 mm aggregate bound and 1,747.950519978 mm3 nominal volume. No material or mass is inferred from that volume.

## Exact nominal registration

The two S101 placements are stored in `transform-register.csv`:

- +X frame: rotate 180 degrees about global `(1,1,0)`, translate `(10.0,-7.5,-8.0)` mm;
- -X frame: rotate +90 degrees about global Z, translate `(-10.0,-7.5,-8.0)` mm.

The transforms register the four represented flange-hole axes on each allocated frame to the XC330 side-tap fields at `x=+/-8 mm`, `y=-22.5/+7.5 mm`. Maximum nominal axis residual is 0.000000 mm. Positive-volume B-Rep intersection is 0.000000000 mm3 for either frame against the actuator, between frames, and between the frames and custom U-base.

This is nominal source-geometry registration only. It does not prove tolerance stack, tap quality, flatness, screw seating, preload, case integrity or received fit.

## Fastener boundaries

The current ROBOTIS product pages identify these package hardware families:

- XC330 package: six `PHS M2x6 TAP` horn screws and ten `PHS M2x8 TAP` frame screws;
- FPX330-S101 set: M2 nuts plus `PHS M2x4`, `PHS M2x4 TAP` and `PHS M2x8 TAP` hardware.

P0.2 represents a nominal 3.0 mm hub stack on the XC330 PCD12 field and frame-ear holes on the S101 PCD16 field. Screw receipt, allocation, head/tool access, engagement, seating, torque, locking, reuse, washer/nut stack and exact ear-fastener length/order code remain held. No missing fastener value is inferred.

## Involute candidate

The project-owned candidate uses:

- module `m = 0.8 mm`;
- `z = 20` teeth;
- pressure angle `20 degrees`;
- pitch radius `r = mz/2 = 8.0 mm`;
- base radius `rb = r cos(20 degrees) = 7.517540966 mm`;
- outside radius `8.8 mm`;
- full-depth candidate root radius `7.0 mm`; and
- `0.150 mm` candidate pair backlash, split across pinion and rack tooth thickness.

The working pinion flanks are generated from the involute equations. The standard full-depth no-undercut screen gives `2/sin^2(20 degrees) = 17.097264` teeth, below the candidate's 20 teeth. This arithmetic is not a tooth-strength, life, accuracy-grade or print-process release. Root fillet, tip relief, compensation, tolerance, orientation, support, material, coupon, wear and jam proof remain `SELECTION REQUIRED`.

## Kinematics and nominal clearances

The three generated positions reproduce:

| Pose | Hard opening | 1 mm pad-envelope opening | Each rack displacement | Pinion travel from closed |
|---|---:|---:|---:|---:|
| Closed | 40 mm | 38 mm | 0 mm | 0 degrees |
| Mid | 58 mm | 56 mm | 9 mm | 64.457752 degrees |
| Open | 76 mm | 74 mm | 18 mm | 128.915504 degrees |

The custom U-base/cover represent 0.30 mm nominal lateral clearance per constrained rack side, 0.50 mm nominal vertical cover clearance and 0.40 mm nominal diametral hub clearance. These values are unvalidated candidates. Print variation, warp, thermal expansion, debris, wear, runout, deflection, external jaw load, end-stop load and jam behavior remain open.

The cover still has two jaw-neck travel slots. Those slots and all rack/pinion/jaw pinch lines require a retained, probe-tested bellows or secondary guard. No hand may enter the mechanism.

## Mass screen

The P0.2 custom solids calculate to 45.366713 g using unselected full-density assumptions of 1.27 g/cm3 for printed parts and 1.15 g/cm3 for pad envelopes.

`692.758 - 82.000 + 23.000 + 45.366713 = 679.124713 g`

Against the retained 750 g moving-group screen, incomplete headroom is 70.875287 g. The calculation excludes both S101 frames, every screw/nut/washer, cable, strain relief, guard/bellows, integration hardware and print/process variation. Therefore it is not mass closure.

## Electrical and software effect

The branch still requires an atomic configuration change if selected: exact 11.1 V source architecture, branch protection, conductor/connector and cable length, voltage drop, inrush/current/duty/thermal evidence, TTL bus/model settings, current-based position behavior, watchdog behavior, HIL and no-restart proof. Manufacturer stall torque is momentary and receives zero continuous-duty or acceptance credit.

No active KiCad, harness, firmware or actuator configuration changes in R191. The active mass ledger intentionally remains XM430.

## Release state

All 16 records in `hold-register.csv` remain `OPEN`. R191 closes zero requirements, zero energization gates and zero Sol R12 blockers. `EG-003`, `EG-005`, `EG-006`, `EG-007`, `EG-014` and `EG-015` remain partial. `EG-028` remains open.

## Artifacts

- Generator: `tools/generate_hr_v0_xc330_gripper_interface_p02.py`
- Independent checker: `tools/check_hr_v0_xc330_gripper_interface_p02.py`
- Manufacturer sources: `cad/vendor/robotis/xc330/`
- Seven custom STEP/STL pairs, three STEP/GLB poses and registers: `cad/hr-v0/generated/xc330-gripper-interface-p0.2/`
- Interactive guide: `release/hr-v0/xc330-gripper-interface-p0.2/index.html`

## Primary manufacturer sources

- ROBOTIS XC330-T288 e-Manual, live page accessed 2026-08-10: https://emanual.robotis.com/docs/en/dxl/x/xc330-t288/
- ROBOTIS US XC330-T288-T, SKU `902-0171-000`, live page accessed 2026-08-10: https://www.robotis.us/dynamixel-xc330-t288-t/
- ROBOTIS US FPX330-S101 4pcs Set, SKU `903-0301-000`, live page accessed 2026-08-10: https://www.robotis.us/fpx330-s101-4pcs-set/
- ROBOTIS official frame download page, FPX330-S101 STEP no. 2021 and PDF no. 2020, accessed 2026-08-10: https://en.robotis.com/service/downloadpage.php?ca_id=7030

Manufacturer catalog, drawing and CAD evidence do not replace received-part inspection, engineering proof, guarding, functional-safety allocation or qualified review.

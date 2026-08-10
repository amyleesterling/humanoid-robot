# HR-V0 lightweight XC330 gripper feasibility P0.1

> **PRELIMINARY FEASIBILITY BRANCH - NOT SELECTED - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

Document ID: **HR-V0-GRIP-XC330-P0.1**

Round: **R190**

Date: 2026-08-10

## Decision

The current RM-X52/XM430 proposal remains the active but unselected gripper path. R190 adds a separate **preferred lightweight feasibility branch** around exact ROBOTIS `XC330-T288-T`, SKU `902-0171-000`. It does not select that branch, update `GRIP-002`, or silently change the active electrical, firmware, CAD, BOM or moving-mass baseline.

This branch answers one narrow question raised by Sol R12: can a source-controlled actuator/mechanism concept cover the retained 40-70 mm object dimension without consuming the entire incomplete moving-mass screen? The arithmetic answer is **plausibly yes**, but the physical evidence answer remains **not yet proven**.

## Exact controlled source

ROBOTIS publishes the XC330-T288-T as a 23 g, 20 x 34 x 26 mm, TTL actuator with 6.5-12.0 V input and 11.1 V recommended input. The official e-Manual publishes 0.92 N m at 11.1 V as momentary stall torque and explicitly warns that stall differs from continuous and real-world output. No Project Button continuous-torque or grip-force rating is inferred from it.

The exact official XL/XC330 STEP download is controlled at `cad/vendor/robotis/xc330/XL-XC-330-official-source.stp`, SHA-256 `E2F7B060801A1D6A21F23BCA2554F29A402F7D73B8498CB201C9E6ADF3139EB6`. The file parses as 15 solids with a 20.0 x 34.0 x 29.000000156 mm aggregate bound. The 29 mm source bound includes projecting output/idler geometry; it is not substituted for the e-Manual's product-body depth.

The generated pinion carries four nominal radial slots derived from the exact source STEP output-wheel geometry. This is a fit-study interface only. Received thread identity, seating, screw head clearance, tolerance, engagement, torque, locking and reuse remain open.

## Independent mechanism concept

R190 generates a symmetric rack-and-pinion mechanism from native CadQuery source:

- module 0.5, 32-tooth pinion;
- 8.0 mm pitch radius;
- two opposed 70 mm racks;
- 40-76 mm nominal hard-jaw opening;
- two 1.0 mm pad envelopes, giving 38-74 mm nominal padded opening; and
- 128.915504 degrees of single-turn actuator travel across the full hard-jaw range.

The padded nominal range contains the retained 40-70 mm object dimension with 2 mm nominal margin at the lower end and 4 mm nominal margin at the upper end. No requirement compliance credit is assigned until the exact material/process, gear backlash, guide clearance, pad stack, deflection, end stops, calibration uncertainty and received usable opening are measured.

The generated base/cover show a central cover but leave two travel-slot access lines. Those lines are recorded as open pinch hazards, not presented as finished guarding. A retained fixed guard or proven bellows/secondary shield is mandatory before motion testing.

## Mass screen

The active moving-mass ledger carries a 692.758 g incomplete known/CAD-estimated subtotal, including 82 g for the XM430 gripper actuator, against a 750 g screen.

The R190 feasibility arithmetic is:

1. `692.758 - 82 + 23 = 633.758 g` after actuator substitution.
2. The generated custom solids calculate as 40.016625 g using explicit full-density assumptions of 1.27 g/cm3 for printed parts and 1.15 g/cm3 for pad envelopes.
3. `633.758 + 40.016625 = 673.774625 g` feasibility subtotal.
4. `750 - 673.774625 = 76.225375 g` incomplete headroom.

This is not mass closure. The 76.225375 g remainder must cover every unresolved allocated frame, screw, nut, cable, connector, strain relief, bumper and integration item. The density values are calculation assumptions, not selected material records or slicer/measured masses. Every received item and the assembled moving group must be weighed and reconciled without omission or double counting.

## Force screen and prohibition on stall-based design

For an ideal symmetric pinion, static equilibrium gives `F = T / (2 r)` for each opposing jaw, with `r = 0.008 m`. That produces 11.5 N per jaw from ROBOTIS US's explicitly estimated 0.184 N m rated-torque disclosure and 57.5 N per jaw from the 0.92 N m momentary stall value.

Both are ideal screens only. They exclude tooth and guide friction, compliance, backlash, current-control behavior, supply drop, temperature and print variation. The stall-derived figure receives zero continuous or acceptance credit and must not be used as a command target. A calibrated load cell must establish the lowest current that retains the selected foam object without unacceptable compression or damage, together with repeatability and thermal limits.

## Electrical and software impact

The XC330-T288-T remains TTL and within the present nominal 12 V actuator-domain concept, but 12.0 V is the manufacturer-published upper input limit, not a margin. Its package connector/cable, current behavior, different geometry and received firmware must be treated as a change. Branch protection, conductor/connector capacity, inrush, voltage drop, thermal behavior, current-limit register behavior, bus watchdog, model identity and supervisor configuration all require a synchronized change and HIL evidence before selection.

No active KiCad, harness, firmware or actuator configuration is changed by R190. The active files intentionally continue to name XM430 so that a feasibility study cannot masquerade as a released configuration.

## Open release holds

Fifteen machine-readable holds remain open in `hold-register.csv`: configuration approval; received actuator/frame registration; output interface; tooth engineering; rack guidance; material/print process; wrist adapter; complete guarding; pads/reference object; force/current; power/cable; power-loss/drop behavior; mass/inertia; physical proof; and qualified review.

R190 closes zero requirements, zero energization gates and zero Sol R12 blockers. It advances source-controlled feasibility only. `EG-003`, `EG-005`, `EG-006`, `EG-007`, `EG-014` and `EG-015` remain partial; `EG-028` remains open.

## Artifacts

- Parametric source: `tools/generate_hr_v0_xc330_gripper_feasibility_p01.py`
- Independent checker: `tools/check_hr_v0_xc330_gripper_feasibility_p01.py`
- Official source and manifest: `cad/vendor/robotis/xc330/`
- Nine custom STEP/STL part pairs, three STEP/GLB poses, calculations, BOM and holds: `cad/hr-v0/generated/xc330-gripper-feasibility-p0.1/`
- Interactive guide: `release/hr-v0/xc330-gripper-feasibility-p0.1/index.html`

## Primary manufacturer evidence

- ROBOTIS XC330-T288-T e-Manual, official live page accessed 2026-08-10; page has no controlled document revision field: https://emanual.robotis.com/docs/en/dxl/x/xc330-t288/
- ROBOTIS US XC330-T288-T product, exact SKU `902-0171-000`, official live page accessed 2026-08-10; page has no controlled document revision field: https://www.robotis.us/dynamixel-xc330-t288-t/
- ROBOTIS official STEP download no. 1987, retrieved 2026-08-10; STEP `FILE_NAME` timestamp is 2021-03-04 and no manufacturer revision field is present: https://www.robotis.com/service/download.php?no=1987
- ROBOTIS US FPX330-S101 4pcs Set, exact SKU `903-0301-000`, official live page accessed 2026-08-10; page has no controlled document revision field: https://www.robotis.us/fpx330-s101-4pcs-set/

Manufacturer catalog and CAD evidence do not replace received-part inspection, engineering proof, guarding, functional-safety allocation or qualified review.

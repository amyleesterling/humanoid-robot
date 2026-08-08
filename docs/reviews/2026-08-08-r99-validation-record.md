# R99 validation record — X430 reaction-torque duty-fixture topology P0.1

> **PRELIMINARY — NOT APPROVED FOR QUOTATION, PROCUREMENT, FABRICATION, ASSEMBLY, POWERED TEST, MOTION, CONNECTION, OR ENERGIZATION.**

Date: 2026-08-08

Configuration: `HR-V0-X430-FIXTURE-P0.1`

## Controlled result

R99 converts the generic R98 fixture need into a dimensioned, reviewable topology without claiming a buildable fixture. It registers exact controlled X430/FR12 geometry, compares four measurement methods, retains stationary reaction torque as the preferred evidence route, and identifies FUTEK TFF400 item `FSH04015` only as a nonselected evaluation candidate.

The package contains a 400 × 600 × 12.7 mm base envelope, a 12.7 × 300 × 300 mm upright envelope, a drawing-derived TFF400 envelope, an upper-bridge active-adapter envelope, exact X430/S102/H101 geometry, a load-arm envelope, STEP/GLB, a readable SVG, a responsive 3D guide, eight geometry controls, four topology dispositions, five non-authorizing load-path screens, twelve open interfaces, six instrument candidate rows, fourteen open holds and a blank fourteen-row inspection form.

No hole size, tolerance, final adapter, material, fastener, anchor, catch, complete guard, controlled load device, cable, calibration, structural proof, physical result or powered authorization exists. `DUTY-HOLD-08` remains open.

## Primary-source boundary

The following current primary records were checked on 2026-08-08 and are registered in the package:

- ROBOTIS XM430-W350 live e-Manual and the controlled R91 X430/FR12 STEP sources;
- FUTEK TFF400 drawing FI1251-F plus the live `FSH04015` product identity;
- FUTEK IAA100 drawing FI1573;
- FUTEK LSB205 drawing FI1452-C;
- LabJack T7 analog-input documentation;
- Joulescope JS220 User Guide revision 1.10, last revised 2025-01-27; and
- OMEGA SA1 instruction sheet M0503/0417.

The model uses only the TFF400 family drawing envelope and interface-axis data. It is not manufacturer CAD. Published sensor capacity and safe overload remain catalog facts, not operating limits or structure allowables. No cable pinout/order code, calibration option, amplifier setting, DAQ configuration or thermal-sensor order code is inferred.

## Automated status

`tools/check_hr_v0_x430_duty_fixture.py` passes. All 48 non-manifest `check_hr_v0_*.py` checkers pass using the controlled CadQuery or KiCad runtime as applicable. Traceability passes with 81 requirements, 40 risks, 109 procedures and 56 release/walking-document references. The energization register remains unresolved: 22 `PARTIAL`, 8 `OPEN`, 0 closed. The regenerated release manifest contains 1,243 package files.

The new checker confirms eight geometry controls, four topology options, five screen equations, twelve open interfaces, six nonselected/selection-required instrument rows, fourteen open holds, three bound ROBOTIS source hashes, a blank fourteen-row physical record and eleven false release flags.

## Visual status

The interactive guide and GLB were rendered over local HTTP in the in-app browser at a desktop viewport. The model loaded, the preliminary banner and authority boundaries were legible, and body/table text remained at least 16 px with metadata at 13 px. Direct SVG rendering found a clipped long warning and right-side heading in the first issue; the generator was corrected to wrap the warning and constrain the SVG to its viewport. The corrected 1600 × 1050 drawing was rerendered and inspected with no clipping. Narrow-mobile behavior is CSS-controlled but was not separately device-emulated in this validation.

## Release boundary

The preferred topology is not selected hardware. `FSH04015`, `FSH04461`, T7, JS220 and LSB205 remain evaluation candidates or selection items. Vendor application confirmation, exact adapters, structural proof, Boston bench anchors, catch, guard, load device, acquisition/uncertainty, reverse-energy controls, as-built inspection and qualified powered-work authorization remain open.

Every fixture-build, fabrication, assembly, powered-test, motion, connection and energization flag remains false. Passing source, geometry, arithmetic, web and repository checks supplies no permission to order, fabricate, assemble, connect, move or energize.

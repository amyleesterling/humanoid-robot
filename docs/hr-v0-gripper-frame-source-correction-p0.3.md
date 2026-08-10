# HR-V0 gripper-frame source correction

Document ID: **HR-V0-GRIP-SRC-P0.3**
Date: 2026-08-08
Parents: `HR-V0-GRIP-CAD-ACQ-P0.1`, `HR-V0-GRIP-ACQ-P0.2`
Requirements: `GRIP-002`, `MECH-005`, `MASS-002`
Verification: `AUDIT-GRIP-002`
Status: **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, MOTION, OR ENERGIZATION**

## Corrected source finding

R108 correctly rejected `FR12-G101GM` as the sole complete HR-V0 gripper mechanism, but its statement that no matching E170/E171 drawing file was acquired is now superseded. The current ROBOTIS XH430-V210 e-Manual states that the FR12-G101GM frame set consists of `FR12-E170` and `FR12-E171` and exposes manufacturer download endpoints for DWG, PDF and STEP files for both parts. All six files are now stored with fixed sizes, SHA-256 hashes, file signatures, source endpoints, document dates and access dates in `cad/vendor/robotis/fr12-g101gm-r109/source-manifest-p0.1.csv`.

The actual binary payloads were checked rather than accepting the download landing pages as evidence. Both PDFs were rendered at 180 dpi and visually inspected. Each is a clear, unclipped, one-page A4 drawing dated 2017-08-31, marked `FOR REFERENCE ONLY`, with units in millimetres and `NONSCALE`. Both material fields are blank and neither sheet shows a general-tolerance block or a drawing revision. The STEP headers name the corresponding parts, carry the same 2017-08-31 date, and identify Pro/ENGINEER 2013410 with `CONFIG_CONTROL_DESIGN` schema.

## Geometry check

CadQuery imported each SHA-controlled STEP as one solid. The computed native-coordinate evidence is:

| Part | Bounding box X x Y x Z (mm) | Volume (mm3) | Native-coordinate center (mm) |
|---|---:|---:|---:|
| FR12-E170 | 37.000000 x 14.000000 x 87.740667 | 5837.452710 | 0.000000, 1.422345, 23.787578 |
| FR12-E171 | 54.000000 x 47.998711 x 94.848224 | 8322.633440 | -0.000255, 12.217384, 38.106643 |

These values prove that the controlled STEP payloads parse as solid reference geometry. They do **not** establish material, mass, tolerance, manufacturing authority, E170-to-E171 mates, actuator/idler interfaces, the complete mechanism, or the six-degree H104-to-carrier transform. The native coordinate systems must not be interpreted as an assembly relation without separate controlled evidence.

## What this closes

- A controlled manufacturer source now exists for the two named FR12-G101GM frame-set geometries.
- The prior `no drawing file acquired` statement is corrected and no longer drives the acquisition plan.
- File identity and parsability can be reproduced from the recorded endpoints and hashes.

## What remains open

- `GRH-001`: complete mechanism definition. The two frame parts do not supply the palms, link rods, flange bushes, crank arm, rail blocks, rail brackets, pads, cable path, full fastener stack or assembly mates.
- `GRH-002`: H104-to-carrier registration. No controlled six-degree transform or tolerance has been established.
- Manufacturer release status. The drawings explicitly say `FOR REFERENCE ONLY`; material, general tolerances and a drawing revision remain absent.
- Installed mass, center of mass, inertia, usable opening, guard/catch, fastener engagement, cable routing, force/current, wear, retention and power-off drop evidence.
- Received-article correlation, qualified mechanical review and every physical test.

`FR12-G101GM` remains **REJECTED AS THE SOLE COMPLETE MECHANISM SOURCE**. `RM-X52` remains a proposed and unreleased parent-kit route. No item was ordered, no supplier was contacted, and no procurement, fabrication, assembly, connection, motion or energization authority is created.

## Primary manufacturer sources

- ROBOTIS, [XH430-V210 e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xh430-v210/), live page with no displayed page revision, accessed 2026-08-08. The accessories section identifies FR12-E170 and FR12-E171 as the FR12-G101GM frame-set parts and exposes downloads 637-642.
- ROBOTIS, FR12-E170 reference drawing, dated 2017-08-31, manufacturer download 638, accessed 2026-08-08.
- ROBOTIS, FR12-E171 reference drawing, dated 2017-08-31, manufacturer download 641, accessed 2026-08-08.

## Release boundary

This correction advances source control only. It closes no energization gate, fabrication gate or complete-gripper hold. HR-V0 remains not ready to fabricate, assemble, connect, move or energize, and Sol R12's missing-buildable-mechanical-definition blocker remains open.

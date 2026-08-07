# HR-V0 Mechanical Interface Correction P0.3

**PRELIMINARY—NO BUILDABLE ARM GEOMETRY—NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-07

Identifier: `HR-V0-MECH-P0.3`

Exact-source evidence: `HR-V0-ROBOTIS-IF-P0.1`

## Result

R53 withdraws the P0.2 arm geometry rather than allowing an unsupported plate arrangement to survive behind a preliminary warning. Exact ROBOTIS STEP files imported with no transforms establish a coherent manufacturer coordinate context for the XM540, FR13-H101K, FR13-S101K, FR13-S102K and FR12-H104K. In that context:

- H101 is a moving hinge/output U-frame around the actuator output and idler;
- S101 is a side/body-frame candidate;
- S102 is a bottom/body-frame candidate displaced from the H101 mounting region; and
- the flat MV0-001 and MV0-003 parts do not define the 3D transforms required to join those interfaces while preserving a proven planar two-axis chain.

The former 44 mm shoulder offset, 160 mm J1–J2 spacing, 160 mm J2–gripper spacing, MV0-001, MV0-002, MV0-003 and S102 application selection are therefore superseded. This correction does not select S101, S102, or a custom frame. It exposes that choice as `SELECTION REQUIRED`.

## R56 current candidate addendum

R57 supersedes R56/P0.3 with `HR-V0-ARM-ARCH-P0.4`. It preserves corrected vendor-to-joint XM540/S102 registration, the ROBOTIS rectangular link pattern, vertical 20-2040 members and 9.525 mm nominal adapter while adding exact OnlineMetals stock and current Accu/MISUMI fastener candidates, a controlled drawing/DXF, ten dimensional controls, physical-evidence templates and ten analytical screens. It does not supersede this P0.3 release hold. The model predicts first nominal adapter/body contact at 122 degrees, so 120 degrees is only a provisional software ceiling. Source reference properties are not allowables; received MTR/fit, qualified analytical acceptance, complete fastener stacks, torque/locking rules, continuous collision proof, cables, hard stop, measured stopping overtravel and uncertainty margin, FAI, physical proof and qualified review remain open; no arm supplier packet is active.

## Controlled evidence

| Artifact | Purpose |
|---|---|
| `cad/vendor/robotis/*.stp` | locally controlled manufacturer geometry with hashes |
| `cad/hr-v0/generated/vendor-interfaces/same-origin-bounds.csv` | reproducible exact-source bounding boxes |
| `cad/hr-v0/generated/vendor-interfaces/XM540-H101-S102-same-origin.step` | exact same-origin 3D evidence for an interactive viewer |
| `cad/hr-v0/generated/vendor-interfaces/XM540-frame-orientation.svg` | readable web diagram of the orientation problem |
| `cad/hr-v0/generated/vendor-interfaces/interface-orientation-summary.json` | source basis, pairwise intersection evidence and disposition |
| `release/hr-v0/fabrication-rfi/WITHDRAWN.md` | supplier-packet withdrawal boundary |
| `tests/forms/hr-v0-robotis-interface-closure-template.csv` | unexecuted replacement-architecture evidence record |

The bounding-box SVG is evidence of source orientation, not a mounting drawing. Only the exact STEP assembly may be used for geometric reconstruction, and it still does not define a project arm.

## Replacement release requirements

Before any new arm part can be quoted or fabricated, `MECH-005` / `AUDIT-MECH-012` require:

1. a deliberate body-frame route: S101, S102, or an exact custom-frame interface;
2. a native CAD assembly derived from the controlled vendor STEP coordinates;
3. explicit homogeneous transforms for actuator body, output frame, link/bracket and gripper interfaces;
4. numerical J1/J2 axis-orientation and parallelism acceptance limits;
5. released J1–J2 and J2–gripper distances derived from that assembly;
6. full-range interference, tool-access and cable-space studies;
7. exact fastener stacks, thread engagement, retention and proof criteria;
8. structural load-path, stress, deflection, fatigue/impact and tolerance analyses;
9. dimensioned drawings and FAI criteria tied to exact source hashes; and
10. signed qualified mechanical disposition.

## Withdrawal and recoverability

The three P0.1 RFI ZIPs were removed from the active tree. Their exact bytes remain recoverable from Git commit `978119f`. The current generator and checker fail closed unless there are zero active ZIPs and all six route records remain withdrawn or held.

The base extrusion, frame-joint and Boston bench-survey work remains candidate evidence only. It is not invalidated by the arm-interface finding, but it still lacks physical fit, torque, proof, anchor and qualified-review evidence. No energization gate closes in P0.3.

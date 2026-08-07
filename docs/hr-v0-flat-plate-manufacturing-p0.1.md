# HR-V0 flat-plate manufacturing control P0.1

Status: **PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Control date: 2026-08-07

RFQ revision: `HR-V0-PLATE-RFQ-P0.1`

## Decision

The four native CAD parts remain an RFQ and first-article package, not a cutting release. The source geometry is unchanged by this process correction.

The current `MV0-001`, `MV0-002`, and `MV0-003` drawings contain 2.70 mm candidate clearance holes in 4.75 mm or 6.35 mm 6061-T6 plate. SendCutSend's current 6061 material page recommends holes no smaller than the material thickness, and its current service article gives 0.170 inch (4.318 mm) as an example minimum hole. Its broader educational sheet-cutting guide and Xometry's laser-cutting guide use a less conservative 50%-of-thickness feature screen. Because the part-specific guidance is more conservative, and because `MV0-003` also fails the 50% screen, **laser-only finished holes are not accepted for these three parts**. Their permitted RFQ routes are one-stop CNC mill/drill or a deliberately hole-free profile blank followed by qualified secondary CNC/drilling. See `HR-V0-FAB-RFQ-P0.1`.

`MV0-004` has 9.00 mm candidate through/slot features in 6.35 mm plate and may be suitable for profile cutting, but its bench slots cannot be released until the actual Boston bench substrate, edge distances, access and anchor system are surveyed.

These are supplier-capability screens, not released project tolerances. Supplier DFM, received-frame coupons, a drawing revision and first-article inspection still govern.

## Controlled process register

| Part | Stock | Critical current feature | RFQ process | Release state |
|---|---|---:|---|---|
| `MV0-001` upper link | 4.75 mm 6061-T6 | 2.70 mm H101/S102 holes | One-stop CNC or profile-only blank plus qualified secondary CNC/drill | Selection required |
| `MV0-002` forearm | 4.75 mm 6061-T6 | 2.70 mm H101/H104 holes | One-stop CNC or profile-only blank plus qualified secondary CNC/drill | Selection required |
| `MV0-003` shoulder adapter | 6.35 mm 6061-T6 | 2.70 mm S102 holes | One-stop CNC or profile-only blank plus qualified secondary CNC/drill | Selection required |
| `MV0-004` bench anchor, qty 2 | 6.35 mm 6061-T6 | 9.00 mm holes/slots | Profile cutting or one-stop CNC after bench survey | Selection required |

The machine-checkable source is [`cad/hr-v0/manufacturing/hr-v0-flat-plate-process-register.csv`](../cad/hr-v0/manufacturing/hr-v0-flat-plate-process-register.csv).

## RFQ package requirements

Each supplier receives one controlled revision containing:

1. part number, revision, millimetre units and quantity;
2. STEP and DXF from the same native generator plus SHA-256 values;
3. the matching SVG/PDF-equivalent drawing with material, nominal thickness and candidate geometry;
4. explicit `NO BEND`, `NO WELD`, `DO NOT SCALE`, deburr and break-sharp-edge instructions;
5. CNC mill/drill requirement for the critical holes on `MV0-001` through `MV0-003`; if a two-process route is quoted, the profile supplier receives only the zero-hole `PROFILE_ONLY_RFQ` artifacts and the secondary shop receives the separately frozen finished drawing;
6. a request for material/temper and actual-thickness evidence;
7. written DFM acceptance of the selected process, hole size/location capability, profile, flatness and inspection method; and
8. one first article per part number before any remaining quantity or assembly use.

The drawing's `±0.127 mm` note records Xometry's published standard CNC metal tolerance as an RFQ basis only. **Quoted capability shall govern.** The final critical-hole diameter, diameter tolerance and position tolerance remain `SELECTION REQUIRED` until received-frame evidence is executed and reviewed.

## Closure sequence

1. Receive and identify the actual ROBOTIS frames and gripper interface hardware.
2. Execute `INSPECT-MECH-003`, `INSPECT-MECH-004`, and `INSPECT-MECH-008` using `MV0-FC01`, `MV0-FC02`, and `MV0-FC03` respectively.
3. Use the recorded fit, fastener access, manufacturer drawings and structural calculation to freeze hole diameter and location tolerances through configuration control.
4. Obtain written supplier DFM acceptance against the same hashes and drawing revision.
5. Issue a separate controlled **first-article candidate** revision; this P0.1 package is not that release.
6. Order only the explicitly authorized first article.
7. Execute `INSPECT-MECH-009` using `tests/forms/hr-v0-flat-plate-dfm-fai-template.csv`, preserving certificates, raw measurements and photographs.
8. Obtain qualified independent mechanical disposition before any fabrication-production, assembly-load, or energization gate can close.

## Primary manufacturer/service evidence

- SendCutSend, *6061 Aluminum*, current page with 0.187 in and 0.250 in 6061-T6 stock, published laser tolerance and the recommendation that holes be no smaller than material thickness; page exposes no revision, accessed 2026-08-07: https://sendcutsend.com/materials/6061-aluminum/
- SendCutSend EDU[CAD], sheet-cutting study guide, file path dated 2025-11 and accessed 2026-08-07; its general minimum-hole/bridge screen is 50% of thickness: https://sendcutsend.com/wp-content/uploads/2025/11/5.2.pdf
- Xometry, *Metal Laser Cutting Service*, current page accessed 2026-08-07; minimum detail is at least 50% of material thickness and standard top-face edge-to-edge tolerance is published as ±0.010 in, with tighter quoting possible: https://www.xometry.com/capabilities/sheet-cutting/metal-laser-cutting/
- Xometry, *CNC Machining Services*, current page accessed 2026-08-07; standard metal tolerance is published as ±0.005 in / ±0.127 mm unless otherwise specified and 6061 is supported: https://www.xometry.com/capabilities/cnc-machining-service/
- Xometry, *Manufacturing Standards*, current page accessed 2026-08-07; sheet thickness is independent of cutting tolerance and flatness is not generally guaranteed for sheet cutting: https://www.xometry.com/manufacturing-standards/
- Protolabs, *Precision Machining Tolerances*, current page accessed 2026-08-07; standard machined-hole tolerance is published as ±0.005 in / ±0.12 mm, with drawing-controlled review for finer requirements: https://www.protolabs.com/services/cnc-machining/precision-machining-tolerances/

Supplier web capabilities are screening evidence only. They do not approve this application, replace a quote/DFM response, establish structural adequacy, or authorize fabrication.

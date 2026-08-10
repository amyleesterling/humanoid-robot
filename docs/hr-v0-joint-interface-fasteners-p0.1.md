# HR-V0 Joint Interface and Fastener Basis P0.1

> **SUPERSEDED BY R53/R69.** This P0.1 interface model uses the withdrawn flat-link topology and must not control a quote, upload, part, fastener stack or assembly. The current candidate is `HR-V0-ARM-ARCH-P0.7` under `HR-V0-MECH-P0.6`; use its C01/C04/C05/C06/C07 controls and the R90 Boston route package.

**PRELIMINARY - NOT RELEASED FOR FABRICATION, PROCUREMENT, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-06  
Mechanical baseline: `HR-V0-MECH-R0.1-PRELIMINARY`  
Native source: `cad/hr-v0/src/hr_v0_cad.py`

## Correction being controlled

The earlier quote geometry used the same eight-hole, 22 mm pitch-circle pattern at both ends of both links. That was not a valid mechanical assumption. The H101 output-horn interface, the S102 actuator-body interface, and the future gripper interface are different interfaces.

The corrected candidate uses:

| Interface | Controlled candidate geometry | Current status |
|---|---|---|
| Shoulder adapter to J1 `FR13-S102K` | Four Ø2.70 clearance holes on the selected 32 x 16 mm rectangular tapped-hole pattern | Physical coupon, bolt stack, torque and tolerance evidence required |
| J1 `FR13-H101K` output to `MV0-001` | Eight Ø2.70 clearance holes on Ø22 PCD | Physical fit and exact output-horn screw stack required |
| `MV0-001` to J2 `FR13-S102K` body frame | Four Ø2.70 clearance holes on the selected 32 x 16 mm rectangular tapped-hole pattern | Physical coupon, bolt stack, torque and tolerance evidence required |
| J2 `FR13-H101K` output to `MV0-002` | Eight Ø2.70 clearance holes on Ø22 PCD | Physical fit and exact output-horn screw stack required |
| `MV0-002` distal end to gripper | No released holes; datum only | `DESIGN REQUIRED` |

The selected S102 rectangle is the four-hole pattern centered on the joint datum at `X = ±16 mm` and `Z = ±8 mm`. The official FR13-S102K drawing calls those holes `4-M2.5x.45 TAP THRU` and dimensions the rectangle 32 x 16 mm. `MV0-FC02` exists solely to verify this interpretation on the received part before any structural plate is cut.

## Primary manufacturer evidence

| Source | Manufacturer date/revision evidence | Controlled fact used |
|---|---|---|
| `cad/vendor/robotis/FR13-H101K.pdf` | Drawing date 2026-01-07; `NONSCALE`; `FOR REFERENCE ONLY` | Frame thickness 2 mm; eight Ø2.5 through holes on Ø22 PCD; multiple tapped/through patterns |
| `cad/vendor/robotis/FR13-S102K.pdf` | Drawing date 2026-01-07; `NONSCALE`; `FOR REFERENCE ONLY` | Frame thickness 2 mm; selected 32 x 16 mm four-hole M2.5 x 0.45 tapped-through pattern |
| `cad/vendor/robotis/XMHD-540.N101.I101.pdf` | Drawing date 2019-03-18; sheet marked non-scale | Output has eight M2.5 x 0.45 taps on Ø22 PCD with 2.5 mm maximum depth; body mounting taps have separately stated maximum depths |
| ROBOTIS X540 frame-assembly e-Manual | Live page checked 2026-08-06; no formal page revision exposed | Hinge frame mounts to output and idler; S102 is a bottom side frame; screw length must not exceed available mounting depth; spacer rings protect the assembly |
| ROBOTIS US `FR13-H101K Set` page | Accessed 2026-08-06; no formal page revision exposed | SKU `903-0270-300` and included fastener inventory |
| ROBOTIS US `FR13-S102K Set` page | Accessed 2026-08-06; no formal page revision exposed | SKU `903-0269-300` and included fastener inventory |

Downloaded drawings and STEP hashes are controlled in `cad/vendor/robotis/vendor-manifest.csv`. Live-page claims must be rechecked at the procurement release.

## Manufacturer kit contents

The exact inventory reported by the current official store is recorded in `bom/hr-v0-frame-kit-contents.csv`. Buying two H101 sets and two S102 sets is expected to supply:

- 2 H101 frames and 2 I101 idler sets;
- 2 S102 frames;
- 16 flat-head wrench bolts `FWB M2.5x17`;
- 32 wrench bolts `WB M2.5x5`;
- 56 wrench bolts `WB M2.5x4`; and
- 40 spacer rings.

Those totals describe expected package contents, not approved usage. The store does not establish the material/strength class, coating, prevailing torque, tightening torque, reuse rule, or exact screw allocation for Project Button. Every received kit and fastener must be identified and counted before use.

## Output-horn stack limit

For the current flat-plate concept, the nominal material stack before thread engagement at an H101/output interface is:

`4.75 mm custom plate + 2.00 mm H101 frame = 6.75 mm nominal`

The actuator drawing limits the output-tap depth to `2.5 mm maximum`. Therefore, before tolerances, washers, head seating, coating, or compression are considered, the absolute geometric upper bound for an under-head screw length is:

`6.75 + 2.50 = 9.25 mm nominal maximum`

This is not a screw selection. A released length must provide a reviewed minimum engagement while never exceeding the actual available depth in the received horn. Standard 8 mm or 10 mm lengths shall not be substituted by convenience: 8 mm may provide insufficient engagement, while 10 mm can exceed the published maximum depth. Counterbores, washers, alternate plate thicknesses, or nonstandard lengths require a controlled redesign and a new proof calculation.

## S102 stack boundary

The selected S102 holes are tapped through the nominal 2 mm frame. The custom adapter/upper-link plate is 4.75 or 6.35 mm thick. The screw must engage the S102 thread without protruding into the actuator, cable, or swept volume. The received assembly clearance, exact head style, thread runout, plate tolerance, spacer use, and accessible tool path are not yet known. Length, material/strength class, torque, locking method and witness marking remain `SELECTION REQUIRED`.

## Release evidence still required

1. Execute `INSPECT-MECH-003` for the PCD22 through-hole patterns and `INSPECT-MECH-004` for the selected S102 tapped rectangle.
2. Execute `INSPECT-MECH-005` on every received frame kit and preserve part/fastener photographs and counts.
3. Measure actual plate/frame/horn stacks and available thread depth with a released method.
4. Select exact screws by manufacturer and order code, including head geometry, material/strength class and coating.
5. Calculate engagement, preload, bearing, pull-out, slip, fatigue and proof loads using released allowables.
6. Release tightening torque, lubrication/threadlocker condition, curing process, reuse rule, witness mark and inspection criteria.
7. Verify tool access, no bottoming, no actuator/cable interference and no loss of joint range on the unpowered first article.
8. Obtain qualified mechanical review before changing any part from quote geometry to a fabrication release.

No value in this document authorizes ordering substitute screws, cutting structural plates, or energizing an actuator.

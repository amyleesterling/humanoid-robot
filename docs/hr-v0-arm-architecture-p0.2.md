# HR-V0 corrected arm architecture P0.2

**PRELIMINARY - CANDIDATE GEOMETRY ONLY - NOT RELEASED FOR QUOTATION, FABRICATION, ASSEMBLY, OR ENERGIZATION**

Date: 2026-08-07

Identifier: `HR-V0-ARM-ARCH-P0.2`

Parent hold: `HR-V0-MECH-P0.3`

## R55 result

P0.2 supersedes the R54/P0.1 candidate. It corrects four material geometry errors without claiming a buildable arm:

1. The XM540 manufacturer STEP output axis is local Z. The proper vendor-to-joint rotation is `[[0,0,-1],[1,0,0],[0,-1,0]]`, mapping output to joint -X. Independently, the actuator bottom mounting axes at local `(x=+/-13.5, y=-41.5)` register exactly to the S102 axes at joint `(y=+/-13.5, z=41.5)`. The display-only axial X placement still requires received horn/idler stack measurement.
2. The link adapter uses the ROBOTIS rectangular frame pattern at `X=+/-16, Z=+/-8`, not the PCD22 horn pattern used by P0.1. ROBOTIS's official OpenMANIPULATOR assembly precedent uses four M2.5 screws and nuts on the analogous H101-to-link interface.
3. The 20-2040 member is vertical: 20 mm across X and 40 mm across Z. Its published core centers become `X=0, Z=+/-10`, giving the M5 pair a 20 mm couple about the X joint axis. P0.1's horizontal member placed the pair on the torque axis.
4. A 0.5 degree sweep found the proximal forearm adapter begins intersecting the J2 body at 122.0 degrees. The candidate therefore carries a provisional 120.0 degree soft limit. Poses 120.5-121.5 are outside that provisional limit even though nominal CAD intersection is zero; 122.0-125.0 collide. A hard stop and measured stopping overtravel are mandatory before any range can be released.

## Candidate datums

| Datum | Candidate value | Status |
|---|---:|---|
| J1 axis | `(0,0,0)`, direction +X | coordinate candidate |
| J1 H101 link face | `Y=32.0000 mm` | exact vendor face; connection open |
| J2 S102 link face | `Y=141.5250 mm` | exact vendor face after package roll |
| J2 axis | `Y=193.0250 mm` | candidate; 193.025 mm from J1 |
| J2 H101 link face, straight reference | `Y=225.0250 mm` | requires -90 degree output offset relative to the rolled body package |
| G1 H104 origin | `Y=312.5500 mm` | candidate; leaves 47.4500 mm to the 360 mm object-center ceiling |

The adapter is a `48 x 40 x 4.7625 mm` 6061-T6 machining candidate with four 2.70 mm frame clearances and two 5.50 mm through holes with nominal 11.20 mm x 90 degree countersinks. Material certificate, finished tolerances, local stress, pull-through, corrosion/finish and first article remain open.

## Fastener and load boundary

`SSK-M5-16-A2` is recorded only as an exact candidate hold for the end taps. Its current primary product data gives M5 x 0.8 full thread, 16 mm overall length, 11.2 mm head diameter, 3.1 mm countersunk length and a 90 degree head. In the nominal 4.7625 mm plate it provides 11.2375 mm modeled engagement into the 22.23 mm tap-depth route.

The nominal static screens are deliberately conservative and do not credit clamp friction:

- 3.9988 N m shoulder screening moment / 20 mm bolt spacing = 199.94 N couple force;
- inferred 6063-T6 internal-thread shear screen = 7,356 N, a 36.8 ratio to the couple force;
- purchased-section strong-axis bending stress = 1.7632 MPa versus the product page's 172.37 MPa yield value; and
- only 1.6625 mm nominal adapter material remains below the M5 countersink.

The first three are static screens, not releases. The fourth remains a blocker: countersink pull-through, local plate bending, preload, fatigue, slip and physical proof are not closed. M2.5 screw/nut order codes, length, grade, torque, locking and wrench envelope remain `SELECTION REQUIRED`.

## Controlled evidence

`cad/hr-v0/generated/arm-architecture-p0.2/` contains the deterministic STEP, interactive GLB, readable SVG, candidate native parts, transform/interface/fastener schedules, 221-row sweep, nominal tool-access screen, joint-load screen and machine-readable summary. `tools/check_hr_v0_arm_architecture.py` fails closed on source hashes, the corrected matrix and patterns, the 120/122 degree boundary, unresolved joint proof and warning text.

Two consecutive 2026-08-07 generator runs produced the same assembly STEP SHA-256: `80BCC6348CC187D9E5259C21603377C7C95DEC28B419EEA8CE0BCB28A53A4025`. This demonstrates source-output reproducibility for that file; it does not validate geometry or physical suitability.

The controlled 80/20 references are in `cad/vendor/8020/`. The official dimension image establishes the 20 x 40 mm envelope, 4.19 mm cores and 20 mm core-center spacing. The official end-view SVG is not treated as structural CAD because its display geometry does not reproduce the published mass/section values. The public eDrawings preview is preserved byte-for-byte without conversion.

## Release blockers

- received XM540/H101/S102 horn, idler and axial-stack fit;
- exact M2.5 stack and nut/tool access;
- M5 torque, anti-galling/locking, countersink tolerances and proof;
- adapter material/process/FAI and accepted local stress/pull-through/fatigue analysis;
- supplier confirmation and received gauge/depth inspection of all end taps;
- continuous between-sample collision proof plus exact cables, connectors, guard, stop and gripper;
- a hard stop and measured fault stopping overtravel below the 122 degree collision pose;
- received mass/COM/inertia, joint-slip, proof, impact and cycle tests; and
- qualified mechanical review and all independent electrical/control/safety release gates.

R55 creates no supplier packet and closes no procurement, fabrication, assembly, energization or functional-safety gate.

# Sol R12 status after R56 strengthened arm candidate

**PRELIMINARY—NOT APPROVED FOR FABRICATION OR ENERGIZATION**

Date: 2026-08-07

Independent review being dispositioned: Sol R12

Project response: R56 / `HR-V0-ARM-ARCH-P0.3`

The Sol summary supplied on 2026-08-07 is the already controlled R12 independent review. It is not a new independent round. R56 is a project-owned correction and is not an approval.

## Material correction

R56 closes the specific R55 thin-adapter geometry defect without promoting the candidate to a fabrication release. The nominal adapter increases from 4.7625 mm to 9.525 mm, with a project finished range of 9.0–10.0 mm. Minimum residual material below the maximum modeled M5 countersink increases from 1.6625 mm to 5.90 mm.

The regenerated exact-coordinate candidate records 202.550 mm J1–J2 spacing, 129.050 mm J2–G1 spacing, 28.400 mm remaining to the 360 mm object-center ceiling, 221 sampled poses, first nominal contact at 122 degrees and a provisional 120 degree J2 ceiling. The combined STEP regenerates byte-identically with SHA-256 `3F177EEB75F0CB1CB20DC0E02F7C2F75D5B935A8AACF1C206CE33284EFEB2F41`.

Westfield `WF2563`, `WF2339` and `WF1254` are exact candidates on hold. Geometry and indicative static screens pass, but received stack/tolerance measurements, torque, locking, anti-galling, reuse and physical proof remain unresolved. Kaiser 6061-T651 typical properties are not design allowables; certified minimum properties and accepted local conical-contact analysis remain mandatory.

## Sol finding disposition

| Sol concern | R56 state | Still required |
|---|---|---|
| No buildable mechanical definition | Improved, still open | certified adapter material, released drawing/tolerances, received frame/fastener stack, torque/locking rules, cables, stops, FAI and proof |
| No closed mass/inertia model | Open | received masses, COM/inertia and full allocation closure |
| Unproven continuous joint torque | Open | current/thermal/duty characterization and qualified drivetrain review |
| Insufficient dynamic restraint/stopping | Candidate still fails closed at provisional 120 degrees before nominal 122-degree contact | hard stop, continuous collision proof, measured stopping overtravel, uncertainty margin and fault tests |
| No executed approved verification | Open | calibrated fixtures, raw records, accountable execution and qualified approval |

R56 closes no procurement, fabrication, assembly, energization or functional-safety gate. HR-V0 remains not build-ready and energization remains prohibited.

# HR-V0 rank-6 3-2-1 joint-stack fixture candidate P0.2

> **PRELIMINARY - NOT APPROVED FOR PROCUREMENT, FABRICATION, ASSEMBLY, CONNECTION, POWERED TESTING, MOTION, OR ENERGIZATION**

## Engineering correction

R253 supersedes `HR-V0-JOINT-STACK-FIXTURE-P0.1` for locating-scheme review. Its six contacts were all normal to one nominal plane. The corresponding frictionless point-contact constraint matrix has rank 3, so the model did not control the two in-plane translations or rotation normal to that plane. P0.1 is prohibited for fixture fabrication or session use.

P0.2 proposes a conventional nominal 3-2-1 scheme on the controlled FR13-S102K geometry:

- datum A: three contacts on the broad external `Y=-51.500 mm` face;
- datum B: two contacts on the external `X=-24.000 mm` side face; and
- datum C: one contact on the external `Z=-16.500 mm` edge face.

With characteristic length `L=48.000 mm`, the normalized six-row matrix `[n, (r × n)/L]` has rank 6, singular values `1.952384, 1.740027, 1.463309, 0.320122, 0.235702, 0.208283`, and condition number `9.373695`. Every 2 mm-radius review envelope is tangent to its intended nominal S102 surface with zero B-rep intersection volume. All remain clear of the imported XM540 and H101 solids; the smallest nominal clearance is `3.751956 mm` at B1/B2.

This is an infinitesimal, frictionless, rigid nominal-CAD result. It does not prove that unilateral contacts stay seated, that an article is stable, or that edge contacts are acceptable. Contact material, seating force, anti-lift restraint, tolerances, local deformation, burr condition, inspection, uncertainty, and physical repeatability remain open.

## Current manufacturer evidence

Current official ROBOTIS sources were rechecked on 2026-08-11:

- the US product page identifies `XM540-W270-T`, TTL and SKU `902-0137-000`, but its package table still names `XM540-W270-R`; purchase remains blocked pending written supplier confirmation;
- the H101 and S102 product pages identify SKUs `903-0270-300` and `903-0269-300` and their kit contents; and
- the X540 e-Manual requires correct mounting length, thrust-washer/index alignment, idler assembly and spacer rings, while warning that stall torque differs from continuous or real-world output.

Those sources do not publish a Project Button tightening torque, received mounting depth, strength class, locking method, or screw reuse rule. No value is inferred.

Primary source pages: [XM540-W270-T product](https://www.robotis.us/dynamixel-xm540-w270-t/), [FR13-H101K](https://www.robotis.us/fr13-h101k-set/), [FR13-S102K](https://www.robotis.us/fr13-s102k-set/), and [X540 e-Manual](https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/).

## Fail-closed physical route

The revised fourteen-step sequence requires received identity and condition, measured mounting depths, a signed temporary hardware instruction, a manufactured and inspected fixture, a no-screw/no-preload contact trial, sequential A/B/C seating, measured restraint force, independent keepout witness, teardown, and re-quarantine. Every row is `NOT EXECUTED`.

Thirteen holds remain open, including written XM540 SKU/protocol confirmation, all fourteen fixture selections, qualified constraint/load/stability review, fixture FAI, received A/B/C fit, edge-contact deformation proof, anti-lift stability, calibrated metrology, separate unpowered-session authorization, and executed acceptance.

## Controlled artifacts

- [Interactive P0.2 guide](../release/hr-v0/joint-stack-fixture-p0.2/index.html)
- [Configuration reconciliation P0.17](../release/hr-v0/configuration-reconciliation-p0.17/index.html)
- [Independent review request](reviews/2026-08-11-r253-independent-review-request.md)
- [Validation record](reviews/2026-08-11-r253-validation-record.md)

P0.2 remains not buildable. R253 closes no Sol blocker and supplies no procurement, fabrication, assembly, test, motion, functional-safety, or energization authority.

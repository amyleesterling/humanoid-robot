# HR-V0 unpowered J1/J2 acquisition and metrology P0.1

Document ID: **HR-V0-JOINT-MET-P0.1**

Date: 2026-08-08

Parents: `HR-V0-MECH-EVAL-P0.1`, `HR-V0-ARM-ARCH-P0.7`, `HR-V0-STOP-REGION-P0.1`

Requirements: `MECH-005`, `MECH-006`, `SAFE-006`, `SAFE-007`, `MASS-002`

Status: **PRELIMINARY - UNPOWERED METROLOGY ONLY - NO PURCHASE, ASSEMBLY-USE, MOTION OR ENERGIZATION RELEASE**

## Result

R83 defined twenty physical inputs but stopped at “receive and measure.” R84 turns that dependency into a controlled technician/laboratory package:

- six exact evaluation articles: two XM540-W270-T actuators, two FR13-H101K sets and two FR13-S102K sets;
- eighteen sequenced operations from work authorization through re-quarantine;
- eight mandatory hold points;
- six instrument classes with provisional screening capability and qualified-review boundaries;
- a direct route for `HSI-001..020`;
- an immutable long-form raw-record schema; and
- a responsive web guide plus readable SVG.

No article has been ordered, received, assembled or measured. All twenty HSI records remain open.

## Important correction: unpowered angle evidence

The R83 register previously combined “encoder zero” with unpowered backlash. An encoder position cannot be acquired while the actuator is unpowered. R84 corrects `HSI-013` and `HSI-014` to require an **external mechanical angle datum**, repeated bidirectional hand-positioned measurements and unpowered backlash evidence. Encoder calibration remains a later, separately authorized powered activity. No encoder value may be inferred from horn marks, nominal CAD or external angle measurements.

## Exact article allocation

`article-allocation.csv` assigns one immutable received configuration to J1 and one to J2. The two H101 allocations explicitly reject HNX540-C101/HN13-C101 substitution because ROBOTIS states that the clamping horn is not compatible with FR13-H101K. J1 and J2 kit hardware must remain separately identified from receipt through teardown.

The six articles are a subset of the existing program-owner-approval-required evaluation batch. This package adds no purchase authority.

## Assembly hard hold

ROBOTIS instructs users to align the thrust washer and horn/shaft index, use an idler for hinge frames, use spacer rings to protect frames, and verify every screw length against mounting-point depth before installation. Its live instructions do not provide a numeric Project Button temporary-assembly torque.

Therefore no threaded temporary stack may be made until a qualified mechanical reviewer signs one exact instruction covering:

1. received screw identity and measured length;
2. drawing-based and received mounting-point depth;
3. spacer-ring placement and accepted resulting gap;
4. exact temporary torque and calibrated tool range;
5. locking-compound prohibition or exact approved use;
6. screw reuse and teardown rules; and
7. stop-work criteria for resistance, bottoming, gap, distortion, wrong indexing, washer damage or missing spacers.

Until that instruction exists, only receiving, inventory, photography, mass measurement and qualified loose-part metrology are allowed. “Finger tight” is not a controlled torque and is not authorized as a workaround.

## Fixture and articulation boundary

The unpowered stack must be supported by a separately reviewed non-damaging fixture. The fixture may not load the actuator case, connector, cable aperture, candidate stop surface or unapproved thread. Gravity motion must be restrained independently of the actuator.

Hand-positioned poses are measurement poses only. The operator must not force a requested angle, drive into a hard point or use the actuator, cable, connector, case, guard or fixture as a design stop. The final pose schedule remains `SELECTION REQUIRED` until the metrology method and restraint are accepted.

## Measurement capability boundary

The instrument register includes project-authored **provisional screening targets**, not released part tolerances or universal acceptance criteria. A qualified mechanical/metrology reviewer must accept the instrument, calibration, method validation and uncertainty budget before execution. Critical attachment faces require contact or CMM-class dimensional evidence; a 3D scan is an envelope screen only.

Every result must preserve the article identity, frozen configuration hash, source commit, datum/method, raw file hash, instrument/calibration state, expanded uncertainty, photographs, witness, nonconformance and qualified disposition. Blank values may not be inferred.

## HSI closure boundary

- `HSI-001..006` and `HSI-013..014` can close only after received execution and qualified acceptance.
- `HSI-007..012` can gain screening or geometry evidence, but final cable/guard/tool envelopes and accepted attachment use/load paths remain external.
- `HSI-015..020` cannot close from a bare joint stack. They still require a configured harness, guard, selected topology, qualified structural/dynamic work, exact bumper and supplier DFM/FAI.

R84 therefore improves executability but closes zero physical inputs, zero energization gates and zero fabrication gates.

## Controlled artifacts

- `test-fixtures/hr-v0/joint-stack-metrology-p0.1/article-allocation.csv`
- `test-fixtures/hr-v0/joint-stack-metrology-p0.1/instrument-capability-register.csv`
- `test-fixtures/hr-v0/joint-stack-metrology-p0.1/hold-point-register.csv`
- `test-fixtures/hr-v0/joint-stack-metrology-p0.1/operation-sequence.csv`
- `test-fixtures/hr-v0/joint-stack-metrology-p0.1/hsi-trace.csv`
- `test-fixtures/hr-v0/joint-stack-metrology-p0.1/source-register.csv`
- `test-fixtures/hr-v0/joint-stack-metrology-p0.1/package-status.json`
- `test-fixtures/hr-v0/joint-stack-metrology-p0.1/HR-V0_joint-stack-metrology.svg`
- `test-fixtures/hr-v0/joint-stack-metrology-p0.1/HR-V0_joint-stack-metrology-guide.html`
- `tests/forms/hr-v0-joint-stack-metrology-template.csv`
- `tools/generate_hr_v0_joint_stack_metrology.py`
- `tools/check_hr_v0_joint_stack_metrology.py`

## Primary manufacturer sources

- [ROBOTIS FR13-H101K Set](https://www.robotis.us/fr13-h101k-set/), SKU `903-0270-300`, live product record rechecked 2026-08-08.
- [ROBOTIS FR13-S102K Set](https://www.robotis.us/fr13-s102k-set/), SKU `903-0269-300`, live product record rechecked 2026-08-08.
- [ROBOTIS DYNAMIXEL X540 assembly instructions](https://emanual.robotis.com/docs/en/dxl/x/xh540-w270/#how-to-assemble), live e-Manual rechecked 2026-08-08.
- [ROBOTIS HNX540-C101 Set](https://www.robotis.us/hnx540-c101-set/), live product record rechecked 2026-08-08; manufacturer incompatibility statement controls the substitution rejection.

## Release boundary

This package is evidence planning, not evidence. It does not authorize purchase, production assembly, actuator connection, cable installation, source connection, encoder readout, torque enable, powered motion, fabrication, operation around children or energization.
